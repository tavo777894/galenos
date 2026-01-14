"""
Main FastAPI application entry point.
"""
import io
import logging
import os
import tempfile
import time
from contextlib import asynccontextmanager, redirect_stderr

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.limiter import limiter
from app.api.v1.router import api_router

logger = logging.getLogger(__name__)
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
uvicorn_logger = logging.getLogger("uvicorn.error")


def _log_info(message: str, *args) -> None:
    logger.info(message, *args)
    uvicorn_logger.info(message, *args)


def _weasyprint_selftest_enabled() -> bool:
    env_value = os.getenv("WEASYPRINT_SELFTEST")
    if env_value is not None:
        return env_value not in {"0", "false", "False", "no", "NO"}
    return settings.WEASYPRINT_SELFTEST

INSECURE_SECRET_KEYS = {
    "your-super-secret-key-change-this-in-production-min-32-chars",
    "CHANGE-THIS-OR-APP-WILL-NOT-START-minimum-32-characters-required",
    "change-me",
    "secret",
    "password",
    "12345",
}

if settings.SECRET_KEY in INSECURE_SECRET_KEYS:
    raise RuntimeError(
        "Insecure SECRET_KEY detected. Generate one with: "
        "python -c \"import secrets; print(secrets.token_urlsafe(32))\""
    )

if len(settings.SECRET_KEY) < 32:
    raise RuntimeError("SECRET_KEY must be at least 32 characters.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not _weasyprint_selftest_enabled():
        _log_info("WeasyPrint self-test: SKIPPED (WEASYPRINT_SELFTEST=0)")
        yield
        return

    _log_info("Running WeasyPrint self-test...")
    noise = ""
    selftest_failed = False
    pdf_bytes = b""
    tmp = None
    saved_fd = None
    buf = io.StringIO()
    try:
        tmp = tempfile.TemporaryFile(mode="w+b")
        saved_fd = os.dup(2)
        os.dup2(tmp.fileno(), 2)
        with redirect_stderr(buf):
            from weasyprint import HTML
            pdf_bytes = HTML(string="<html><body><h1>Self-Test</h1></body></html>").write_pdf()
    except Exception as exc:
        logger.error("WeasyPrint self-test FAILED: %s", exc)
        selftest_failed = True
        if settings.DEBUG:
            logger.warning("Continuing in DEBUG mode despite WeasyPrint failure")
        else:
            raise RuntimeError(
                f"WeasyPrint initialization failed: {exc}\n"
                "Windows: Ensure MSYS2 mingw64 is installed at C:\\msys64\\mingw64\n"
                "Run: python scripts/test_weasyprint_minimal.py for diagnostics"
            ) from exc
    finally:
        if saved_fd is not None:
            time.sleep(5.0)
            os.dup2(saved_fd, 2)
            os.close(saved_fd)
        native_noise = ""
        if tmp is not None:
            tmp.seek(0)
            native_noise = tmp.read().decode("utf-8", errors="replace").strip()
            tmp.close()
        buf_noise = buf.getvalue().strip()
        noise = "\n".join(filter(None, [buf_noise, native_noise])).strip()

    if noise and settings.DEBUG:
        logger.debug("WeasyPrint/GTK stderr captured during self-test:\n%s", noise)
    if selftest_failed and settings.DEBUG:
        yield
        return
    if not pdf_bytes.startswith(b"%PDF"):
        raise RuntimeError("WeasyPrint generated invalid PDF (wrong header)")
    _log_info("WeasyPrint self-test PASSED (%s bytes)", len(pdf_bytes))
    yield



# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema de Historia Clínica Electrónica - MVP",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def root():
    """
    Root endpoint for health check.

    Returns:
        Application status and version
    """
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "clinic": settings.CLINIC_NAME
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
