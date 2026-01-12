"""
Template endpoints for SOAP consultation templates with favorites.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.core.deps import get_current_active_user, require_doctor_or_admin
from app.models.user import User
from app.models.template import Template, user_favorite_templates
from app.models.encounter import MedicalSpecialty
from app.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    Template as TemplateSchema,
    TemplateWithFavorite
)

router = APIRouter()


@router.post("/", response_model=TemplateSchema, status_code=status.HTTP_201_CREATED)
def create_template(
    template_in: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    """
    Create a new template.
    Requires DOCTOR or ADMIN role.
    """
    db_template = Template(**template_in.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/", response_model=List[TemplateWithFavorite])
def list_templates(
    specialty: Optional[MedicalSpecialty] = Query(None, description="Filter by medical specialty"),
    only_active: bool = Query(True, description="Show only active templates"),
    only_favorites: bool = Query(False, description="Show only user favorites"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List templates with optional filters.
    Returns templates with favorite status for current user.
    """
    query = db.query(Template)

    # Filter by specialty
    if specialty:
        query = query.filter(Template.specialty == specialty)

    # Filter by active status
    if only_active:
        query = query.filter(Template.is_active == 1)

    # Filter by favorites
    if only_favorites:
        query = query.join(
            user_favorite_templates,
            Template.id == user_favorite_templates.c.template_id
        ).filter(user_favorite_templates.c.user_id == current_user.id)

    # Order by title
    query = query.order_by(Template.title)

    templates = query.offset(skip).limit(limit).all()

    # Get user's favorite template IDs
    favorite_ids = {t.id for t in current_user.favorite_templates}

    # Add is_favorite flag to each template
    templates_with_favorite = []
    for template in templates:
        template_dict = {
            "id": template.id,
            "title": template.title,
            "description": template.description,
            "specialty": template.specialty,
            "default_subjective": template.default_subjective,
            "default_objective": template.default_objective,
            "default_assessment": template.default_assessment,
            "default_plan": template.default_plan,
            "is_active": template.is_active,
            "created_at": template.created_at,
            "updated_at": template.updated_at,
            "is_favorite": template.id in favorite_ids
        }
        templates_with_favorite.append(template_dict)

    return templates_with_favorite


@router.get("/{template_id}", response_model=TemplateWithFavorite)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific template by ID with favorite status."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )

    # Check if it's a favorite
    is_favorite = template in current_user.favorite_templates

    template_dict = {
        "id": template.id,
        "title": template.title,
        "description": template.description,
        "specialty": template.specialty,
        "default_subjective": template.default_subjective,
        "default_objective": template.default_objective,
        "default_assessment": template.default_assessment,
        "default_plan": template.default_plan,
        "is_active": template.is_active,
        "created_at": template.created_at,
        "updated_at": template.updated_at,
        "is_favorite": is_favorite
    }

    return template_dict


@router.put("/{template_id}", response_model=TemplateSchema)
def update_template(
    template_id: int,
    template_in: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    """
    Update a template.
    Requires DOCTOR or ADMIN role.
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )

    # Update only provided fields
    update_data = template_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)

    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    """
    Soft delete a template (set is_active to 0).
    Requires DOCTOR or ADMIN role.
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )

    template.is_active = 0
    db.commit()

    return None
