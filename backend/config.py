"""
Configuration and settings
"""

import os
from pydantic import BaseModel

class Settings(BaseModel):
    """Application settings from environment"""
    
    # Backend
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", 8000))
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    
    # HuggingFace
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    
    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    
    # JWT Authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production-use-a-strong-random-key")
    JWT_EXPIRY_HOURS: int = int(os.getenv("JWT_EXPIRY_HOURS", 72))
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    
    class Config:
        case_sensitive = True

settings = Settings()
