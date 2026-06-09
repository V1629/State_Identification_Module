"""
Direct Test Script for Orchestrator with Advanced State Tracking
Shows detailed state aggregation and frequency analysis

ROBUST VERSION: Handles incomplete orchestrator.py implementation
"""

import sys
import os
from datetime import datetime
import time
from typing import Optional

# Add parent directory to path so we can import core module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("\n" + "="*100)
print("🧪 ORCHESTRATOR TEST - Advanced Emotional State Analysis")
print("="*100)

# ==========================================================
# MODULE IMPORTS WITH ERROR HANDLING
# ==========================================================

print("\n📦 Importing modules...")

# Import orchestrator components
try:
    from core.orchestrator import (
        ImpactCalculator, 
        IncidentAnalysis, 
        IncidentDetector, 
        EmotionalStateOrchestrator
    )
    print("   ✅ orchestrator imported")
except ImportError as e:
    print(f"   ❌ Error importing orchestrator: {e}")
    print("   Make sure orchestrator.py is in the core directory")
    sys.exit(1)

# Import user profile
try:
    from core.user_profile import UserProfile, ALL_EMOTIONS, INITIAL_WEIGHTS
    print("   ✅ user_profile imported")
except ImportError as e:
    print(f"   ❌ Error importing user_profile: {e}")
    print("   Make sure user_profile.py is in the core directory")
    sys.exit(1)

# Import emotional detector
try:
    from core.emotional_detector import classify_emotions
    print("   ✅ emotional_detector imported")
except ImportError as e:
    print(f"   ❌ Error importing emotional_detector: {e}")
    print("   Make sure emotional_detector.py is in the core directory")
    sys.exit(1)

# Import temporal extractor
try:
    from core.temporal_extractor import TemporalExtractor
    print("   ✅ temporal_extractor imported")
except ImportError as e:
    print(f"   ❌ Error importing temporal_extractor: {e}")
    print("   Make sure temporal_extractor.py is in the core directory")
    sys.exit(1)

# Optional: Try importing logger (not critical)
logger = None
try:
    from core.chat_logger import ChatLogger
    logger = ChatLogger("chat_logs.xlsx")
    print("   ✅ ChatLogger initialized")
except Exception as e:
    print(f"   ⚠️  Logger not available: {e}")
    print("   Continuing without logging feature")

# ==========================================================
# CREATE ORCHESTRATOR & TEST IT
# ==========================================================

print("\n🔧 Creating orchestrator...")
try:
    orchestrator = EmotionalStateOrchestrator()
    print("   ✅ Orchestrator created")
