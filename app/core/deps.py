"""
Dependencies for FastAPI endpoints.
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.schemas.user import TokenData

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get the current authenticated user from JWT token.

    Args:
        db: Database session
        token: JWT token from request

    Returns:
        User object if authenticated

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    token_data = TokenData(username=username, role=payload.get("role"))

    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active user.

    Args:
        current_user: Current authenticated user

    Returns:
        User object if active

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(required_role: UserRole):
    """
    Dependency factory to require a specific user role.

    Args:
        required_role: The role required to access the endpoint

    Returns:
        Dependency function that checks user role
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {required_role.value} role"
            )
        return current_user
    return role_checker


def require_doctor(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to require doctor role.

    Args:
        current_user: Current authenticated user

    Returns:
        User object if user is a doctor

    Raises:
        HTTPException: If user is not a doctor
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires doctor role"
        )
    return current_user


def require_doctor_or_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to require doctor or admin role.

    Args:
        current_user: Current authenticated user

    Returns:
        User object if user is a doctor or admin

    Raises:
        HTTPException: If user is not a doctor or admin
    """
    if current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires doctor or admin role"
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to require admin role.

    Args:
        current_user: Current authenticated user

    Returns:
        User object if user is an admin

    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires admin role"
        )
    return current_user
