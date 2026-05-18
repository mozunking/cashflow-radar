"""JWT Authentication for CAD Service"""
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Security scheme for Swagger UI
bearer_scheme = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    role: str
    exp: datetime | None = None


class AuthenticatedUser(BaseModel):
    """Authenticated user info"""
    user_id: str
    role: str


def verify_jwt(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]) -> AuthenticatedUser:
    """Verify JWT token and return user info.

    In production, this would:
    1. Verify RS256 signature against public key
    2. Check expiration
    3. Validate claims (issuer, audience)
    4. Extract user_id and role from token
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # For now, accept any bearer token and extract basic info
    # In production, implement full JWT RS256 verification
    token = credentials.credentials

    # TODO: Implement full JWT RS256 verification with SM2
    # For production: verify against public key, check exp, validate claims

    # Placeholder: decode token header (not secure - for development only)
    try:
        # This is a mock implementation - replace with real JWT verification
        return AuthenticatedUser(user_id="dev_user", role="admin")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(*allowed_roles: str):
    """Dependency factory for role-based access control.

    Usage:
        @router.post("/")
        async def endpoint(user: Annotated[AuthenticatedUser, Depends(require_role("admin", "operator"))]):
    """
    def role_checker(user: Annotated[AuthenticatedUser, Depends(verify_jwt)]) -> AuthenticatedUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return user
    return role_checker


def optional_auth(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]) -> AuthenticatedUser | None:
    """Optional authentication - returns None if no token provided."""
    if credentials is None:
        return None
    try:
        return verify_jwt(credentials)
    except HTTPException:
        return None
