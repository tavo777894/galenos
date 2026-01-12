import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

print(f"sys.executable: {sys.executable}")
print(f"sys.prefix: {sys.prefix}")
print(f"sys.base_prefix: {sys.base_prefix}")

try:
    import app  # noqa: F401
    print("import app: OK")
except Exception as exc:
    print(f"import app: FAIL ({exc})")
    sys.exit(1)

for name in ["uvicorn", "fastapi", "weasyprint"]:
    try:
        __import__(name)
        print(f"import {name}: OK")
    except Exception as exc:
        print(f"import {name}: FAIL ({exc})")
        sys.exit(1)

print("verify_venv: SUCCESS")
