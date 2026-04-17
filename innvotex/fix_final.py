"""Final unicode cleanup - fix actual unicode characters."""
with open("Academic_Resilience_Platform (1).html", "r", encoding="utf-8") as f:
    c = f.read()

# Fix actual unicode characters
c = c.replace("\u2014", "-")   # em dash
c = c.replace("\u2013", "-")   # en dash
c = c.replace("\u2022", "-")   # bullet
c = c.replace("\u2019", "'")   # right quote
c = c.replace("\u2018", "'")   # left quote
c = c.replace("\u201c", '"')   # left double
c = c.replace("\u201d", '"')   # right double
c = c.replace("\u2026", "...")  # ellipsis
c = c.replace("\u00b7", ".")   # middle dot

# Fix the 'or paste text' divider
c = c.replace("-- - or paste your text below - --", "- or paste your text below -")

with open("Academic_Resilience_Platform (1).html", "w", encoding="utf-8") as f:
    f.write(c)
print("Final unicode cleanup done")
