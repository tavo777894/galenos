import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    import app  # noqa: F401
except Exception as exc:
    print(f"import app: FAIL ({exc})")
    sys.exit(1)

from weasyprint import HTML

out_dir = Path(r"D:\galenos\out")
out_dir.mkdir(parents=True, exist_ok=True)

out_path = out_dir / "weasy_minimal.pdf"
if out_path.exists():
    out_path.unlink()

try:
    html = HTML(string="<html><body><h1>WeasyPrint OK</h1></body></html>")
    html.write_pdf(str(out_path))
    pdf_bytes = out_path.read_bytes()
    if not pdf_bytes.startswith(b"%PDF"):
        print("PDF header validation failed.")
        out_path.unlink(missing_ok=True)
        sys.exit(1)
except Exception as exc:
    print(f"weasyprint minimal: FAIL ({exc})")
    out_path.unlink(missing_ok=True)
    sys.exit(1)

print(f"PDF size: {len(pdf_bytes)} bytes")
print(f"PDF head: {pdf_bytes[:16]}")
print("test_weasyprint_minimal: SUCCESS")
