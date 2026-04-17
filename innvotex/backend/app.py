"""
Academic Plagiarism & AI Content Detector - Flask Backend
Main application with REST API endpoints.
"""

import os
import sys
import time
import json
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.models import (
    init_db, create_user, get_user_by_email, get_all_users,
    create_document, get_document, get_documents_by_user, get_all_documents,
    create_scan_result, get_scan_result, get_scan_result_by_document,
    get_all_scan_results, get_system_stats
)

# --- App Setup -----------------------------
app = Flask(__name__, static_folder=None)
app.secret_key = 'academic-plagiarism-detector-secret-key-2024'
CORS(app, supports_credentials=True)


def sanitize_for_bson(obj):
    """Recursively sanitize data to be BSON-safe for MongoDB.
    Converts oversized ints, numpy types, etc. to safe Python types."""
    if isinstance(obj, dict):
        return {k: sanitize_for_bson(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_bson(v) for v in obj]
    elif isinstance(obj, int):
        # BSON max is 8-byte signed int
        if obj > 2**63 - 1 or obj < -(2**63):
            return float(obj)
        return int(obj)  # also converts numpy int64 to Python int
    elif isinstance(obj, float):
        return float(obj)  # converts numpy float64
    elif isinstance(obj, bool):
        return bool(obj)
    elif isinstance(obj, str):
        return str(obj)
    elif obj is None:
        return None
    else:
        return str(obj)  # fallback: convert unknown types to string

# Frontend directory
FRONTEND_DIR = os.path.dirname(os.path.dirname(__file__))


# --- Serve Frontend ------------------------

@app.route('/')
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, 'Academic_Resilience_Platform (1).html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# --- Auth Endpoints ------------------------

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['full_name', 'email', 'password']
    for field in required:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400

    # Check if user exists
    existing = get_user_by_email(data['email'])
    if existing:
        return jsonify({'error': 'Email already registered'}), 409

    # Hash password
    try:
        import bcrypt
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    except ImportError:
        import hashlib
        password_hash = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()

    user_id = create_user(
        full_name=data['full_name'],
        email=data['email'],
        phone=data.get('phone', ''),
        password_hash=password_hash,
        role=data.get('role', 'student'),
        status=data.get('status', 'pending')  # 'active' from admin, 'pending' from self-signup
    )

    if user_id is None:
        return jsonify({'error': 'Failed to create account'}), 500

    account_status = data.get('status', 'pending')
    msg = 'Account created successfully' if account_status == 'active' else 'Registration submitted. Please wait for admin approval.'
    return jsonify({
        'message': msg,
        'user_id': user_id,
        'status': account_status
    }), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required'}), 400

    user = get_user_by_email(data['email'])
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    # Verify password
    try:
        import bcrypt
        valid = bcrypt.checkpw(data['password'].encode('utf-8'), user['password_hash'].encode('utf-8'))
    except (ImportError, ValueError):
        import hashlib
        valid = user['password_hash'] == hashlib.sha256(data['password'].encode('utf-8')).hexdigest()

    if not valid:
        return jsonify({'error': 'Invalid email or password'}), 401

    # Check account status
    status = user.get('status', 'active')
    role = data.get('role', user['role'])
    if status == 'pending' and role != 'admin':
        return jsonify({'error': 'Your account is pending admin approval. Please wait for an administrator to approve your registration.'}), 403
    if status == 'rejected':
        return jsonify({'error': 'Your account access has been denied. Please contact the administrator.'}), 403

    role = data.get('role', user['role'])

    session['user_id'] = user['id']
    session['role'] = role

    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user['id'],
            'full_name': user['full_name'],
            'email': user['email'],
            'role': role,
            'status': user['status']
        }
    })


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})


# --- Document Scanning ---------------------

