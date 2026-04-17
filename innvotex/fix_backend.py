"""Fix all non-ASCII characters in app.py that crash on Windows console."""
with open("backend/app.py", "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("\u2014", "-")   # em dash
c = c.replace("\u2013", "-")   # en dash
c = c.replace("\u2500", "-")   # box drawing
c = c.replace("\u2501", "-")
c = c.replace("\u2502", "|")
c = c.replace("\u2022", "-")   # bullet
c = c.replace("\u2019", "'")   # right quote
c = c.replace("\u2018", "'")   # left quote
c = c.replace("\u201c", '"')
c = c.replace("\u201d", '"')
c = c.replace("\u2026", "...")  # ellipsis

with open("backend/app.py", "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed all non-ASCII in app.py")
