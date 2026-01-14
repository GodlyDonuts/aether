import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.pulse_monitor import pulse_monitor
from backend.axon_registry import axon_registry
from backend.synthesizer import synthesizer
from backend.models import Message, ConversationState
from backend.config import settings

async def reproduce():
    print("🐞 Reproducing Missing Nudge Issue...\n")
    
    # Simulate the conversation state
    messages = []
    
    conversation_steps = [
        "I need a plumbing wrench",
        "Faucet Wrenches sound nice",
        "I just need a basic faucet wrench"
    ]
    
    for i, user_text in enumerate(conversation_steps):
        print(f"--- Turn {i+1} ---")
        print(f"User: {user_text}")
        
        # Add user message
        messages.append(Message(role="user", content=user_text))
        
        # 1. Pulse Monitor
        analysis = await pulse_monitor.analyze(messages)
        print(f"Creating Analysis... {analysis.intent_bucket.value}, Score: {analysis.propensity_score}")
        print(f"Entities: {analysis.detected_entities}")
        
        # 2. Check Trigger
        should_trigger = pulse_monitor.should_trigger_nudge(analysis)
        print(f"Should Trigger? {should_trigger}")
        
        nudge = None
        if should_trigger:
            # 3. Registry
            nudge = await axon_registry.find_nudge(analysis)
            if nudge:
                print(f"Registry found nudge: {nudge.product_name} (Relevance: {nudge.relevance_score})")
            else:
                print("Registry returned None")
        
        # 4. Synthesizer check (checking filtering logic)
        if nudge:
            if nudge.relevance_score >= settings.MIN_RELEVANCE_SCORE:
                print("Synthesizer WOULD include this nudge.")
            else:
                print(f"Synthesizer WOULD DROP this nudge (Score {nudge.relevance_score} < {settings.MIN_RELEVANCE_SCORE})")
        
        # Add AI placeholder response to keep history realistic
        messages.append(Message(role="assistant", content="Placeholder response."))
        print("\n")

if __name__ == "__main__":
    asyncio.run(reproduce())