@app.route('/api/scan', methods=['POST'])
def scan_document():
    """Upload and scan a document for plagiarism & AI content."""
    start_time = time.time()

    # Get text content
    text = None
    filename = 'pasted_text.txt'
    user_id = session.get('user_id', 'guest')
    subject = ''

    if 'file' in request.files:
        file = request.files['file']
        filename = file.filename or 'uploaded_file'
        subject  = request.form.get('subject', '')
        # Accept user_id from FormData (sent by logged-in student)
        uid_from_form = request.form.get('user_id', '').strip()
        if uid_from_form:
            user_id = uid_from_form

        # Read file content
        if filename.lower().endswith('.txt'):
            text = file.read().decode('utf-8', errors='ignore')
        elif filename.lower().endswith('.pdf'):
            try:
                import PyPDF2
                import io
                file_bytes = file.read()
                reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                text = '\n'.join([page.extract_text() or '' for page in reader.pages])
                if not text.strip():
                    return jsonify({'error': 'Could not extract text from PDF. Try a text-based PDF or paste the text directly.'}), 400
            except ImportError:
                return jsonify({'error': 'PDF support not available. Install PyPDF2: pip install PyPDF2'}), 400
            except Exception as e:
                return jsonify({'error': f'Failed to read PDF: {str(e)}'}), 400
        elif filename.lower().endswith('.docx'):
            try:
                import docx
                import io
                doc = docx.Document(io.BytesIO(file.read()))
                text = '\n'.join([para.text for para in doc.paragraphs])
            except ImportError:
                return jsonify({'error': 'DOCX support not available. Install python-docx: pip install python-docx'}), 400
            except Exception as e:
                return jsonify({'error': f'Failed to read DOCX: {str(e)}'}), 400
        else:
            text = file.read().decode('utf-8', errors='ignore')
    elif request.json and 'text' in request.json:
        text     = request.json['text']
        filename = request.json.get('filename', 'pasted_text.txt')
        subject  = request.json.get('subject', '')
        user_id  = request.json.get('user_id', session.get('user_id', 'guest'))
    elif request.form and 'text' in request.form:
        text     = request.form['text']
        filename = request.form.get('filename', 'pasted_text.txt')
        subject  = request.form.get('subject', '')
        uid_from_form = request.form.get('user_id', '').strip()
        if uid_from_form:
            user_id = uid_from_form

    if not text or len(text.strip()) < 50:
        return jsonify({'error': 'Please provide at least 50 characters of text to analyze'}), 400

    word_count = len(text.split())

    # Save document to MongoDB
    doc_id = create_document(user_id, filename, text, word_count, subject=subject)


    # Run detection
    try:
        from backend.detection.plagiarism_engine import detect_plagiarism
        from backend.detection.ai_detector import detect_ai_content
        from backend.detection.report_generator import generate_report

        print(f"[Scan] Starting analysis of '{filename}' ({word_count} words)...")

        # Run plagiarism detection
        plag_results = detect_plagiarism(text)

        # Run AI content detection
        ai_results = detect_ai_content(text)

        # Generate report
        doc_info = {'filename': filename, 'word_count': word_count}
        report = generate_report(plag_results, ai_results, doc_info)

        total_time = round(time.time() - start_time, 2)
        report['metrics']['total_processing_time'] = total_time

        # Determine risk level
        risk_level = report['summary']['overall_risk_level']

        # Sanitize report for MongoDB BSON compatibility
        safe_report = sanitize_for_bson(report)

        # Save scan result
        scan_id = create_scan_result(
            document_id=doc_id,
            plagiarism_score=float(report['summary']['plagiarism_score']),
            ai_score=float(report['summary']['ai_content_score']),
            risk_level=risk_level,
            report_json=safe_report,
            processing_time=total_time
        )

        print(f"[Scan] Analysis complete in {total_time}s - Plagiarism: {report['summary']['plagiarism_score']}%, AI: {report['summary']['ai_content_score']}%, Risk: {risk_level}")

        return jsonify({
            'success': True,
            'scan_id': scan_id,
            'document_id': doc_id,
            'report': safe_report
        })

    except Exception as e:
        import traceback
        try:
            traceback.print_exc()
        except OSError:
            # Windows console can't handle certain characters
            err_str = traceback.format_exc()
            print(err_str.encode('ascii', errors='replace').decode('ascii'))
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/scan/<scan_id>', methods=['GET'])
def get_scan(scan_id):
    """Get a specific scan result."""
    result = get_scan_result(scan_id)
    if not result:
        return jsonify({'error': 'Scan not found'}), 404
    return jsonify(result)


@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all documents (for faculty/admin)."""
    docs = get_all_documents()
    return jsonify({'documents': docs})


@app.route('/api/documents/user/<user_id>', methods=['GET'])
def list_user_documents(user_id):
    """List documents for a specific user."""
    docs = get_documents_by_user(user_id)
    return jsonify({'documents': docs})


@app.route('/api/documents/<doc_id>/report', methods=['GET'])
def get_document_report(doc_id):
    """Get the full report for a document."""
    result = get_scan_result_by_document(doc_id)
    if not result:
        return jsonify({'error': 'No scan results for this document'}), 404
    return jsonify(result)


# --- Admin/Stats Endpoints -----------------

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics for admin dashboard."""
    stats = get_system_stats()
    return jsonify(stats)


@app.route('/api/scans', methods=['GET'])
def list_scans():
    """List all scan results (admin view)."""
    results = get_all_scan_results()
    return jsonify({'scans': results})


