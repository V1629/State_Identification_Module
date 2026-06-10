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
    
    # Database (if needed later)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    
    class Config:
        case_sensitive = True

settings = Settings()
