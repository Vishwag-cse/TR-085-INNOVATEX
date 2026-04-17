"""Get the traceback from the Werkzeug debugger."""
import urllib.request
import json
import re
import html as htmlmod

data = json.dumps({
    "text": "Computer science has evolved into a discipline where artificial intelligence systems are no longer just tools but active participants in problem-solving. Modern architectures integrate machine learning models.",
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
    print("Success:", r.read().decode()[:300])
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", "replace")
    
    # Extract traceback from Werkzeug debugger HTML
    # Look for the traceback text in <pre> or <code> blocks
    matches = re.findall(r'class="traceline".*?<pre>(.*?)</pre>', body, re.DOTALL)
    if matches:
        for m in matches[-5:]:
            print(htmlmod.unescape(m.strip()))
            print()
    else:
        # Try plain pre blocks
        matches = re.findall(r'<pre>(.*?)</pre>', body, re.DOTALL)
        if matches:
            for m in matches:
                clean = htmlmod.unescape(m.strip())
                if "File" in clean or "Error" in clean or "Traceback" in clean:
                    print(clean[:300])
                    print("---")
        else:
            # Just print all text
            clean = re.sub(r'<[^>]+>', '\n', body)
            clean = htmlmod.unescape(clean)
            lines = [l.strip() for l in clean.split('\n') if l.strip()]
            for l in lines:
                if 'File' in l or 'Error' in l or 'line' in l or 'OSError' in l:
                    print(l)
