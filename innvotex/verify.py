"""Verify HTML file integrity."""
import re

with open("Academic_Resilience_Platform (1).html", "r", encoding="utf-8") as f:
    c = f.read()

checks = {
    "DOCTYPE": "<!DOCTYPE" in c,
    "html_open": "<html" in c,
    "html_close": "</html>" in c,
    "body_open": "<body>" in c,
    "body_close": "</body>" in c,
    "pageRole": 'id="pageRole"' in c,
    "pageLogin": 'id="pageLogin"' in c,
    "pageSignup": 'id="pageSignup"' in c,
    "hidden_css": ".hidden{display:none!important;}" in c,
    "selectRole": "function selectRole" in c,
    "chatbot_removed": "PLAGGUARD CHATBOT" not in c and 'id="pgBot"' not in c,
}

for k, v in checks.items():
    status = "OK" if v else "FAIL"
    print(f"  [{status}] {k}")

opens = len(re.findall(r"<script>", c))
closes = len(re.findall(r"</script>", c))
print(f"  Script tags: {opens} open, {closes} close")

comments_open = len(re.findall(r"<!--", c))
comments_close = len(re.findall(r"-->", c))
print(f"  Comments: {comments_open} open, {comments_close} close, diff={comments_open - comments_close}")

print(f"  File size: {len(c)} bytes, {c.count(chr(10))} lines")
