"""
FastAPI application package initialization.

IMPORTANT:
This module configures WeasyPrint DLL loading on Windows.
It must run BEFORE any import that loads WeasyPrint.
"""
import os
import sys
import warnings
from pathlib import Path

def _setup_weasyprint_dlls_windows() -> None:
    if sys.platform != "win32":
        return

    msys2_bin = Path(r"C:\msys64\mingw64\bin")
    if msys2_bin.exists():
        try:
            os.add_dll_directory(str(msys2_bin))
        except Exception as e:
            warnings.warn(f"Failed to add DLL directory {msys2_bin}: {e}", RuntimeWarning)
    else:
        warnings.warn(
            f"MSYS2 mingw64 not found at {msys2_bin}. WeasyPrint PDF generation may fail.",
            RuntimeWarning,
        )

_setup_weasyprint_dlls_windows()
