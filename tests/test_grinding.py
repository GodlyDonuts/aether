import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.pulse_monitor import pulse_monitor
from backend.axon_registry import axon_registry
from backend.models import Message

async def test_grinding():
    print("🧠 Testing Grinding Pattern Detection...\n")
    
    # Simulate repeated math questions
    conversation = [
        "What is the derivative of sin(x)*cos(x)",
        "What is the derivative of (15x^4)/x^3",
        "Derivative of (2x+4)^4",
        "(7x^2 +6x)^3" # 4th message should definitely trigger
    ]
    
    messages = []
    
    for i, text in enumerate(conversation):
        print(f"--- Turn {i+1} ---")
        print(f"User: {text}")
        
        # Add user message
        messages.append(Message(role="user", content=text))
        
        # Analyze
        analysis = await pulse_monitor.analyze(messages)
        print(f"Pattern: {analysis.intent_bucket.value}, Score: {analysis.propensity_score}")
        print(f"Struggle: {analysis.struggle_state.value}")
        
        # Check Nudge
        if pulse_monitor.should_trigger_nudge(analysis):
            print(">>> NUDGE TRIGGERED! <<<")
            nudge = await axon_registry.find_nudge(analysis)
            if nudge:
                print(f"📦 Recommended: {nudge.product_name}")
                print(f"💬 Text: {nudge.nudge_text}")
            else:
                print("❌ Registry returned None")
        else:
            print("... No nudge yet")
            
        # Add placeholder AI response
        messages.append(Message(role="assistant", content="Here is the solution..."))
        print("\n")

if __name__ == "__main__":
    asyncio.run(test_grinding())
