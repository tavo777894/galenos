"""
Global search endpoint for Command Palette.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.patient import Patient
from pydantic import BaseModel

router = APIRouter()


class PatientSearchResult(BaseModel):
    """Patient search result schema."""
    id: int
    full_name: str
    ci: str
    phone: Optional[str] = None


class ActionSearchResult(BaseModel):
    """Action search result schema."""
    id: str
    title: str
    route: str


class GlobalSearchResponse(BaseModel):
    """Global search response schema."""
    patients: List[PatientSearchResult]
    actions: List[ActionSearchResult]


@router.get("/", response_model=GlobalSearchResponse)
def global_search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results per category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Global search endpoint for Command Palette.

    Searches across:
    - Patients (by name, CI)
    - Quick actions (contextual based on search term)

    Args:
        q: Search query
        limit: Maximum results per category
        db: Database session
        current_user: Current authenticated user

    Returns:
        Search results with patients and actions
    """
    search_term = f"%{q.lower()}%"
    patients_results = []
    actions_results = []

    # Search patients
    patients = db.query(Patient).filter(
        (Patient.first_name.ilike(search_term)) |
        (Patient.last_name.ilike(search_term)) |
        (Patient.ci.like(f"%{q}%"))
    ).limit(limit).all()

    for patient in patients:
        patients_results.append(PatientSearchResult(
            id=patient.id,
            full_name=patient.full_name,
            ci=patient.ci,
            phone=patient.phone
        ))

    # Contextual actions based on search
    search_lower = q.lower()

    if "nuevo" in search_lower or "paciente" in search_lower or "crear" in search_lower:
        actions_results.append(ActionSearchResult(
            id="new-patient",
            title="Nuevo Paciente",
            route="/patients/new"
        ))

    if "paciente" in search_lower or "lista" in search_lower or "ver" in search_lower:
        actions_results.append(ActionSearchResult(
            id="list-patients",
            title="Ver Lista de Pacientes",
            route="/patients"
        ))

    if "documento" in search_lower or "pdf" in search_lower:
        actions_results.append(ActionSearchResult(
            id="list-documents",
            title="Ver Documentos",
            route="/documents"
        ))

    if "consulta" in search_lower or "cita" in search_lower:
        actions_results.append(ActionSearchResult(
            id="new-consultation",
            title="Nueva Consulta (Próximamente)",
            route="/consultations/new"
        ))

    return GlobalSearchResponse(
        patients=patients_results,
        actions=actions_results
    )
