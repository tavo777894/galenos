"""
Main FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.limiter import limiter
from app.api.v1.router import api_router

logger = logging.getLogger(__name__)

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
    logger.info("Running WeasyPrint self-test...")
    try:
        from weasyprint import HTML

        pdf_bytes = HTML(string="<html><body><h1>Self-Test</h1></body></html>").write_pdf()
        if not pdf_bytes.startswith(b"%PDF"):
            raise RuntimeError("WeasyPrint self-test failed: invalid PDF header.")
        logger.info("WeasyPrint self-test PASSED (%s bytes)", len(pdf_bytes))
    except Exception as exc:
        if settings.DEBUG:
            logger.warning("WeasyPrint self-test FAILED: %s", exc)
        else:
            raise RuntimeError(
                "WeasyPrint self-test failed. On Windows, install MSYS2 to "
                "C:\\msys64 and run: python scripts\\test_weasyprint_minimal.py"
            ) from exc
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
