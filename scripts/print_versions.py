import subprocess
import sys
from importlib import metadata
from pathlib import Path

root_dir = Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    import app  # noqa: F401
    print("import app: OK")
except Exception as exc:
    print(f"import app: FAIL ({exc})")
    sys.exit(1)

packages = ["weasyprint", "pydyf", "cffi", "cairocffi", "tinycss2", "cssselect2"]

for name in packages:
    try:
        version = metadata.version(name)
    except metadata.PackageNotFoundError:
        print(f"{name}: not installed")
        continue

    try:
        module = __import__(name)
        location = getattr(module, "__file__", "unknown")
    except Exception as exc:
        location = f"import failed ({exc})"

    print(f"{name}: {version} ({location})")

    if name == "pydyf":
        try:
            parts = []
            for part in version.split("."):
                if part.isdigit():
                    parts.append(int(part))
                else:
                    digits = "".join(ch for ch in part if ch.isdigit())
                    if digits:
                        parts.append(int(digits))
                    break
            while len(parts) < 3:
                parts.append(0)
            if tuple(parts[:2]) < (0, 10):
                print("pydyf warning: version < 0.10 may be incompatible with WeasyPrint.")
        except Exception:
            print("pydyf warning: unable to parse version.")

print("pip check:")
try:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout.strip() or result.stderr.strip() or "(no output)"
    print(output)
except Exception as exc:
    print(f"pip check failed: {exc}")

try:
    import weasyprint  # noqa: F401
    print("WeasyPrint import: OK")
except Exception as exc:
    print(f"WeasyPrint import: FAIL ({exc})")
