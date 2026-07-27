"""
Analysis endpoints — connects frontend requests to core logic.

All endpoints require JWT authentication via the Authorization header.
The user_id is ALWAYS extracted from the verified JWT token, never from
request parameters, ensuring users can only access their own data.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.orchestrator import EmotionalStateOrchestrator
from core.user_profile import UserProfile

from ..middleware.auth_middleware import get_current_user
from ..database import save_user_state, load_user_state, delete_user_state

router = APIRouter(tags=["analysis"])

# Initialize orchestrator (singleton)
_orchestrator: Optional[EmotionalStateOrchestrator] = None


def get_orchestrator() -> EmotionalStateOrchestrator:
    """Get or initialize the orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = EmotionalStateOrchestrator()
    return _orchestrator


# ==================== Request/Response Models ====================


class AnalyzeRequest(BaseModel):
    """Request body for analyze endpoint.
    user_id is NOT accepted here — it comes from the JWT token."""
    message: str


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
    short_term_state: Optional[Dict[str, float]] = None
    mid_term_state: Optional[Dict[str, float]] = None
    long_term_state: Optional[Dict[str, float]] = None
    message_count: int = 0


# ==================== Helpers ====================


def state_to_label(state) -> str:
    """Convert state distribution dict to single label string."""
    if isinstance(state, dict) and state:
        return max(state.items(), key=lambda x: x[1])[0]
    if isinstance(state, str):
        return state
    return "Neutral"


def get_top_score(state) -> float:
    """Get the highest score from a state dict, scaled to 0-10."""
    if isinstance(state, dict) and state:
        return round(max(state.values()) * 10, 2)
    return 5.0


async def load_profile_from_db(user_id: str) -> UserProfile:
    """
    Load user profile from MongoDB, applying decay for time elapsed.
    Creates a new profile if none exists.

    Args:
        user_id: Authenticated user's MongoDB ObjectId as string

    Returns:
        UserProfile instance ready for processing
    """
    state_data = await load_user_state(user_id)

    if state_data:
        profile = UserProfile.from_db_dict(user_id, state_data)

        # Apply time-based decay since last session
        last_updated = state_data.get("last_updated")
        if last_updated:
            if isinstance(last_updated, datetime):
                elapsed_hours = (
                    datetime.utcnow() - last_updated
                ).total_seconds() / 3600
            else:
                elapsed_hours = 0
            profile.apply_decay(elapsed_hours)
    else:
        profile = UserProfile(user_id)

    return profile


# ==================== Endpoints ====================


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_message(
    request: AnalyzeRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Analyze a message for emotional state.
    Requires JWT authentication.

    Flow:
      1. Load profile from MongoDB (with decay applied)
      2. Process message through orchestrator (updates ST/MT/LT via EMA)
      3. Save updated profile back to MongoDB
      4. Return analysis result
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        orchestrator = get_orchestrator()

        # Load profile from DB (or create new)
        profile = await load_profile_from_db(user_id)

        # Inject profile into orchestrator for processing
        orchestrator.user_profiles[user_id] = profile

        # Process message — updates ST, MT, LT via EMA + compounding
        result = orchestrator.process_user_message(
            user_id=user_id,
            message=request.message,
        )

        # Get the updated profile
        updated_profile = orchestrator.user_profiles.get(user_id, profile)

        # Save updated profile to MongoDB
        await save_user_state(user_id, updated_profile.to_db_dict())

        # Build response
        short_state = state_to_label(updated_profile.short_term_state)
        mid_state = state_to_label(updated_profile.mid_term_state)
        long_state = state_to_label(updated_profile.long_term_state)

        return AnalyzeResponse(
            message=request.message,
            short_term_state=short_state,
            mid_term_state=mid_state,
            long_term_state=long_state,
            significance_score=float(getattr(result, "impact_score", 0.0)),
            emotions=getattr(result, "emotions_detected", {}) or {},
            timestamp=datetime.now().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Analysis failed: {str(e)}"
        )


@router.get("/states", response_model=StatesResponse)
async def get_current_states(
    user_id: str = Depends(get_current_user),
):
    """
    Get current emotional states for the authenticated user.
    Loads from MongoDB — returns the persisted ST/MT/LT values.
    """
    try:
        profile = await load_profile_from_db(user_id)

        return StatesResponse(
            short_term=state_to_label(profile.short_term_state),
            mid_term=state_to_label(profile.mid_term_state),
            long_term=state_to_label(profile.long_term_state),
            short_term_score=get_top_score(profile.short_term_state),
            mid_term_score=get_top_score(profile.mid_term_state),
            long_term_score=get_top_score(profile.long_term_state),
            short_term_state=profile.short_term_state,
            mid_term_state=profile.mid_term_state,
            long_term_state=profile.long_term_state,
            message_count=profile.message_count,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get states: {str(e)}"
        )


@router.get("/ema-scores", response_model=EMAScoresResponse)
async def get_ema_timeline(
    user_id: str = Depends(get_current_user),
    days: int = 1,
):
    """
    Get EMA score timeline for chart visualization.
    Currently generates data points from the user's stored states.
    """
    try:
        profile = await load_profile_from_db(user_id)

        now = datetime.now()
        data_points = []

        # Use real profile scores as the basis
        st_score = get_top_score(profile.short_term_state)
        mt_score = get_top_score(profile.mid_term_state)
        lt_score = get_top_score(profile.long_term_state)

        # Generate timeline points showing current state with slight variation
        for i in range(8):
            time_label = (now - timedelta(hours=3 * i)).strftime("%H:%M")
            # Slight variation to simulate timeline
            # (future: store real snapshots per analyze call)
            variation = (i * 0.1) % 0.5
            data_points.append(
                EMADataPoint(
                    time=time_label,
                    shortTerm=round(max(0, st_score - variation), 2),
                    midTerm=round(max(0, mt_score - variation * 0.5), 2),
                    longTerm=round(max(0, lt_score - variation * 0.2), 2),
                )
            )

        return EMAScoresResponse(data=data_points)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get EMA scores: {str(e)}",
        )


@router.post("/reset")
async def reset_user_state(
    user_id: str = Depends(get_current_user),
):
    """
    Reset the authenticated user's emotional state.
    Deletes their state from MongoDB and clears in-memory profile.
    """
    try:
        # Delete from database
        await delete_user_state(user_id)

        # Clear from in-memory orchestrator
        orchestrator = get_orchestrator()
        if user_id in orchestrator.user_profiles:
            del orchestrator.user_profiles[user_id]

        return {
            "status": "success",
            "message": "Emotional state has been reset",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Reset failed: {str(e)}"
        )
