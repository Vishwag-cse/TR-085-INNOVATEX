"""Check if dashboards have the hidden class."""
import re

with open("Academic_Resilience_Platform (1).html", "r", encoding="utf-8") as f:
    c = f.read()

targets = ["dashStudent", "dashFaculty", "dashAdmin", "pageLogin", "pageSignup"]
for d in targets:
    marker = f'id="{d}"'
    idx = c.find(marker)
    if idx == -1:
        print(f"MISSING: {d}")
    else:
        tag_start = c.rfind("<", 0, idx)
        tag_end = c.find(">", idx)
        tag = c[tag_start:tag_end+1]
        has_hidden = "hidden" in tag
        print(f"{'OK' if has_hidden else 'NO HIDDEN!'} {d}: {tag[:120]}")