except Exception as e:
    print(f"   ❌ Error creating orchestrator: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test if process_user_message is implemented
print("\n🔍 Testing orchestrator.process_user_message()...")
try:
    test_result = orchestrator.process_user_message(
        user_id="test_check",
        message="test message",
        reference_date=datetime.now(),
        writing_time=1.0
    )
    
    if test_result is None:
        print("   ❌ ERROR: process_user_message() returns None!")
        print("\n" + "="*100)
        print("CRITICAL: Your orchestrator.py file is incomplete!")
        print("="*100)
        print("\nThe process_user_message() method is not fully implemented.")
        print("It's missing the implementation body and returns None by default.")
        print("\nTo fix this:")
        print("1. Check orchestrator_completion.py for the missing code")
        print("2. Add the missing implementation to your orchestrator.py")
        print("3. The method should return an IncidentAnalysis object")
        print("\nExpected structure:")
        print("  - Step 1: Detect emotions (classify_emotions)")
        print("  - Step 2: Extract temporal references")
        print("  - Step 3: Initialize/get user profile")
        print("  - Step 4: Detect repeated incidents")
        print("  - Step 5: Calculate impact")
        print("  - Step 6: Get state impact multipliers")
        print("  - Step 7: Update user profile")
        print("  - Step 8: Generate analysis summary")
        print("  - Step 9: Return IncidentAnalysis object")
        print("\n" + "="*100)
        sys.exit(1)
    elif not isinstance(test_result, IncidentAnalysis):
        print(f"   ❌ ERROR: process_user_message() returns {type(test_result)}, expected IncidentAnalysis")
        sys.exit(1)
    else:
        print("   ✅ process_user_message() working correctly")
        # Clean up test profile
        if "test_check" in orchestrator.user_profiles:
            del orchestrator.user_profiles["test_check"]
except Exception as e:
    print(f"   ❌ Error testing orchestrator: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("   ✅ All checks passed - ready to start!\n")

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def display_emotions(emotions_dict: dict, top_n: int = 5):
    """Display emotions with visual bars"""
    if not emotions_dict:
        print("   No emotions detected")
        return
    
    emotions_sorted_by_score = sorted(
        emotions_dict.items(),
        key=lambda emotion_item: emotion_item[1],
        reverse=True
    )
    
    for display_rank, (emotion_name, emotion_score) in enumerate(emotions_sorted_by_score[:top_n], 1):
        visual_bar = "█" * int(emotion_score * 25)
        print(f"   {display_rank}. {emotion_name:20s} │ {visual_bar:25s} │ {emotion_score:.4f}")


def display_temporal_references(temporal_ref_data: dict):
    """Display temporal references found in message"""
    if not temporal_ref_data or not temporal_ref_data.get('has_temporal_ref'):
        print("   No temporal references detected")
        return
    
    print(f"   Phrases found: {temporal_ref_data.get('phrases_found', [])}")
    
    parsed_date_results = temporal_ref_data.get('parsed_dates', [])
    if parsed_date_results:
        for parsed_item in parsed_date_results[:3]:  # Show top 3
            print(f"\n   • {parsed_item.get('phrase', 'N/A')}")
            print(f"     Category: {parsed_item.get('age_category', 'unknown')}", end="")
            print(f" | Confidence: {parsed_item.get('confidence', 0.0):.2f}")


def display_current_states(profile: UserProfile):
    """Display current emotional states for all time periods"""
    print(f"\n💤 CURRENT EMOTIONAL STATE:")
    
    all_states_with_emotions = profile.get_all_states_with_top_emotions(top_n=2)
    
    for temporal_state_type in ['short_term', 'mid_term', 'long_term']:
        state_icon = "⚡" if temporal_state_type == "short_term" else ("📈" if temporal_state_type == "mid_term" else "🏛️")
        state_emotions = all_states_with_emotions.get(temporal_state_type, [])
        
        if not profile.is_state_activated(temporal_state_type):
            print(f"\n   {state_icon} {temporal_state_type.upper():12s}: ⏳ Not activated")
        elif state_emotions and len(state_emotions) > 0 and state_emotions[0][0] != "N/A":
            print(f"\n   {state_icon} {temporal_state_type.upper():12s}: {state_emotions[0][0]} ({state_emotions[0][1]:.4f})")
            if len(state_emotions) > 1 and state_emotions[1][0] != "N/A":
                print(f"      Secondary: {state_emotions[1][0]} ({state_emotions[1][1]:.4f})")
        else:
            print(f"\n   {state_icon} {temporal_state_type.upper():12s}: No emotions yet")


def display_activation_status(profile: UserProfile):
    """Display state activation status"""
    print(f"\n🔓 STATE ACTIVATION STATUS:")
    
    all_activation_info = profile.get_state_activation_info()
    
    for temporal_state_type in ['short_term', 'mid_term', 'long_term']:
        state_info = all_activation_info[temporal_state_type]
        activation_status_text = "✅ ACTIVE" if state_info['is_active'] else "⏳ INACTIVE"
        
        state_icon = "⚡" if temporal_state_type == "short_term" else ("📈" if temporal_state_type == "mid_term" else "🏛️")
        
        print(f"\n   {state_icon} {temporal_state_type.upper():12s}: {activation_status_text}")
        print(f"      Days: {profile.profile_age_days} | Messages: {profile.message_count}")


def display_frequency_analysis(profile: UserProfile):
    """Display emotion frequency analysis from history"""
    if not profile.message_history or len(profile.message_history) == 0:
        print("⚠️  No chat history yet\n")
        return
    
    print("\n" + "="*100)
    print("📊 EMOTION FREQUENCY ANALYSIS")
    print("="*100)
    
    top_emotions_by_frequency = profile.get_top_emotions_by_frequency(top_n=10)
    
    print(f"\nAnalyzing {len(profile.message_history)} messages...\n")
    print(f"{'Rank':<6} {'Emotion':<20} {'Avg Score':<15} {'Frequency':<15}")
    print("-" * 100)
    
    if top_emotions_by_frequency:
        max_frequency_value = max([freq_data[2] for freq_data in top_emotions_by_frequency])
        for display_rank, (emotion_name, average_score, occurrence_frequency) in enumerate(top_emotions_by_frequency, 1):
            visual_bar = "█" * int(occurrence_frequency / max_frequency_value * 30) if max_frequency_value > 0 else ""
            print(f"{display_rank:<6} {emotion_name:<20} {average_score:<15.4f} {occurrence_frequency:<15} {visual_bar}")
    else:
        print("No emotion data available yet")
    
    print("\n" + "="*100 + "\n")


def log_to_excel(excel_logger, profile: UserProfile, analysis, message: str):
    """Log chat data to Excel file"""
    if not excel_logger:
        return
    
    try:
        # Get detected emotions
        if analysis.emotions_detected:
            highest_scoring_emotion = max(analysis.emotions_detected.items(), key=lambda emotion_item: emotion_item[1])
            detected_emotion_name = highest_scoring_emotion[0]
            detected_emotion_score = highest_scoring_emotion[1]
        else:
            detected_emotion_name = ""
            detected_emotion_score = 0.0
        
        # Current state (from current message)
        current_message_state = {
            'short_term': [(detected_emotion_name, detected_emotion_score)] if detected_emotion_name else [],
            'mid_term': [(detected_emotion_name, detected_emotion_score)] if detected_emotion_name else [],
            'long_term': [(detected_emotion_name, detected_emotion_score)] if detected_emotion_name else [],
        }
        
        # Profile state (from accumulated profile)
        accumulated_profile_state = {
            'short_term': profile.get_top_emotions_or_placeholder('short_term', 1),
            'mid_term': profile.get_top_emotions_or_placeholder('mid_term', 1),
            'long_term': profile.get_top_emotions_or_placeholder('long_term', 1),
        }
        
        # Get activation info
        state_activation_info = profile.get_state_activation_info()
        
        # Log to Excel
        excel_logger.log_chat(
            message=message,
            impact_score=analysis.impact_score,
            current_state=current_message_state,
            profile_state=accumulated_profile_state,
            activation_status=state_activation_info,
            profile_age_days=profile.profile_age_days,
            message_count=profile.message_count
        )
        print(f"\n✅ Logged to chat_logs.xlsx")
    except Exception as logging_error:
        print(f"\n⚠️  Logging failed: {logging_error}")








# ==========================================================
# MAIN INTERACTION LOOP
# ==========================================================

print("="*100)
print("INSTRUCTIONS:")
print("="*100)
print("• Enter a message to analyze")
print("• Type 'profile' to view full profile with advanced state info")
print("• Type 'history' to see emotion frequency analysis")
print("• Type 'states' to see current activation status")
print("• Type 'exit' to quit\n")

total_messages_processed = 0
current_user_id = "test_user"

while True:
    try:
        # Measure input time
        input_start_time = time.perf_counter()
        user_command = input("💬 You: ").strip()
        input_end_time = time.perf_counter()
        
        if not user_command:
            continue
        
        # Handle commands
        if user_command.lower() == 'exit':
            print("\n👋 Goodbye!\n")
            break
        
        if user_command.lower() == 'profile':
            # Get profile from orchestrator's user_profiles dict
            user_profile = orchestrator.user_profiles.get(current_user_id)
            if user_profile:
                user_profile.display_profile(top_n=5)
            else:
                print("⚠️  No profile yet. Send a message first.\n")
            continue
        
        if user_command.lower() == 'history':
            user_profile = orchestrator.user_profiles.get(current_user_id)
            if user_profile:
                display_frequency_analysis(user_profile)
            else:
                print("⚠️  No profile yet. Send a message first.\n")
            continue
        
        if user_command.lower() == 'states':
            user_profile = orchestrator.user_profiles.get(current_user_id)
            if user_profile:
                display_activation_status(user_profile)
                display_current_states(user_profile)
                print()
            else:
                print("⚠️  No profile yet. Send a message first.\n")
            continue
        
        # Process message
        total_messages_processed += 1
        message_writing_time = input_end_time - input_start_time
        
        print(f"\n{'─'*100}")
        print(f"Message #{total_messages_processed}")
        print(f"{'─'*100}\n")
        
        # Call orchestrator to process message
        analysis_result = orchestrator.process_user_message(
            user_id=current_user_id,
            message=user_command,
            reference_date=datetime.now(),
            writing_time=message_writing_time
        )
        
        # Critical check: ensure analysis is not None
        if analysis_result is None:
            print("❌ ERROR: orchestrator.process_user_message() returned None!")
            print("This should not happen after our initial check.")
            print("Please check your orchestrator.py implementation.")
            continue
        
        # ==========================================================
        # DISPLAY ANALYSIS RESULTS
        # ==========================================================
        
        # 1. EMOTIONS DETECTED
        print("😊 EMOTIONS DETECTED:")
        display_emotions(analysis_result.emotions_detected, top_n=5)
        
        # 2. TEMPORAL REFERENCES
        print("\n⏰ TEMPORAL REFERENCES:")
        display_temporal_references(analysis_result.temporal_references)
        
        # 3. WRITING TIME
        print(f"\n⌨️  Writing time: {message_writing_time:.4f} seconds")
        
        # 4. IMPACT SCORE
        print(f"\n💥 IMPACT SCORE: {analysis_result.impact_score:.4f}", end="")
        if analysis_result.impact_score > 0.8:
            print(" 🔴 HIGH")
        elif analysis_result.impact_score > 0.4:
            print(" 🟡 MEDIUM")
        else:
            print(" 🟢 LOW")
        
        # 5. ANALYSIS SUMMARY
        if hasattr(analysis_result, 'analysis_summary') and analysis_result.analysis_summary:
            print(f"\n📌 Summary: {analysis_result.analysis_summary}")
        
        # 6. GET PROFILE
        user_profile = orchestrator.user_profiles.get(current_user_id)
        
        if user_profile:
            # 7. STATE ACTIVATION STATUS
            display_activation_status(user_profile)
            
            # 8. CURRENT EMOTIONAL STATE
            display_current_states(user_profile)
            
            # 9. LOG TO EXCEL
            log_to_excel(logger, user_profile, analysis_result, user_command)
        else:
            print("\n⚠️  Profile not created properly")
        
        print(f"\n{'─'*100}\n")
        
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
        break
    except Exception as processing_error:
        print(f"\n❌ ERROR: {processing_error}\n")
        import traceback
        traceback.print_exc()
        print()

print("="*100)
print("TEST COMPLETE")
print("="*100)