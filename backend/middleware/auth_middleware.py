"""
Authentication Middleware
JWT verification for protected endpoints.

Security: The user_id is always extracted from the verified JWT token,
never from request parameters. This ensures users can only access
their own data regardless of what API parameters they pass.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from ..config import settings

# HTTPBearer extracts the token from "Authorization: Bearer <token>" header
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    FastAPI dependency: extracts and verifies JWT token.

    Returns the user_id (MongoDB ObjectId as string) from the token.
    Rejects expired or tampered tokens with 401.

    Usage:
        @router.get("/protected")
        async def protected_route(user_id: str = Depends(get_current_user)):
            # user_id is guaranteed to be the authenticated user
            ...
    """
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
        )
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        return user_id

    except JWTError:
        raise credentials_exception
