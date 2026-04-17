"""Fix garbled UTF-8 characters in the HTML file."""
import re

filepath = r"Academic_Resilience_Platform (1).html"
with open(filepath, 'r', encoding='utf-8') as f:
    c = f.read()

# Common garbled UTF-8 sequences and their replacements
replacements = {
    '\u00e2\u0080\u0094': '--',       # em dash —
    '\u00e2\u0080\u0093': '-',        # en dash –
    '\u00e2\u0080\u0099': "'",        # right single quote '
    '\u00e2\u0080\u0098': "'",        # left single quote '
    '\u00e2\u0080\u009c': '"',        # left double quote "
    '\u00e2\u0080\u009d': '"',        # right double quote "
    '\u00e2\u0080\u00a6': '...',      # ellipsis …
    '\u00c2\u00b7': '.',              # middle dot ·
    '\u00e2\u009c\u0093': 'OK',       # check mark ✓
    '\u00e2\u009c\u0085': '[OK]',     # ✅
    '\u00e2\u009d\u008c': '[X]',      # ❌
    '\u00e2\u0086\u0092': '->',       # arrow →
    '\u00e2\u0080\u00a2': '-',        # bullet •
}

for garbled, clean in replacements.items():
    c = c.replace(garbled, clean)

# Fix any remaining non-ASCII in placeholders
c = re.sub(r'placeholder="([^"]*?)[^\x20-\x7e]+([^"]*?)"', r'placeholder="\1\2"', c)

# Fix admin AI model status strings with garbled emoji prefixes
c = re.sub(r"'[^\x20-\x7e]*\s*Loaded'", "'Loaded'", c)
c = re.sub(r"'[^\x20-\x7e]*\s*Not Loaded'", "'Not Loaded'", c)
c = re.sub(r"'[^\x20-\x7e]*\s*Offline'", "'Offline'", c)
c = re.sub(r"'[^\x20-\x7e]*\s*Online'", "'Online'", c)
c = re.sub(r"'[^\x20-\x7e]*\s*Degraded'", "'Degraded'", c)

# Fix "View →" in template strings  
c = re.sub(r'View\s*[^\x20-\x7e]+</span>', 'View</span>', c)

# Fix "— document appears" lines
c = re.sub(r'sources\s*[^\x20-\x7e]+\s*document appears', 'sources - document appears', c)

# Fix "Student — filename" patterns in template literals
c = re.sub(r"\{(x\.student_name \|\| 'Student')\}\s*[^\x20-\x7e$]+\s*\{x\.filename\}", r'{\1} - {x.filename}', c)

# Fix CrossRef line
c = re.sub(r'CrossRef[^\x20-\x7e]+</div>', 'CrossRef...</div>', c)

# Fix high-risk paragraph count
c = re.sub(r'high-risk\s*[^\x20-\x7e]+</div>', 'high-risk</div>', c)

# Fix "Submitted ✓" badge
c = re.sub(r'Submitted\s*[^\x20-\x7e]+</span>', 'Submitted</span>', c)

# Fix stuOrig textContent line
c = re.sub(r"textContent = '[^\x20-\x7e]+';", "textContent = '--';", c)

# Fix comment decorations (╔═══, ━━━ etc) - leave as plain dashes
c = re.sub(r'// [^\x20-\x7e]{3,}', '// ──────────────────', c)
c = re.sub(r'<!-- [^\x20-\x7e]{3,}', '<!-- ──────────────────', c)
c = re.sub(r'[^\x20-\x7e]{3,} -->', '────────────────── -->', c)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"Done! Cleaned {filepath}")
