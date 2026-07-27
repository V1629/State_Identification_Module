"""
Authentication Routes
Google OAuth login/signup endpoint.

Flow:
  1. Frontend gets Google ID token via Google Sign-In button
  2. Frontend sends token to POST /api/auth/google
  3. Backend verifies token with Google
  4. Backend creates/finds user in MongoDB
  5. Backend returns JWT for subsequent API calls
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from passlib.context import CryptContext

from ..config import settings
from ..database import (
    create_user,
    get_user_by_google_id,
    get_user_by_email,
    get_user_by_id,
    update_last_login,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from ..middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


# ==================== Request/Response Models ====================


class GoogleAuthRequest(BaseModel):
    """Google OAuth credential from frontend"""
    credential: str  # Google ID token from Google Sign-In
    is_signup: bool = False


class RegisterRequest(BaseModel):
    """Email/Password registration"""
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    """Email/Password login"""
    email: str
    password: str


class AuthResponse(BaseModel):
    """Authentication response with JWT and user info"""
    token: str
    user: dict


# ==================== Helper Functions ====================


def create_access_token(user_id: str) -> str:
    """
    Create JWT access token.

    The 'sub' claim contains the MongoDB user _id,
    which is used by get_current_user() to identify the user.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        hours=settings.JWT_EXPIRY_HOURS
    )
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


# ==================== Endpoints ====================


@router.post("/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest):
    """
    Authenticate with Google OAuth.

    - Verifies the Google ID token
    - Creates a new user if they don't exist
    - Returns JWT token for subsequent authenticated requests

    The JWT token should be sent in the Authorization header:
        Authorization: Bearer <token>
    """
    try:
        # Verify Google ID token
        id_info = id_token.verify_oauth2_token(
            request.credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        google_id = id_info["sub"]
        email = id_info.get("email", "")
        name = id_info.get("name", "")
        picture = id_info.get("picture", "")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google",
            )

        # Check if user exists by email
        user = await get_user_by_email(email)

        if request.is_signup:
            if user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists. Please sign in instead.",
                )
            # New user — create account
            user = await create_user(
                google_id=google_id,
                email=email,
                name=name,
                picture=picture,
            )
        else:
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account not found. Please sign up first.",
                )
            # Existing user — update last login
            await update_last_login(str(user["_id"]))

        # Create JWT
        token = create_access_token(str(user["_id"]))

        return AuthResponse(
            token=token,
            user={
                "id": str(user["_id"]),
                "email": email,
                "name": name,
                "picture": picture,
            },
        )

    except ValueError as e:
        # Google token verification failed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}",
        )


@router.post("/register", response_model=AuthResponse)
async def register_user(request: RegisterRequest):
    """Register a new user with Email and Password."""
    user = await get_user_by_email(request.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please sign in instead.",
        )
    
    hashed_password = pwd_context.hash(request.password)
    user = await create_user(
        email=request.email,
        name=request.name,
        password_hash=hashed_password
    )
    
    token = create_access_token(str(user["_id"]))
    return AuthResponse(
        token=token,
        user={
            "id": str(user["_id"]),
            "email": request.email,
            "name": request.name,
            "picture": "",
        },
    )


@router.post("/login", response_model=AuthResponse)
async def login_user(request: LoginRequest):
    """Login with Email and Password."""
    user = await get_user_by_email(request.email)
    
    if not user or not user.get("password_hash"):
        # If user exists but no password_hash, they probably signed up via Google
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
        
    if not pwd_context.verify(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
        
    await update_last_login(str(user["_id"]))
    token = create_access_token(str(user["_id"]))
    
    return AuthResponse(
        token=token,
        user={
            "id": str(user["_id"]),
            "email": user.get("email", ""),
            "name": user.get("name", ""),
            "picture": user.get("picture", ""),
        },
    )


@router.get("/me")
async def get_current_user_info(
    user_id: str = Depends(get_current_user),
):
    """
    Get current authenticated user's info.
    Requires valid JWT in Authorization header.
    """
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {
        "id": str(user["_id"]),
        "email": user.get("email", ""),
        "name": user.get("name", ""),
        "picture": user.get("picture", ""),
    }
