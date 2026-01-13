
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.pulse_monitor import pulse_monitor
from backend.models import Message

async def verify_pulse_monitor():
    print("--- Starting Pulse Monitor Verification ---")
    
    # Simulate a conversation showing high commercial intent ("SHOPPING" / "GRINDING")
    messages = [
        Message(role="user", content="I need a new laptop for gaming."),
        Message(role="assistant", content="What is your budget and what games do you play?"),
        Message(role="user", content="Around $2000. I play Cyberpunk and Call of Duty."),
        Message(role="assistant", content="You should look for something with an RTX 4070 or 4080."),
        Message(role="user", content="What are the best options right now? I want to buy one this week."),
    ]
    
    print(f"Analyzing {len(messages)} messages...")
    
    try:
        analysis = await pulse_monitor.analyze(messages)
        
        print("\n--- Analysis Result ---")
        print(f"Intent Bucket: {analysis.intent_bucket}")
        print(f"Propensity Score: {analysis.propensity_score}")
        print(f"Recommended Category: {analysis.recommended_category}")
        print(f"Reasoning: {analysis.reasoning}")
        
        print("\n--- Grounding Data (SERP) ---")
        if analysis.grounding_data:
            print("SUCCESS: Grounding data found!")
            print(analysis.grounding_data)
        else:
            print("WARNING: No grounding data found. Propensity might be too low or SERP key missing.")
            
    except Exception as e:
        print(f"ERROR: Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_pulse_monitor())
