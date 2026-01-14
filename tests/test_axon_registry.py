import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.axon_registry import axon_registry
from backend.models import IntentAnalysis, IntentBucket, StruggleState

async def test_registry():
    print("🚀 Testing AXON Registry...")
    
    # Mock Intent Analysis: "I need a plumbing wrench"
    mock_intent = IntentAnalysis(
        intent_bucket=IntentBucket.TRANSACTIONAL,
        struggle_state=StruggleState.MODERATE,
        propensity_score=85,
        detected_entities=["plumbing wrench", "repair kit"],
        reasoning="User explicitly asked for tools to fix a leak."
    )
    
    print(f"\n📥 Input Intent: {mock_intent.detected_entities}")
    print(f"   Bucket: {mock_intent.intent_bucket.value}")
    print(f"   Struggle: {mock_intent.struggle_state.value}")
    
    # Call Registry
    nudge = await axon_registry.find_nudge(mock_intent)
    
    if nudge:
        print("\n✅ Nudge Generated Successfully!")
        print(f"📦 Product: {nudge.product_name}")
        print(f"🏪 Vendor: {nudge.vendor_name}")
        print(f"🎯 Relevance: {nudge.relevance_score}")
        print(f"💬 Text: {nudge.nudge_text}")
        print(f"🔗 CTA: {nudge.call_to_action}")
    else:
        print("\n❌ No Nudge Generated (Check API key or mock logic)")

if __name__ == "__main__":
    asyncio.run(test_registry())
