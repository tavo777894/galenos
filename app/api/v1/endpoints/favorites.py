"""
Favorites endpoints for managing user favorite templates and snippets.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.template import Template
from app.models.snippet import Snippet

router = APIRouter()


@router.post("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_template_to_favorites(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a template to user's favorites (idempotent)."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )

    # Check if already favorited
    if template in current_user.favorite_templates:
        return None

    current_user.favorite_templates.append(template)
    db.commit()

    return None


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_template_from_favorites(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a template from user's favorites (idempotent)."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )

    # Check if it's in favorites
    if template not in current_user.favorite_templates:
        return None

    current_user.favorite_templates.remove(template)
    db.commit()

    return None


@router.post("/snippets/{snippet_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_snippet_to_favorites(
    snippet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a snippet to user's favorites (idempotent)."""
    snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snippet with ID {snippet_id} not found"
        )

    # Check if already favorited
    if snippet in current_user.favorite_snippets:
        return None

    current_user.favorite_snippets.append(snippet)
    db.commit()

    return None


@router.delete("/snippets/{snippet_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_snippet_from_favorites(
    snippet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a snippet from user's favorites (idempotent)."""
    snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snippet with ID {snippet_id} not found"
        )

    # Check if it's in favorites
    if snippet not in current_user.favorite_snippets:
        return None

    current_user.favorite_snippets.remove(snippet)
    db.commit()

    return None
