"""
Health check endpoints
"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Check if API is running"""
    return {
        "status": "ok",
        "message": "State Identification Module API is running"
    }
