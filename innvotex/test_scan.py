"""Test the scan API with text input."""
import urllib.request
import json

data = json.dumps({
    "text": "Computer science has evolved into a discipline where artificial intelligence systems are no longer just tools but active participants in problem-solving and decision-making processes. Modern architectures integrate machine learning models that continuously adapt by analyzing vast datasets, optimizing performance through feedback loops and probabilistic reasoning.",
    "filename": "test.txt",
    "subject": "cs"
}).encode()

req = urllib.request.Request(
    "http://localhost:5000/api/scan",
    data=data,
    headers={"Content-Type": "application/json"}
)

try:
    r = urllib.request.urlopen(req, timeout=60)
    d = json.loads(r.read())
    if d.get("success"):
        s = d["report"]["summary"]
        print(f"SUCCESS!")
        print(f"  Plagiarism: {s['plagiarism_score']}%")
        print(f"  AI Score:   {s['ai_content_score']}%")
        print(f"  Risk:       {s['overall_risk_level']}")
    else:
        print("Response:", json.dumps(d, indent=2)[:500])
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    # Try to get JSON error
    try:
        err = json.loads(body)
        print("API Error:", err.get("error", body[:300]))
    except:
        print(f"HTTP {e.code}: {body[:300]}")
except Exception as e:
    print(f"Error: {e}")
