"""Build a USB-installable zip using only Python's standard library."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
root = Path(__file__).resolve().parents[1]
out = root / "dist" / "kindle-cover-home-0.2.0.zip"
out.parent.mkdir(exist_ok=True)
with ZipFile(out, "w", ZIP_DEFLATED) as z:
    for folder in ("extensions", "tools", "docs", "tests"):
        for path in sorted((root / folder).rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                z.write(path, path.relative_to(root))
    z.write(root / "README.md", "README.md")
print(out)