@app.route('/api/users', methods=['GET'])
def list_users():
    """List all users (admin view)."""
    users = get_all_users()
    return jsonify({'users': users})


@app.route('/api/users/role/<role>', methods=['GET'])
def list_users_by_role(role):
    """List users filtered by role (admin view)."""
    from backend.models import get_users_by_role
    users = get_users_by_role(role)
    return jsonify({'users': users, 'role': role, 'count': len(users)})


@app.route('/api/users/pending', methods=['GET'])
def list_pending_users():
    """List users with pending status (awaiting admin approval)."""
    from backend.models import get_users_by_status
    users = get_users_by_status('pending')
    return jsonify({'users': users, 'count': len(users)})


@app.route('/api/users/<user_id>/status', methods=['PATCH'])
def update_user_status_route(user_id):
    """Approve or reject a user by updating their status."""
    data = request.json or {}
    new_status = data.get('status')
    if new_status not in ('active', 'rejected'):
        return jsonify({'error': 'Status must be active or rejected'}), 400
    from backend.models import update_user_status
    ok = update_user_status(user_id, new_status)
    if not ok:
        return jsonify({'error': 'User not found or update failed'}), 404
    return jsonify({'message': f'User status updated to {new_status}', 'user_id': user_id, 'status': new_status})


# --- AI Reference Search -------------------

