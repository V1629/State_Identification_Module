"""
Analysis endpoints - connects frontend requests to core logic
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.orchestrator import EmotionalStateOrchestrator
from core.user_profile import UserProfile

router = APIRouter(tags=["analysis"])

# Initialize orchestrator (can be moved to a singleton service later)
_orchestrator: Optional[EmotionalStateOrchestrator] = None

def get_orchestrator() -> EmotionalStateOrchestrator:
    """Get or initialize the orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = EmotionalStateOrchestrator()
    return _orchestrator


# ==================== Request/Response Models ====================

class AnalyzeRequest(BaseModel):
    """Request body for analyze endpoint"""
    message: str
    user_id: str = "default_user"


class EmotionalState(BaseModel):
    """Emotional state response"""
    state: str
    confidence: float
    category: str  # "short-term", "mid-term", "long-term"


class AnalyzeResponse(BaseModel):
    """Response from analyze endpoint"""
    message: str
    short_term_state: str
    mid_term_state: str
    long_term_state: str
    significance_score: float
    emotions: Dict[str, float]
    timestamp: str


class EMADataPoint(BaseModel):
    """Single EMA score data point"""
    time: str
    shortTerm: float
    midTerm: float
    longTerm: float


class EMAScoresResponse(BaseModel):
    """EMA scores timeline response"""
    data: List[EMADataPoint]


class StatesResponse(BaseModel):
    """Current emotional states response"""
    short_term: str
    mid_term: str
    long_term: str
    short_term_score: float
    mid_term_score: float
    long_term_score: float


# ==================== Endpoints ====================

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_message(request: AnalyzeRequest):
    """
    Analyze a message for emotional state
    
    - Processes message through emotional detector
    - Updates temporal states
    - Calculates significance score
    - Returns all emotional analysis
    """
    try:
        orchestrator = get_orchestrator()
        
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Analyze message (this calls core logic)
        result = orchestrator.analyze_message(
            message=request.message,
            user_id=request.user_id
        )
        
        return AnalyzeResponse(
            message=request.message,
            short_term_state=result.get("short_term_state", "Neutral"),
            mid_term_state=result.get("mid_term_state", "Stable"),
            long_term_state=result.get("long_term_state", "Positive"),
            significance_score=result.get("significance_score", 5.0),
            emotions=result.get("emotions", {}),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/states", response_model=StatesResponse)
async def get_current_states(user_id: str = "default_user"):
    """
    Get current emotional states for a user
    
    Returns:
    - Short-term state (recent messages)
    - Mid-term state (trending)
    - Long-term state (overall)
    """
    try:
        orchestrator = get_orchestrator()
        
        # Get user profile
        user_profile = orchestrator.user_profiles.get(user_id)
        
        if not user_profile:
            # Return defaults if user doesn't exist
            return StatesResponse(
                short_term="Neutral",
                mid_term="Stable",
                long_term="Positive",
                short_term_score=5.0,
                mid_term_score=5.0,
                long_term_score=5.0
            )
        
        return StatesResponse(
            short_term=user_profile.short_term_state,
            mid_term=user_profile.mid_term_state,
            long_term=user_profile.long_term_state,
            short_term_score=user_profile.short_term_ema,
            mid_term_score=user_profile.mid_term_ema,
            long_term_score=user_profile.long_term_ema
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get states: {str(e)}")


@router.get("/ema-scores", response_model=EMAScoresResponse)
async def get_ema_timeline(user_id: str = "default_user", days: int = 1):
    """
    Get EMA score timeline for chart visualization
    
    Generates dummy data for now - connects to real data later
    """
    try:
        # Generate dummy data for frontend chart
        now = datetime.now()
        data_points = []
        
        for i in range(8):
            time = (now - timedelta(hours=3*i)).strftime("%H:%M")
            # Generate realistic EMA scores
            base_short = 6.5
            base_mid = 6.0
            base_long = 5.8
            
            data_points.append(EMADataPoint(
                time=time,
                shortTerm=base_short + (i * 0.1) % 2,
                midTerm=base_mid + (i * 0.05) % 1.5,
                longTerm=base_long + (i * 0.02) % 1.0
            ))
        
        return EMAScoresResponse(data=data_points)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get EMA scores: {str(e)}")


@router.post("/reset")
async def reset_user_state(user_id: str = "default_user"):
    """Reset user state (for testing)"""
    try:
        orchestrator = get_orchestrator()
        orchestrator.user_profiles[user_id] = UserProfile(user_id=user_id)
        
        return {"status": "success", "message": f"User {user_id} state reset"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")
