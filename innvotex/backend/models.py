"""
Database models for the Academic Plagiarism & AI Content Detector.
Uses MongoDB for document storage.
"""

import os
import json
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient

# --- MongoDB Connection --------------------
# Set your MongoDB URI in environment variable or use default local
MONGO_URI = os.environ.get(
    'MONGO_URI',
    'mongodb://localhost:27017/'
)
DB_NAME = os.environ.get('MONGO_DB_NAME', 'plagguard')

_client = None
_db = None


def get_db():
    """Get MongoDB database connection (lazy singleton)."""
    global _client, _db
    if _db is None:
        print(f"[DB] Connecting to MongoDB: {MONGO_URI[:40]}...")
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        _db = _client[DB_NAME]
        # Test connection
        try:
            _client.server_info()
            print(f"[DB] Connected to MongoDB database: {DB_NAME}")
        except Exception as e:
            print(f"[DB] MongoDB connection failed: {e}")
            print("[DB] Make sure MongoDB is running or set MONGO_URI env variable.")
    return _db


def init_db():
    """Initialize MongoDB collections and indexes."""
    db = get_db()

    # Create indexes for faster queries
    db.users.create_index('email', unique=True)
    db.documents.create_index('user_id')
    db.documents.create_index([('uploaded_at', -1)])
    db.scan_results.create_index('document_id')
    db.scan_results.create_index([('created_at', -1)])

    print("[DB] MongoDB indexes created successfully.")


def _serialize(doc):
    """Convert MongoDB document to JSON-serializable dict."""
    if doc is None:
        return None
    d = dict(doc)
    if '_id' in d:
        d['id'] = str(d['_id'])
        del d['_id']
    # Convert ObjectId fields
    for key in ['user_id', 'document_id', 'scan_result_id']:
        if key in d and isinstance(d[key], ObjectId):
            d[key] = str(d[key])
    # Convert datetime fields
    for key in ['created_at', 'uploaded_at']:
        if key in d and isinstance(d[key], datetime):
            d[key] = d[key].isoformat()
    return d


# --- User helpers --------------------------

def create_user(full_name, email, phone, password_hash, role='student', status='pending'):
    db = get_db()
    try:
        result = db.users.insert_one({
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'password_hash': password_hash,
            'role': role,
            'status': status,
            'created_at': datetime.utcnow()
        })
        return str(result.inserted_id)
    except Exception as e:
        print(f"[DB] Error creating user: {e}")
        return None


def get_user_by_email(email):
    db = get_db()
    user = db.users.find_one({'email': email})
    return _serialize(user)


def get_all_users():
    db = get_db()
    users = db.users.find(
        {},
        {'password_hash': 0}  # Exclude password
    ).sort('created_at', -1)
    return [_serialize(u) for u in users]


def get_users_by_role(role):
    db = get_db()
    users = db.users.find(
        {'role': role},
        {'password_hash': 0}
    ).sort('created_at', -1)
    return [_serialize(u) for u in users]


def get_users_by_status(status):
    """Return all users with a given status (e.g. 'pending', 'active', 'rejected')."""
    db = get_db()
    users = db.users.find(
        {'status': status},
        {'password_hash': 0}
    ).sort('created_at', -1)
    return [_serialize(u) for u in users]


def update_user_status(user_id, new_status):
    """Update a user's status field. Returns True on success, False if not found."""
    db = get_db()
    try:
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'status': new_status, 'updated_at': datetime.utcnow()}}
        )
        return result.matched_count > 0
    except Exception as e:
        print(f"[DB] Error updating user status: {e}")
        return False


# --- Document helpers ----------------------

def create_document(user_id, filename, original_text, word_count, subject=''):
    db = get_db()
    result = db.documents.insert_one({
        'user_id': user_id,
        'filename': filename,
        'original_text': original_text,
        'word_count': word_count,
        'subject': subject,
        'uploaded_at': datetime.utcnow()
    })
    return str(result.inserted_id)


def get_document(doc_id):
    db = get_db()
    doc = db.documents.find_one({'_id': ObjectId(doc_id)})
    return _serialize(doc)


def get_documents_by_user(user_id):
    db = get_db()
    docs = db.documents.find({'user_id': user_id}).sort('uploaded_at', -1)
    results = []
    for doc in docs:
        d = _serialize(doc)
        # Attach latest scan result
        scan = db.scan_results.find_one(
            {'document_id': str(doc['_id'])},
            sort=[('created_at', -1)]
        )
        if scan:
            s = _serialize(scan)
            d['plagiarism_score'] = s.get('plagiarism_score', 0)
            d['ai_score'] = s.get('ai_score', 0)
            d['risk_level'] = s.get('risk_level', 'low')
            d['processing_time'] = s.get('processing_time', 0)
        results.append(d)
    return results