@app.route('/api/references/search', methods=['POST'])
def search_references():
    """
    Search for real online academic papers relevant to a document.
    Uses Semantic Scholar API (free, no key needed) with CrossRef as fallback.
    Accepts: { text: str, subject: str, keywords: list[str] }
    Returns: { papers: [...], source: str }
    """
    import re
    import urllib.request
    import urllib.parse

    data = request.json or {}
    text = data.get('text', '')
    subject = data.get('subject', '')
    manual_keywords = data.get('keywords', [])

    # -- Extract keywords from document text --
    def extract_keywords(text, n=8):
        """Simple TF-based keyword extractor - no external deps."""
        stopwords = {
            'the','a','an','and','or','but','in','on','at','to','for','of',
            'with','by','from','is','are','was','were','be','been','being',
            'have','has','had','do','does','did','will','would','could','should',
            'may','might','this','that','these','those','it','its','we','our',
            'they','their','he','she','his','her','as','if','so','not','no',
            'can','also','been','more','any','all','some','such','each','which',
            'when','where','how','what','who','use','used','using'
        }
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        freq = {}
        for w in words:
            if w not in stopwords:
                freq[w] = freq.get(w, 0) + 1
        sorted_words = sorted(freq, key=freq.get, reverse=True)
        return sorted_words[:n]

    # Build query terms
    keywords = manual_keywords if manual_keywords else extract_keywords(text)
    subject_map = {
        'maths': 'mathematics', 'physics': 'physics',
        'chemistry': 'chemistry', 'cs': 'computer science',
        'biology': 'biology'
    }
    subject_term = subject_map.get(subject, subject)
    query_terms = keywords[:5]
    if subject_term:
        query_terms = [subject_term] + query_terms[:4]
    query = ' '.join(query_terms)

    papers = []

    # -- Try Semantic Scholar (primary) --
    try:
        ss_query = urllib.parse.quote(query)
        ss_url = (
            f'https://api.semanticscholar.org/graph/v1/paper/search'
            f'?query={ss_query}&limit=6'
            f'&fields=title,authors,year,externalIds,url,abstract,openAccessPdf,publicationTypes'
        )
        req = urllib.request.Request(ss_url, headers={
            'User-Agent': 'PlagGuard-AcademicDetector/1.0',
            'Accept': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=8) as resp:
            import json as _json
            result = _json.loads(resp.read().decode())
            for p in result.get('data', []):
                title = p.get('title', 'Untitled')
                authors = [a.get('name', '') for a in p.get('authors', [])[:3]]
                author_str = ', '.join(authors) if authors else 'Unknown Author'
                year = p.get('year', 'N/A')
                # Get best URL
                url = p.get('url', '')
                pdf = p.get('openAccessPdf', {})
                pdf_url = pdf.get('url', '') if pdf else ''
                ext_ids = p.get('externalIds', {})
                doi = ext_ids.get('DOI', '')
                doi_url = f'https://doi.org/{doi}' if doi else ''
                best_url = pdf_url or doi_url or url or f'https://www.semanticscholar.org/search?q={urllib.parse.quote(title)}'
                abstract = (p.get('abstract') or '')[:200]
                pub_types = p.get('publicationTypes') or []
                pub_type = pub_types[0] if pub_types else 'Paper'
                papers.append({
                    'title': title,
                    'authors': author_str,
                    'year': year,
                    'url': best_url,
                    'abstract': abstract + ('...' if len(p.get('abstract') or '') > 200 else ''),
                    'type': pub_type,
                    'source': 'Semantic Scholar',
                    'has_pdf': bool(pdf_url),
                    'doi': doi
                })
        if papers:
            return jsonify({'papers': papers, 'query': query, 'source': 'Semantic Scholar', 'keyword_used': query_terms})
    except Exception as e:
        print(f'[References] Semantic Scholar failed: {e}')

    # -- Fallback: CrossRef --
    try:
        cr_query = urllib.parse.quote(query)
        cr_url = (
            f'https://api.crossref.org/works?query={cr_query}&rows=6'
            f'&select=title,author,published-print,URL,abstract,type,DOI'
            f'&mailto=plagguard@academic.edu'
        )
        req = urllib.request.Request(cr_url, headers={
            'User-Agent': 'PlagGuard-AcademicDetector/1.0 (mailto:plagguard@academic.edu)'
        })
        with urllib.request.urlopen(req, timeout=8) as resp:
            import json as _json
            result = _json.loads(resp.read().decode())
            for item in result.get('message', {}).get('items', []):
                titles = item.get('title', ['Untitled'])
                title = titles[0] if titles else 'Untitled'
                authors_raw = item.get('author', [])
                authors = [f"{a.get('given','')} {a.get('family','')}".strip() for a in authors_raw[:3]]
                author_str = ', '.join(authors) if authors else 'Unknown Author'
                published = item.get('published-print', {})
                date_parts = published.get('date-parts', [[]])
                year = date_parts[0][0] if date_parts and date_parts[0] else 'N/A'
                url = item.get('URL', '')
                doi = item.get('DOI', '')
                abstract_raw = item.get('abstract', '')
                abstract = re.sub(r'<[^>]+>', '', abstract_raw)[:200]
                papers.append({
                    'title': title,
                    'authors': author_str,
                    'year': year,
                    'url': url or (f'https://doi.org/{doi}' if doi else ''),
                    'abstract': abstract + ('...' if len(abstract_raw) > 200 else ''),
                    'type': item.get('type', 'journal-article').replace('-', ' ').title(),
                    'source': 'CrossRef',
                    'has_pdf': False,
                    'doi': doi
                })
        return jsonify({'papers': papers, 'query': query, 'source': 'CrossRef', 'keyword_used': query_terms})
    except Exception as e:
        print(f'[References] CrossRef also failed: {e}')
        return jsonify({'papers': [], 'query': query, 'source': 'none', 'error': str(e), 'keyword_used': query_terms})


# --- Health Check --------------------------

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check with model status."""
    from backend.detection.plagiarism_engine import _model as plag_model
    from backend.detection.ai_detector import _classifier as ai_model

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'MongoDB',
        'models': {
            'plagiarism_engine': 'loaded' if plag_model and plag_model != 'FAILED' else 'not_loaded',
            'ai_detector': 'loaded' if ai_model and ai_model != 'FAILED' else 'not_loaded'
        },
        'version': '1.1.0'
    })


# --- Seed Demo Data ------------------------

def seed_demo_data():
    """Create demo users for quick testing."""
    import hashlib

    demos = [
        ('Alex Johnson', 'alex@university.edu', '9876543210', 'student'),
        ('Dr. Sarah Smith', 'sarah@university.edu', '9876543211', 'faculty'),
        ('Admin User', 'admin@university.edu', '9876543212', 'admin'),
    ]

    for name, email, phone, role in demos:
        existing = get_user_by_email(email)
        if not existing:
            try:
                import bcrypt
                pw_hash = bcrypt.hashpw(b'password123', bcrypt.gensalt()).decode('utf-8')
            except ImportError:
                pw_hash = hashlib.sha256(b'password123').hexdigest()

            create_user(name, email, phone, pw_hash, role, 'active')
            print(f"[Seed] Created demo user: {email} (role: {role}, password: password123)")


# --- Main ----------------------------------

if __name__ == '__main__':
    print("=" * 60)
    print("  Academic Plagiarism & AI Content Detector")
    print("  Backend Server v1.0")
    print("=" * 60)

    # Initialize database
    init_db()

    # Seed demo data
    seed_demo_data()

    print("\n[Server] Starting Flask server on http://localhost:5000")
    print("[Server] Frontend: http://localhost:5000")
    print("[Server] API Base: http://localhost:5000/api")
    print("[Server] Demo credentials:")
    print("  Student:  alex@university.edu / password123")
    print("  Faculty:  sarah@university.edu / password123")
    print("  Admin:    admin@university.edu / password123")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=True)
