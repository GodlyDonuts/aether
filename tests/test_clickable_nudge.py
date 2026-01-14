import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import IntentAnalysis, IntentBucket, StruggleState
from backend.axon_registry import axon_registry

async def test_clickable_nudge():
    print("🔗 Testing Clickable Nudge Generation...\n")
    
    # Mock Analysis for a known fallback case (plumbing) to ensure we get a result
    analysis = IntentAnalysis(
        intent_bucket=IntentBucket.TRANSACTIONAL,
        struggle_state=StruggleState.MILD,
        propensity_score=80,
        detected_entities=["faucet", "repair", "kit"],
        reasoning="Test"
    )
    
    # Run find_nudge
    # Note: If SERP API key is missing or invalid, it will fallback to mock data which now has links
    nudge = await axon_registry.find_nudge(analysis)
    
    if nudge:
        print(f"📦 Product: {nudge.product_name}")
        print(f"🔗 Link: {nudge.link}")
        print(f"💬 Text: {nudge.nudge_text}")
        
        # Verify markdown link format
        if f"[{nudge.product_name}]({nudge.link})" in nudge.nudge_text or \
           f"[**{nudge.product_name}**]({nudge.link})" in nudge.nudge_text:
            print("✅ Markdown Link Generation: PASSED")
        else:
            print("❌ Markdown Link Generation: FAILED configuration")
            
        # Verify link presence
        if nudge.link:
            print("✅ Link Field Population: PASSED")
        else:
            print("❌ Link Field Population: FAILED (None)")
            
    else:
        print("❌ No nudge generated.")

if __name__ == "__main__":
    asyncio.run(test_clickable_nudge())
