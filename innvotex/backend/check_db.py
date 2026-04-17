"""
Quick MongoDB inspection script.
Run: py backend/check_db.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pymongo
from datetime import datetime

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME   = os.environ.get('MONGO_DB_NAME', 'plagguard')

client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

try:
    info = client.server_info()
    print(f"[OK] MongoDB {info['version']} connected at {MONGO_URI}")
except Exception as e:
    print(f"[FAIL] Cannot connect: {e}")
    sys.exit(1)

db = client[DB_NAME]

print(f"\n=== Database: {DB_NAME} ===")
for col in sorted(db.list_collection_names()):
    n = db[col].count_documents({})
    print(f"  {col:<20} {n} document(s)")

print("\n=== Users ===")
users = list(db.users.find({}, {'password_hash': 0}))
if users:
    for u in users:
        print(f"  [{u.get('role','?'):8}]  {u.get('email','?'):35}  {u.get('full_name','?')}")
else:
    print("  (no users found - need to seed demo accounts)")

print("\n=== Documents (latest 5) ===")
docs = list(db.documents.find().sort('uploaded_at', -1).limit(5))
if docs:
    for d in docs:
        print(f"  {str(d['_id'])}  {d.get('filename','?'):25}  user={d.get('user_id','?')}")
else:
    print("  (no documents yet)")

print("\n=== Scan Results (latest 3) ===")
scans = list(db.scan_results.find().sort('created_at', -1).limit(3))
if scans:
    for s in scans:
        print(f"  doc={s.get('document_id','?')}  plag={s.get('plagiarism_score','?')}%  ai={s.get('ai_score','?')}%  risk={s.get('risk_level','?')}")
else:
    print("  (no scans yet)")

client.close()
print("\nDone.")
