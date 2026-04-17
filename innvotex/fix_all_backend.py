"""Strip ALL non-ASCII from backend .py files, replacing with ASCII equivalents."""
import os

replacements = {
    "\u2014": "-",    # em dash
    "\u2013": "-",    # en dash
    "\u2192": "->",   # right arrow
    "\u2190": "<-",   # left arrow
    "\u2500": "-",    # box drawing
    "\u2501": "-",
    "\u2502": "|",
    "\u2022": "-",    # bullet
    "\u2019": "'",    # right quote
    "\u2018": "'",    # left quote
    "\u201c": '"',    # left double
    "\u201d": '"',    # right double
    "\u2026": "...",  # ellipsis
    "\u00b7": ".",    # middle dot
    "\u2713": "[OK]", # check mark
    "\u2717": "[X]",  # cross mark
    "\u00a0": " ",    # non-breaking space
}

for root, dirs, files in os.walk("backend"):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read()
            
            changed = False
            for old, new in replacements.items():
                if old in content:
                    content = content.replace(old, new)
                    changed = True
            
            # Also strip any remaining non-ASCII that we missed
            clean = []
            for ch in content:
                if ord(ch) > 127:
                    clean.append("?")  # replace unknown non-ASCII with ?
                    changed = True
                else:
                    clean.append(ch)
            
            if changed:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write("".join(clean))
                print(f"Fixed: {path}")

print("Done - all backend .py files are now pure ASCII")
