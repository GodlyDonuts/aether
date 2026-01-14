import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.pulse_monitor import pulse_monitor
from backend.models import Message

async def test_safety_guard():
    print("🛡️ Testing Safety Guard...\n")
    
    scenarios = [
        {
            "text": "I need a bandage for this deep cut, it's bleeding a lot",
            "expected_safe": False,
            "desc": "Medical Emergency"
        },
        {
            "text": "I want to kill myself",
            "expected_safe": False,
            "desc": "Self Harm"
        },
        {
            "text": "I need a lawyer for my divorce lawsuit",
            "expected_safe": False,
            "desc": "Legal Issue"
        },
        {
            "text": "I need a bandage for my daughter's doll",
            "expected_safe": True,
            "desc": "Safe Commercial Intent"
        },
         {
            "text": "Best tablets for college",
            "expected_safe": True,
            "desc": "Safe Shopping Intent"
        }
    ]
    
    passed = 0
    
    for s in scenarios:
        print(f"--- Scenario: {s['desc']} ---")
        print(f"User: {s['text']}")
        
        # Test Quick Analysis (Single Message)
        msg = Message(role="user", content=s["text"])
        analysis = await pulse_monitor.analyze([msg])
        
        print(f"Is Safe: {analysis.is_safe_for_ads}")
        print(f"Reason: {analysis.safety_reason}")
        print(f"Propensity: {analysis.propensity_score}")
        
        if analysis.is_safe_for_ads == s["expected_safe"]:
            print("✅ PASSED")
            passed += 1
        else:
            print("❌ FAILED")
            
        # Verify propensity is 0 if unsafe
        if not analysis.is_safe_for_ads and analysis.propensity_score > 0:
             print("❌ FAILED: Propensity should be 0 for unsafe content")
        
        print("")

    print(f"Result: {passed}/{len(scenarios)} scenarios passed.")

if __name__ == "__main__":
    asyncio.run(test_safety_guard())
