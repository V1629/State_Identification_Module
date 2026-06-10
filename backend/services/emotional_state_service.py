"""
Emotional State Service
High-level service for emotional analysis operations
"""

import sys
import os
from typing import Dict, Optional

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.orchestrator import EmotionalStateOrchestrator
from core.user_profile import UserProfile


class EmotionalStateService:
    """Service for emotional state operations"""
    
    def __init__(self):
        self.orchestrator = EmotionalStateOrchestrator()
        self.user_profiles: Dict[str, UserProfile] = {}
    
    def analyze_message(self, message: str, user_id: str = "default_user") -> Dict:
        """
        Analyze emotional content of a message
        
        Args:
            message: Text to analyze
            user_id: User identifier
            
        Returns:
            Dict with analysis results
        """
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")
        
        # Get or create user profile
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
        
        user_profile = self.user_profiles[user_id]
        
        # Analyze using orchestrator
        result = self.orchestrator.analyze_message(
            message=message,
            user_profile=user_profile
        )
        
        # Update user profile
        self.user_profiles[user_id] = user_profile
        
        return result
    
    def get_user_state(self, user_id: str) -> Dict:
        """Get current emotional state for user"""
        if user_id not in self.user_profiles:
            return {
                "short_term_state": "Neutral",
                "mid_term_state": "Stable",
                "long_term_state": "Positive",
                "short_term_score": 5.0,
                "mid_term_score": 5.0,
                "long_term_score": 5.0
            }
        
        profile = self.user_profiles[user_id]
        return {
            "short_term_state": profile.short_term_state,
            "mid_term_state": profile.mid_term_state,
            "long_term_state": profile.long_term_state,
            "short_term_score": profile.short_term_ema,
            "mid_term_score": profile.mid_term_ema,
            "long_term_score": profile.long_term_ema
        }
    
    def reset_user(self, user_id: str) -> None:
        """Reset user state"""
        self.user_profiles[user_id] = UserProfile(user_id=user_id)


# Global service instance
_service: Optional[EmotionalStateService] = None


def get_service() -> EmotionalStateService:
    """Get or create global service instance"""
    global _service
    if _service is None:
        _service = EmotionalStateService()
    return _service
