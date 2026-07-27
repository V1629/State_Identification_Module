"""
User Emotional Profile Manager with Adaptive Weight Learning
NOW WITH: Dynamic weight adjustment based on chat history patterns

VERSION: 2.0 - Enhanced Edition
- Robust error handling
- Better null safety
- Enhanced data validation
- Improved edge case handling
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import json
import os
from collections import Counter
import math


# ==========================================================
# ALL 27 EMOTIONS
# ==========================================================

ALL_EMOTIONS = [
    'admiration', 'amusement', 'anger', 'annoyance', 'approval',
    'caring', 'confusion', 'curiosity', 'desire', 'disappointment',
    'disapproval', 'disgust', 'embarrassment', 'excitement', 'fear',
    'gratitude', 'grief', 'joy', 'love', 'nervousness',
    'neutral', 'optimism', 'pride', 'realization', 'relief',
    'remorse', 'sadness', 'surprise'
]


# ==========================================================
# STATE ACTIVATION THRESHOLDS
# ==========================================================

STATE_ACTIVATION_CONFIG = {
    'short_term': {
        'name': '⚡ Short-term',
        'min_days': 0,
        'min_messages': 1,
        'description': 'Recent emotions, always tracking'
    },
    'mid_term': {
        'name': '📈 Mid-term',
        'min_days': 0,          # Message-count only (no day requirement)
        'min_messages': 5,      # DEV: 5 msgs (PROD: 30)
        'description': 'Patterns across sessions',
        'window_size': 15       # Rolling window: look at last 15 messages
    },
    'long_term': {
        'name': '🏛️ Long-term',
        'min_days': 0,          # Message-count only (no day requirement)
        'min_messages': 15,     # DEV: 15 msgs (PROD: 50)
        'description': 'Baseline personality across many sessions'
    }
}


# ==========================================================
# INITIAL WEIGHTS (Hierarchy: emotion > recency > repetition > confidence)
# ==========================================================

INITIAL_WEIGHTS = {
    'emotion_intensity': 0.45,      # Highest - emotion is primary
    'recency_weight': 0.30,         # High - recent events matter
    'recurrence_boost': 0.15,       # Medium - patterns matter
    'temporal_confidence': 0.10     # Lowest - exact timing less critical
}


def get_effective_alpha(base_learning_rate: float, message_count: int, decay_constant: int = 200) -> float:
    """
    Calculate adaptive learning rate based on profile maturity.
    
    As more messages are processed, the learning rate decreases,
    making the profile more stable over time.
    
    Args:
        base_learning_rate: Starting learning rate (e.g., 0.15)
        message_count: Number of messages processed so far
        decay_constant: Controls how fast the rate decays (default 200)
    
    Returns:
        Effective learning rate that decreases with message count
    """
    return base_learning_rate / (1 + message_count / decay_constant)


# ==========================================================
# USER PROFILE CLASS
# ==========================================================

class UserProfile:
    """
    Manages user's emotional profile across three temporal dimensions
    WITH ADAPTIVE WEIGHT LEARNING
    
    Attributes:
        user_id: Unique user identifier
        short_term_state: Recent emotions (0-30 days) - Always active
        mid_term_state: Rolling window patterns (31-365 days) - Activates after 14 days OR 40 messages
        long_term_state: Frequency-based baseline (365+ days) - Activates after 90 days OR 150 messages
        adaptive_weights: Dynamically adjusted weights based on chat patterns
    """

    def __init__(self, user_id: str):
        """
        Initialize user profile
        
        Args:
            user_id: Unique user identifier
        """
        if not user_id or not isinstance(user_id, str):
            raise ValueError("user_id must be a non-empty string")
        
        self.user_id = user_id
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        
        # Initialize all 27 emotions with zero scores
        self.short_term_state = {emotion: 0.0 for emotion in ALL_EMOTIONS}
        self.mid_term_state = {emotion: 0.0 for emotion in ALL_EMOTIONS}
        self.long_term_state = {emotion: 0.0 for emotion in ALL_EMOTIONS}
        
        # Message history - stores all messages with emotions
        self.message_history = []

        # User's baseline typing speed
        self.typing_speed_mean = 5.0
        self.typing_speed_std = 1.0
        
        # State activation tracking
        self.message_count = 0
        self.profile_age_days = 0
        self.state_activation_status = {
            'short_term': True,    # Always active
            'mid_term': False,
            'long_term': False
        }
        
        # Flags to track if states have been initialized
        self.mid_term_initialized = False
        self.long_term_initialized = False
        
        # ===== ADAPTIVE WEIGHTS SYSTEM =====
        # Initialize with hierarchy: emotion > recency > repetition > confidence
        self.adaptive_weights = INITIAL_WEIGHTS.copy()
        self.weights_learning_enabled = False  # Enable when mid_term activates#########################will be enalbled after 50 messages
        self.weight_adjustment_history = []    # Track weight changes over time

        # ===== PER-USER EMA PARAMETERS =====
        self.entropy_penalty_coeff = 0.3
        self.recurrence_step = 0.3
        self.behavior_alpha = 0.2
        self.similarity_threshold = 0.2
        self.impact_multipliers = {
            "recent": {"short_term": 1.0, "mid_term": 0.6, "long_term": 0.2},
            "medium": {"short_term": 0.3, "mid_term": 0.9, "long_term": 0.5},
            "distant": {"short_term": 0.05, "mid_term": 0.3, "long_term": 0.8},
            "unknown": {"short_term": 0.5, "mid_term": 0.5, "long_term": 0.3},
            "future": {"short_term": 0.7, "mid_term": 0.4, "long_term": 0.0}
        }

    # ============================================================
    # PROFILE AGE CALCULATION
    # ============================================================

    def calculate_profile_age(self) -> int:
        """
        Calculate days since profile creation
        
        Returns:
            Number of days since profile creation
        """
        try:
            self.profile_age_days = (datetime.now() - self.created_at).days
            return self.profile_age_days
        except Exception as e:
            print(f"⚠️  Error calculating profile age: {e}")
            return 0

    # ============================================================
    # STATE ACTIVATION LOGIC
    # ============================================================

    def is_state_activated(self, state_type: str) -> bool:
        """
        Check if a state should be updated based on thresholds
        
        Uses HYBRID approach: Activates if EITHER time OR message threshold met
        
        Args:
            state_type: 'short_term', 'mid_term', or 'long_term'
        
        Returns:
            True if state is activated, False otherwise
        """
        threshold = STATE_ACTIVATION_CONFIG.get(state_type)
        if not threshold:
            return False
        
        try:
            # Update age first
            self.calculate_profile_age()
            
            min_days = threshold.get('min_days', 0)
            min_messages = threshold.get('min_messages', 0)
            
            days_met = self.profile_age_days >= min_days
            messages_met = self.message_count >= min_messages
            
            # OR logic: activate if either condition is met
            is_activated = days_met or messages_met
            
            # Update status tracking
            self.state_activation_status[state_type] = is_activated
            
            return is_activated
        except Exception as e:
            print(f"⚠️  Error checking state activation for {state_type}: {e}")
            return False

    def get_state_activation_info(self) -> Dict[str, Dict]:
        """
        Get current activation status and progress for all states
        
        Returns:
            Dictionary with activation info for each state
        """
        try:
            self.calculate_profile_age()
            
            info = {}
            for state_type, threshold in STATE_ACTIVATION_CONFIG.items():
                min_days = threshold.get('min_days', 0)
                min_messages = threshold.get('min_messages', 0)
                
                days_progress = (self.profile_age_days / min_days * 100) if min_days > 0 else 100
                messages_progress = (self.message_count / min_messages * 100) if min_messages > 0 else 100
                
                days_met = self.profile_age_days >= min_days
                messages_met = self.message_count >= min_messages
                
                # Determine what activated the state
                if days_met and messages_met:
                    activated_by = 'both'
                elif days_met:
                    activated_by = 'days'
                elif messages_met:
                    activated_by = 'messages'
                else:
                    activated_by = 'not_yet'
                
                days_remaining = max(0, min_days - self.profile_age_days)
                messages_remaining = max(0, min_messages - self.message_count)
                
                info[state_type] = {
                    'is_active': days_met or messages_met,
                    'days_progress': min(100.0, days_progress),
                    'messages_progress': min(100.0, messages_progress),
                    'days_remaining': days_remaining,
                    'messages_remaining': messages_remaining,
                    'activated_by': activated_by
                }
            
            return info
        except Exception as e:
            print(f"⚠️  Error getting state activation info: {e}")
            return {
                'short_term': {'is_active': True, 'days_progress': 0, 'messages_progress': 0, 
                              'days_remaining': 0, 'messages_remaining': 0, 'activated_by': 'error'},
                'mid_term': {'is_active': False, 'days_progress': 0, 'messages_progress': 0,
                            'days_remaining': 14, 'messages_remaining': 40, 'activated_by': 'not_yet'},
                'long_term': {'is_active': False, 'days_progress': 0, 'messages_progress': 0,
                             'days_remaining': 90, 'messages_remaining': 150, 'activated_by': 'not_yet'}
            }

    # ============================================================
    # EMOTIONAL STATE UPDATES
    # ============================================================

    def update_emotional_state(
        self,
        emotions: Dict[str, float],
        impact_score: float,
        state_updates: Dict[str, Dict[str, float]],
        message: str,
        timestamp: datetime,
        temporal_category: str = "unknown"
    ):
        """
        Update user's emotional state based on new message
        
        Args:
            emotions: Detected emotions {emotion: score}
            impact_score: Overall impact score
            state_updates: State-specific updates
            message: Original message
            timestamp: Message timestamp
            temporal_category: Temporal category of reference
        """
        try:
            self.message_count += 1
            self.last_updated = datetime.now()
            
            # Store in message history
            self.message_history.append({
                'message': message,
                'timestamp': timestamp,
                'emotions_detected': emotions,
                'impact_score': impact_score,
                'temporal_category': temporal_category
            })
            
            # ===== EMA-BASED STATE UPDATES =====
            short_term_learning_rate = get_effective_alpha(0.30, self.message_count)
            mid_term_learning_rate = get_effective_alpha(0.125, self.message_count)
            long_term_learning_rate = get_effective_alpha(0.02, self.message_count)

            for emotion in ALL_EMOTIONS:
                short_term_impact_value = 0.0
                if emotion in state_updates:
                    short_term_impact_value = state_updates[emotion].get('short_term', 0.0)

                # Short-term EMA (always active)
                if self.is_state_activated('short_term'):
                    previous_short_term_value = self.short_term_state.get(emotion, 0.0)
                    self.short_term_state[emotion] = (
                        short_term_learning_rate * short_term_impact_value 
                        + (1 - short_term_learning_rate) * previous_short_term_value
                    )

                # Mid-term EMA
                mid_term_impact_value = 0.0
                if emotion in state_updates:
                    mid_term_impact_value = state_updates[emotion].get('mid_term', 0.0)
                if self.is_state_activated('mid_term'):
                    previous_mid_term_value = self.mid_term_state.get(emotion, 0.0)
                    self.mid_term_state[emotion] = (
                        mid_term_learning_rate * mid_term_impact_value 
                        + (1 - mid_term_learning_rate) * previous_mid_term_value
                    )

                # Long-term EMA
                long_term_impact_value = 0.0
                if emotion in state_updates:
                    long_term_impact_value = state_updates[emotion].get('long_term', 0.0)
                if self.is_state_activated('long_term'):
                    previous_long_term_value = self.long_term_state.get(emotion, 0.0)
                    self.long_term_state[emotion] = (
                        long_term_learning_rate * long_term_impact_value 
                        + (1 - long_term_learning_rate) * previous_long_term_value
                    )

            # Update adaptive weights every message using EMA
            self._update_adaptive_weights_ema(emotions, impact_score)
            
        except Exception as e:
            print(f"⚠️  Error updating emotional state: {e}")

    # ============================================================
    # ADAPTIVE WEIGHT LEARNING SYSTEM
    # ============================================================

    def _update_adaptive_weights_ema(self, emotions: Dict[str, float], impact_score: float):
        """
        Update adaptive weights using EMA based on observed signals.
        Called every message (no 10-message checkpoint).
        """
        try:
            if not emotions:
                return

            computed_factors = getattr(self, '_last_computed_factors', None)
            if computed_factors:
                emotion_intensity_value = computed_factors.get('emotion_intensity', max(emotions.values()))
                recency_weight_value = computed_factors.get('recency_weight', 0.5)
                recurrence_boost_value = computed_factors.get('recurrence_boost', 0.5)
                temporal_confidence_value = computed_factors.get('temporal_confidence', 0.5)
            else:
                emotion_intensity_value = max(emotions.values()) if emotions else 0.0
                recency_weight_value = 0.5
                recurrence_boost_value = 0.5
                temporal_confidence_value = 0.5

            total_signal_strength = emotion_intensity_value + recency_weight_value + recurrence_boost_value + temporal_confidence_value
            if total_signal_strength <= 0:
                return

            observed_weight_proportions = {
                'emotion_intensity': emotion_intensity_value / total_signal_strength,
                'recency_weight': recency_weight_value / total_signal_strength,
                'recurrence_boost': recurrence_boost_value / total_signal_strength,
                'temporal_confidence': temporal_confidence_value / total_signal_strength,
            }

            base_learning_rates = {
                'emotion_intensity': 0.12,
                'recency_weight': 0.15,
                'recurrence_boost': 0.25,
                'temporal_confidence': 0.20,
            }

            previous_weights = self.adaptive_weights.copy()

            for weight_key in self.adaptive_weights:
                base_learning_rate = base_learning_rates.get(weight_key, 0.15)
                effective_learning_rate = get_effective_alpha(base_learning_rate, self.message_count)
                self.adaptive_weights[weight_key] = (
                    effective_learning_rate * observed_weight_proportions[weight_key] 
                    + (1 - effective_learning_rate) * self.adaptive_weights[weight_key]
                )

            total_weight_sum = sum(self.adaptive_weights.values())
            if total_weight_sum > 0:
                self.adaptive_weights = {key: value / total_weight_sum for key, value in self.adaptive_weights.items()}

            weight_changed = any(
                abs(self.adaptive_weights.get(key, 0) - previous_weights.get(key, 0)) > 0.001
                for key in previous_weights
            )
            if weight_changed:
                self.weight_adjustment_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'message_count': self.message_count,
                    'old_weights': previous_weights,
                    'new_weights': self.adaptive_weights.copy(),
                    'reason': self._get_adjustment_reason(previous_weights, self.adaptive_weights)
                })
        except Exception as e:
            print(f"⚠️  Error updating adaptive weights via EMA: {e}")

    @staticmethod
    def _get_adjustment_reason(old_weights: dict, new_weights: dict) -> str:
        """Explain why weights changed"""
        try:
            change_descriptions = []
            
            for weight_key in old_weights:
                if weight_key in new_weights:
                    weight_difference = new_weights[weight_key] - old_weights[weight_key]
                    if abs(weight_difference) > 0.01:
                        change_direction = "increased" if weight_difference > 0 else "decreased"
                        change_descriptions.append(f"{weight_key}: {change_direction} by {abs(weight_difference):.3f}")
            
            return " | ".join(change_descriptions) if change_descriptions else "No significant changes"
        except Exception as e:
            return f"Error: {e}"

    # ============================================================
    # QUERY METHODS
    # ============================================================

    def get_top_emotions_by_frequency(self, top_n: int = 3) -> List[Tuple[str, float, int]]:
        """
        Get top emotions by frequency across all messages
        
        Args:
            top_n: Number of top emotions to return
        
        Returns:
            List of (emotion, avg_score, frequency) tuples
        """
        try:
            if not self.message_history:
                return []
            
            emotion_data = {}
            
            for msg in self.message_history:
                emotions = msg.get('emotions_detected', {})
                for emotion, score in emotions.items():
                    if emotion not in emotion_data:
                        emotion_data[emotion] = {'scores': [], 'count': 0}
                    emotion_data[emotion]['scores'].append(score)
                    emotion_data[emotion]['count'] += 1
            
            if not emotion_data:
                return []
            
            emotion_stats = []
            for emotion, data in emotion_data.items():
                avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0.0
                frequency = data['count']
                emotion_stats.append((emotion, avg_score, frequency))
            
            emotion_stats.sort(key=lambda x: (x[2], x[1]), reverse=True)
            
            return emotion_stats[:top_n]
        except Exception as e:
            print(f"⚠️  Error getting top emotions by frequency: {e}")
            return []

    def get_all_states_with_top_emotions(self, top_n: int = 5) -> Dict[str, List[Tuple[str, float]]]:
        """
        Get top N emotions for all three states
        
        Args:
            top_n: Number of top emotions per state
        
        Returns:
            Dict with state names as keys and lists of (emotion, score) tuples
        """
        try:
            result = {}
            
            sorted_short = sorted(
                self.short_term_state.items(),
                key=lambda x: x[1],
                reverse=True
            )
            result['short_term'] = sorted_short[:top_n]
            
            if self.is_state_activated('mid_term'):
                sorted_mid = sorted(
                    self.mid_term_state.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                result['mid_term'] = sorted_mid[:top_n]
            else:
                result['mid_term'] = [("N/A", 0.0)]
            
            if self.is_state_activated('long_term'):
                sorted_long = sorted(
                    self.long_term_state.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                result['long_term'] = sorted_long[:top_n]
            else:
                result['long_term'] = [("N/A", 0.0)]
            
            return result
        except Exception as e:
            print(f"⚠️  Error getting all states: {e}")
            return {
                'short_term': [("N/A", 0.0)],
                'mid_term': [("N/A", 0.0)],
                'long_term': [("N/A", 0.0)]
            }

    def get_top_emotions_or_placeholder(self, state_type: str, top_n: int = 1) -> List[Tuple[str, float]]:
        """
        Get top emotions for a state or placeholder if not active
        
        Args:
            state_type: 'short_term', 'mid_term', or 'long_term'
            top_n: Number of emotions to return
        
        Returns:
            List of (emotion, score) tuples or [("N/A", 0.0)]
        """
        try:
            if not self.is_state_activated(state_type):
                return [("N/A", 0.0)]
            
            if state_type == 'short_term':
                state = self.short_term_state
            elif state_type == 'mid_term':
                state = self.mid_term_state
            elif state_type == 'long_term':
                state = self.long_term_state
            else:
                return [("N/A", 0.0)]
            
            sorted_emotions = sorted(
                state.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            result = sorted_emotions[:top_n]
            return result if result else [("N/A", 0.0)]
        except Exception as e:
            print(f"⚠️  Error getting top emotions for {state_type}: {e}")
            return [("N/A", 0.0)]

    # ============================================================
    # DECAY ENGINE
    # ============================================================

    def apply_decay(self, hours_since_last_update: float):
        """
        Apply time-based decay to emotional states.
        Called when loading a profile from DB after a gap.

        Decay rates (from docs/state-management.md):
          - ST: Fast exponential  Relevance(t) = Initial × e^(-0.3t)
          - MT: S-curve with 60-day half-life
          - LT: Asymptotic — never fully decays (no decay applied)

        Args:
            hours_since_last_update: Hours since profile was last updated
        """
        days_elapsed = hours_since_last_update / 24.0

        if days_elapsed < 0.01:  # Less than ~15 minutes — skip
            return

        # --- Short-Term: Fast exponential decay (λ = 0.3/day) ---
        # 70% reduction every 2 days, auto-expire by 14 days
        st_decay_factor = math.exp(-0.3 * days_elapsed)
        for emotion in ALL_EMOTIONS:
            self.short_term_state[emotion] *= st_decay_factor

        # --- Mid-Term: S-curve decay (half-life 60 days) ---
        # Only decay if more than 1 day has passed
        if days_elapsed > 1.0:
            k = 0.1   # Steepness of S-curve
            t_half = 60.0  # Half-life in days
            mt_decay_factor = 1.0 / (1.0 + math.exp(k * (days_elapsed - t_half)))
            for emotion in ALL_EMOTIONS:
                self.mid_term_state[emotion] *= mt_decay_factor

        # --- Long-Term: No decay ---
        # LT represents permanent baseline, never fully decays

    # ============================================================
    # COMPOUNDING DETECTION (ST → MT ESCALATION)
    # ============================================================

    def check_compounding(self):
        """
        Check for ST → MT compounding escalation.

        Rule (from docs/state-management.md):
          If 3+ messages in the current session share a dominant emotion,
          boost that emotion in the mid-term state.

        This detects patterns like:
          Day 1: "Traffic stress" (ST)
          Day 3: "Meeting went bad" (ST)
          Day 5: "Deadline pressure" (ST)
          → Escalate: "Work stress pattern" (MT)
        """
        if not self.is_state_activated('mid_term'):
            return

        if len(self.message_history) < 3:
            return

        # Look at recent messages in current session (up to last 7)
        recent = self.message_history[-7:]

        # Count dominant emotions across recent messages
        emotion_counts: Dict[str, int] = {}
        for msg in recent:
            emotions = msg.get('emotions_detected', {})
            if emotions:
                dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
                emotion_counts[dominant_emotion] = (
                    emotion_counts.get(dominant_emotion, 0) + 1
                )

        # If any emotion appears 3+ times, boost it in MT
        for emotion, count in emotion_counts.items():
            if count >= 3:
                boost = 0.05 * (count - 2)  # 5% boost per extra occurrence
                current = self.mid_term_state.get(emotion, 0.0)
                self.mid_term_state[emotion] = min(1.0, current + boost)

    # ============================================================
    # SIGNIFICANCE SCORE (PRISM)
    # ============================================================

    def calculate_significance_score(
        self,
        emotion_intensity: float,
        impact_score: float,
    ) -> float:
        """
        Calculate PRISM-based significance score.

        From docs/05-core-concepts.md:
          SS = (0.25 × Intensity) + (0.20 × Persistence)
             + (0.20 × Recency) + (0.15 × Impact) + (0.20 × Volatility)

        Args:
            emotion_intensity: From ImpactCalculator (0-1)
            impact_score: Compound impact score (0-1)

        Returns:
            Significance score [0, 1]
        """
        # Intensity: from emotion detector
        intensity = emotion_intensity

        # Persistence: based on accumulated message count (capped at 1.0)
        persistence = min(1.0, self.message_count / 10)

        # Recency: always 1.0 for current message
        recency = 1.0

        # Impact: from temporal impact calculation
        impact = impact_score

        # Volatility: standard deviation of recent intensities
        recent_intensities = []
        for msg in self.message_history[-5:]:
            emotions = msg.get('emotions_detected', {})
            if emotions:
                recent_intensities.append(max(emotions.values()))

        if len(recent_intensities) >= 2:
            mean_int = sum(recent_intensities) / len(recent_intensities)
            variance = sum(
                (x - mean_int) ** 2 for x in recent_intensities
            ) / len(recent_intensities)
            volatility = math.sqrt(variance)
        else:
            volatility = 0.0

        # Weighted sum
        ss = (
            0.25 * intensity
            + 0.20 * persistence
            + 0.20 * recency
            + 0.15 * impact
            + 0.20 * volatility
        )

        return max(0.0, min(1.0, ss))

    # ============================================================
    # SERIALIZATION
    # ============================================================

    def to_db_dict(self) -> Dict[str, Any]:
        """
        Convert profile to dict for MongoDB storage.
        Stores only states and parameters — no message history.
        """
        return {
            'short_term_state': self.short_term_state,
            'mid_term_state': self.mid_term_state,
            'long_term_state': self.long_term_state,
            'message_count': self.message_count,
            'adaptive_weights': self.adaptive_weights,
            'weights_learning_enabled': self.weights_learning_enabled,
            'entropy_penalty_coeff': self.entropy_penalty_coeff,
            'recurrence_step': self.recurrence_step,
            'behavior_alpha': self.behavior_alpha,
            'similarity_threshold': self.similarity_threshold,
            'impact_multipliers': self.impact_multipliers,
            'created_at': self.created_at,
            'last_updated': datetime.now(),
        }

    @classmethod
    def from_db_dict(cls, user_id: str, data: dict) -> 'UserProfile':
        """
        Create UserProfile from MongoDB document.
        Restores states and parameters, leaves message_history empty
        (messages are not persisted — only states are).

        Args:
            user_id: User identifier (MongoDB ObjectId as string)
            data: Document from user_states collection

        Returns:
            Populated UserProfile instance
        """
        profile = cls(user_id)

        if not data:
            return profile

        # Restore emotional states
        for emotion in ALL_EMOTIONS:
            profile.short_term_state[emotion] = (
                data.get('short_term_state', {}).get(emotion, 0.0)
            )
            profile.mid_term_state[emotion] = (
                data.get('mid_term_state', {}).get(emotion, 0.0)
            )
            profile.long_term_state[emotion] = (
                data.get('long_term_state', {}).get(emotion, 0.0)
            )

        # Restore counts
        profile.message_count = data.get('message_count', 0)

        # Restore timestamps
        created_at = data.get('created_at')
        if created_at:
            if isinstance(created_at, datetime):
                profile.created_at = created_at
            elif isinstance(created_at, str):
                profile.created_at = datetime.fromisoformat(created_at)

        last_updated = data.get('last_updated')
        if last_updated:
            if isinstance(last_updated, datetime):
                profile.last_updated = last_updated
            elif isinstance(last_updated, str):
                profile.last_updated = datetime.fromisoformat(last_updated)

        # Restore adaptive parameters
        profile.adaptive_weights = data.get(
            'adaptive_weights', INITIAL_WEIGHTS.copy()
        )
        profile.weights_learning_enabled = data.get(
            'weights_learning_enabled', False
        )
        profile.entropy_penalty_coeff = data.get('entropy_penalty_coeff', 0.3)
        profile.recurrence_step = data.get('recurrence_step', 0.3)
        profile.behavior_alpha = data.get('behavior_alpha', 0.2)
        profile.similarity_threshold = data.get('similarity_threshold', 0.2)
        profile.impact_multipliers = data.get(
            'impact_multipliers', profile.impact_multipliers
        )

        # Re-check activation based on restored message_count
        profile.state_activation_status['mid_term'] = (
            profile.is_state_activated('mid_term')
        )
        profile.state_activation_status['long_term'] = (
            profile.is_state_activated('long_term')
        )

        return profile

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary (for API responses)"""
        try:
            activation_info = self.get_state_activation_info()
            
            return {
                'user_id': self.user_id,
                'created_at': self.created_at.isoformat(),
                'last_updated': self.last_updated.isoformat(),
                'message_count': self.message_count,
                'profile_age_days': self.profile_age_days,
                'short_term_state': self.short_term_state,
                'mid_term_state': self.mid_term_state,
                'long_term_state': self.long_term_state,
                'top_emotions': self.get_all_states_with_top_emotions(),
                'state_activation_info': activation_info,
                'adaptive_weights': self.adaptive_weights,
                'weights_learning_enabled': self.weights_learning_enabled,
                'entropy_penalty_coeff': self.entropy_penalty_coeff,
                'recurrence_step': self.recurrence_step,
                'behavior_alpha': self.behavior_alpha,
                'similarity_threshold': self.similarity_threshold,
                'impact_multipliers': self.impact_multipliers,
                'message_history_count': len(self.message_history),
            }
        except Exception as e:
            print(f"⚠️  Error converting profile to dict: {e}")
            return {
                'user_id': self.user_id,
                'error': str(e)
            }

    def to_json(self) -> str:
        """Convert profile to JSON string"""
        try:
            return json.dumps(self.to_dict(), indent=2, default=str)
        except Exception as e:
            print(f"⚠️  Error converting profile to JSON: {e}")
            return json.dumps({'user_id': self.user_id, 'error': str(e)})

    def save_to_file(self, filename: str) -> bool:
        """
        Save profile to JSON file
        
        Args:
            filename: Path to save file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            directory = os.path.dirname(filename)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.to_json())
            return True
        except Exception as e:
            print(f"❌ Error saving profile: {e}")
            return False

    @classmethod
    def load_from_file(cls, filename: str) -> Optional['UserProfile']:
        """
        Load profile from JSON file
        
        Args:
            filename: Path to load file
        
        Returns:
            UserProfile instance or None if failed
        """
        try:
            if not os.path.exists(filename):
                return None
            
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'user_id' not in data:
                print("❌ Error: Invalid profile file (missing user_id)")
                return None
            
            profile = cls(data['user_id'])
            
            profile.short_term_state = {
                k: float(v) for k, v in data.get('short_term_state', {}).items()
                if k in ALL_EMOTIONS
            }
            profile.mid_term_state = {
                k: float(v) for k, v in data.get('mid_term_state', {}).items()
                if k in ALL_EMOTIONS
            }
            profile.long_term_state = {
                k: float(v) for k, v in data.get('long_term_state', {}).items()
                if k in ALL_EMOTIONS
            }
            
            if 'created_at' in data:
                profile.created_at = datetime.fromisoformat(data['created_at'])
            if 'last_updated' in data:
                profile.last_updated = datetime.fromisoformat(data['last_updated'])
            
            profile.message_count = data.get('message_count', 0)
            
            profile.adaptive_weights = data.get('adaptive_weights', INITIAL_WEIGHTS.copy())
            profile.weights_learning_enabled = data.get('weights_learning_enabled', False)

            profile.entropy_penalty_coeff = data.get('entropy_penalty_coeff', 0.3)
            profile.recurrence_step = data.get('recurrence_step', 0.3)
            profile.behavior_alpha = data.get('behavior_alpha', 0.2)
            profile.similarity_threshold = data.get('similarity_threshold', 0.2)
            profile.impact_multipliers = data.get('impact_multipliers', profile.impact_multipliers)
            
            return profile
        except Exception as e:
            print(f"❌ Error loading profile: {e}")
            return None

    # ============================================================
    # DISPLAY
    # ============================================================

    def display_profile(self, top_n: int = 5):
        """Pretty print user profile with activation status and adaptive weights"""
        try:
            print("\n" + "="*100)
            print(f"📊 USER EMOTIONAL PROFILE: {self.user_id}")
            print("="*100)
            print(f"Created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Last Updated: {self.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Messages Analyzed: {self.message_count}")
            print(f"Profile Age: {self.calculate_profile_age()} days")
            print("="*100)
            
            activation_info = self.get_state_activation_info()
            print("\n🔓 STATE ACTIVATION STATUS:")
            print("-" * 100)
            
            for state_type in ['short_term', 'mid_term', 'long_term']:
                info = activation_info.get(state_type, {})
                status = "✅ ACTIVE" if info.get('is_active', False) else "⏳ INACTIVE"
                threshold = STATE_ACTIVATION_CONFIG.get(state_type, {})
                
                print(f"\n{threshold.get('name', state_type)} {status}")
                print(f"   Days:     {info.get('days_progress', 0):5.1f}% ({self.profile_age_days}/{threshold.get('min_days', 0)} days)")
                print(f"   Messages: {info.get('messages_progress', 0):5.1f}% ({self.message_count}/{threshold.get('min_messages', 0)} messages)")
            
            print("\n" + "="*100 + "\n")
        except Exception as e:
            print(f"\n❌ Error displaying profile: {e}\n")
