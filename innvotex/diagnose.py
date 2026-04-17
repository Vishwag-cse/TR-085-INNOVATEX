"""Find where subjectNames is defined and check for top-level runtime errors."""
import re

with open("Academic_Resilience_Platform (1).html", "r", encoding="utf-8") as f:
    lines = f.readlines()

script_start = None
for i, line in enumerate(lines):
    if '<script>' in line and 'src=' not in line:
        script_start = i + 1
        break

print(f"Script starts at line {script_start}")

# Find subjectNames
for i, line in enumerate(lines):
    if 'subjectNames' in line and ('const' in line or 'let' in line or 'var' in line):
        print(f"L{i+1}: {line.rstrip()[:120]}")

# Find top-level statements (not inside a function) that access DOM
# These run immediately and will fail if DOM isn't ready
print("\nTop-level DOM accesses (potential errors):")
in_function = 0
for i, line in enumerate(lines[script_start:], script_start+1):
    stripped = line.strip()
    in_function += stripped.count('{') - stripped.count('}')
    if in_function <= 0 and 'document.getElementById' in line and 'function' not in line and 'const' not in line.split('document')[0][-20:]:
        in_function = max(0, in_function)
        print(f"L{i}: {line.rstrip()[:120]}")
