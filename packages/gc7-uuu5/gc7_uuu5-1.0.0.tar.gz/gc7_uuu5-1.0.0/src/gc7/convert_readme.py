# convert_readme.py
with open("README.md", "r", encoding="cp1252", errors="replace") as f:
    content = f.read()

with open("README2.md", "w", encoding="utf-8") as f:
    f.write(content)
