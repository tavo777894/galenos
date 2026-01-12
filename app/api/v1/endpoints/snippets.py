"""
Snippet endpoints for reusable text fragments with favorites.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_active_user, require_doctor_or_admin
from app.models.user import User
from app.models.snippet import Snippet, SnippetCategory, user_favorite_snippets
from app.schemas.snippet import (
    SnippetCreate,
    SnippetUpdate,
    Snippet as SnippetSchema,
    SnippetWithFavorite
)

router = APIRouter()


@router.post("/", response_model=SnippetSchema, status_code=status.HTTP_201_CREATED)
def create_snippet(
    snippet_in: SnippetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    """
    Create a new snippet.
    Requires DOCTOR or ADMIN role.
    """
    db_snippet = Snippet(**snippet_in.model_dump())
    db.add(db_snippet)
    db.commit()
    db.refresh(db_snippet)
    return db_snippet


@router.get("/", response_model=List[SnippetWithFavorite])
def list_snippets(
    category: Optional[str] = Query(None, description="Filter by category"),
    only_active: bool = Query(True, description="Show only active snippets"),
    only_favorites: bool = Query(False, description="Show only user favorites"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List snippets with optional filters.
    Returns snippets with favorite status for current user.
    """
    query = db.query(Snippet)

    # Filter by category
    if category:
        query = query.filter(Snippet.category == category)

    # Filter by active status
    if only_active:
        query = query.filter(Snippet.is_active == 1)

    # Filter by favorites
    if only_favorites:
        query = query.join(
            user_favorite_snippets,
            Snippet.id == user_favorite_snippets.c.snippet_id
        ).filter(user_favorite_snippets.c.user_id == current_user.id)

    # Order by usage count (most used first), then by title
    query = query.order_by(Snippet.usage_count.desc(), Snippet.title)

    snippets = query.offset(skip).limit(limit).all()

    # Get user's favorite snippet IDs
    favorite_ids = {s.id for s in current_user.favorite_snippets}

    # Add is_favorite flag to each snippet
    snippets_with_favorite = []
    for snippet in snippets:
        snippet_dict = {
            "id": snippet.id,
            "title": snippet.title,
            "category": snippet.category,
            "content": snippet.content,
            "is_active": snippet.is_active,
            "usage_count": snippet.usage_count,
            "created_at": snippet.created_at,
            "updated_at": snippet.updated_at,
            "is_favorite": snippet.id in favorite_ids
        }
        snippets_with_favorite.append(snippet_dict)

    return snippets_with_favorite


@router.get("/{snippet_id}", response_model=SnippetWithFavorite)
def get_snippet(
    snippet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific snippet by ID with favorite status."""
    snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snippet with ID {snippet_id} not found"
        )

    # Increment usage count
    snippet.usage_count += 1
    db.commit()

    # Check if it's a favorite
    is_favorite = snippet in current_user.favorite_snippets

    snippet_dict = {
        "id": snippet.id,
        "title": snippet.title,
        "category": snippet.category,
        "content": snippet.content,
        "is_active": snippet.is_active,
        "usage_count": snippet.usage_count,
        "created_at": snippet.created_at,
        "updated_at": snippet.updated_at,
        "is_favorite": is_favorite
    }

    return snippet_dict


@router.put("/{snippet_id}", response_model=SnippetSchema)
def update_snippet(
    snippet_id: int,
    snippet_in: SnippetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    """
    Update a snippet.
    Requires DOCTOR or ADMIN role.
    """
    snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snippet with ID {snippet_id} not found"
        )

    # Update only provided fields
    update_data = snippet_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(snippet, field, value)

    db.commit()
    db.refresh(snippet)

    return snippet


@router.delete("/{snippet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snippet(
    snippet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    """
    Soft delete a snippet (set is_active to 0).
    Requires DOCTOR or ADMIN role.
    """
    snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snippet with ID {snippet_id} not found"
        )

    snippet.is_active = 0
    db.commit()

    return None
