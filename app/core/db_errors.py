"""
Helpers for translating database integrity errors into HTTP errors.
"""
from typing import Optional, Mapping

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


def _is_unique_violation(error: IntegrityError) -> bool:
    message = str(error.orig).lower()
    return (
        "unique constraint" in message
        or "unique violation" in message
        or "duplicate key value" in message
        or "duplicate entry" in message
    )


def raise_conflict_for_integrity_error(
    error: IntegrityError,
    *,
    detail_map: Optional[Mapping[str, str]] = None,
    default_detail: str = "Unique constraint violation",
) -> None:
    if not _is_unique_violation(error):
        raise error

    detail = default_detail
    if detail_map:
        lowered = str(error.orig).lower()
        for token, message in detail_map.items():
            if token.lower() in lowered:
                detail = message
                break

    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from error