def get_all_documents():
    db = get_db()
    docs = db.documents.find().sort('uploaded_at', -1)
    results = []
    for doc in docs:
        d = _serialize(doc)
        # Safely attach user info (user_id may be 'guest' or invalid ObjectId)
        user = None
        try:
            uid = d.get('user_id')
            if uid and len(str(uid)) == 24:
                user = db.users.find_one({'_id': ObjectId(str(uid))})
        except Exception:
            pass
        if user:
            d['student_name']  = user.get('full_name', 'Unknown')
            d['student_email'] = user.get('email', '')
        else:
            d['student_name']  = d.get('user_id', 'Unknown') if d.get('user_id') else 'Unknown'
            d['student_email'] = ''
        # Attach latest scan result
        scan = db.scan_results.find_one(
            {'document_id': d['id']},
            sort=[('created_at', -1)]
        )
        if scan:
            s = _serialize(scan)
            d['plagiarism_score'] = s.get('plagiarism_score', 0)
            d['ai_score']         = s.get('ai_score', 0)
            d['risk_level']       = s.get('risk_level', 'low')
            d['processing_time']  = s.get('processing_time', 0)
            d['doc_id']           = d.get('id', '')
        else:
            d['plagiarism_score'] = 0
            d['ai_score']         = 0
            d['risk_level']       = 'low'
        results.append(d)
    return results


# --- Scan result helpers -------------------

def create_scan_result(document_id, plagiarism_score, ai_score, risk_level, report_json, processing_time):
    db = get_db()
    result = db.scan_results.insert_one({
        'document_id': str(document_id),
        'plagiarism_score': plagiarism_score,
        'ai_score': ai_score,
        'risk_level': risk_level,
        'report_json': report_json,
        'processing_time': processing_time,
        'created_at': datetime.utcnow()
    })
    return str(result.inserted_id)


def get_scan_result(result_id):
    db = get_db()
    result = db.scan_results.find_one({'_id': ObjectId(result_id)})
    if result:
        r = _serialize(result)
        return r
    return None


def get_scan_result_by_document(document_id):
    db = get_db()
    result = db.scan_results.find_one(
        {'document_id': str(document_id)},
        sort=[('created_at', -1)]
    )
    if result:
        r = _serialize(result)
        # Expose the full nested report for the Analyse tab
        if 'report_json' in r:
            r['report'] = r['report_json']
        return r
    return None


def get_all_scan_results():
    db = get_db()
    results = db.scan_results.find().sort('created_at', -1)
    output = []
    for r in results:
        s = _serialize(r)
        # Safely attach document + user info
        doc = None
        try:
            did = s.get('document_id')
            if did and len(str(did)) == 24:
                doc = db.documents.find_one({'_id': ObjectId(str(did))})
        except Exception:
            pass
        if doc:
            s['filename']   = doc.get('filename', 'unknown')
            s['word_count'] = doc.get('word_count', 0)
            s['subject']    = doc.get('subject', '')
            # Safely get user
            user = None
            try:
                uid = doc.get('user_id')
                if uid and len(str(uid)) == 24:
                    user = db.users.find_one({'_id': ObjectId(str(uid))})
            except Exception:
                pass
            s['student_name'] = user.get('full_name', 'Unknown') if user else 'Unknown'
        else:
            s['filename']     = 'unknown'
            s['student_name'] = 'Unknown'
            s['subject']      = ''
        output.append(s)
    return output


def get_system_stats():
    """Get aggregate system statistics for admin dashboard."""
    db = get_db()
    stats = {}
    stats['total_users'] = db.users.count_documents({})
    stats['total_students'] = db.users.count_documents({'role': 'student'})
    stats['total_faculty'] = db.users.count_documents({'role': 'faculty'})
    stats['total_documents'] = db.documents.count_documents({})
    stats['total_scans'] = db.scan_results.count_documents({})

    # Aggregation for averages
    pipeline = [
        {'$group': {
            '_id': None,
            'avg_plagiarism': {'$avg': '$plagiarism_score'},
            'avg_ai_score': {'$avg': '$ai_score'},
            'avg_processing_time': {'$avg': '$processing_time'}
        }}
    ]
    agg = list(db.scan_results.aggregate(pipeline))
    if agg:
        stats['avg_plagiarism'] = round(agg[0].get('avg_plagiarism', 0) or 0, 1)
        stats['avg_ai_score'] = round(agg[0].get('avg_ai_score', 0) or 0, 1)
        stats['avg_processing_time'] = round(agg[0].get('avg_processing_time', 0) or 0, 2)
    else:
        stats['avg_plagiarism'] = 0
        stats['avg_ai_score'] = 0
        stats['avg_processing_time'] = 0

    stats['flagged_documents'] = db.scan_results.count_documents({
        'risk_level': {'$in': ['high', 'critical']}
    })

    return stats
