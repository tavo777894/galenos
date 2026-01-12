import os
import sys
import ctypes
from pathlib import Path

msys2_bin = Path(r"C:\msys64\mingw64\bin")

if not msys2_bin.exists():
    print(f"MSYS2 mingw64 not found at {msys2_bin}")
    sys.exit(1)

try:
    os.add_dll_directory(str(msys2_bin))
except Exception as exc:
    print(f"Failed to add DLL directory: {exc}")
    sys.exit(1)

try:
    ctypes.CDLL("gobject-2.0-0.dll")
    ctypes.CDLL("pango-1.0-0.dll")
    ctypes.CDLL("libcairo-2.dll")
    print("DLL load: OK")
except Exception as exc:
    print(f"DLL load: FAIL ({exc})")
    sys.exit(1)
