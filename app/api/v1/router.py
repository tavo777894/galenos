"""
Main API router that aggregates all endpoint routers.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, patients, documents, search, encounters, templates, snippets, favorites, attachments

api_router = APIRouter()

# Include authentication routes
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Include patient routes
api_router.include_router(
    patients.router,
    prefix="/patients",
    tags=["Patients"]
)

# Include document routes
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"]
)

# Include search routes
api_router.include_router(
    search.router,
    prefix="/search",
    tags=["Search"]
)

# Include encounter routes (Sprint 3)
api_router.include_router(
    encounters.router,
    prefix="/encounters",
    tags=["Encounters"]
)

# Include template routes (Sprint 3)
api_router.include_router(
    templates.router,
    prefix="/templates",
    tags=["Templates"]
)

# Include snippet routes (Sprint 3)
api_router.include_router(
    snippets.router,
    prefix="/snippets",
    tags=["Snippets"]
)

# Include favorites routes (Sprint 3)
api_router.include_router(
    favorites.router,
    prefix="/favorites",
    tags=["Favorites"]
)

# Include attachments routes (Sprint 3)
api_router.include_router(
    attachments.router,
    prefix="/attachments",
    tags=["Attachments"]
)
