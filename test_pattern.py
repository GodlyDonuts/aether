import httpx
import time
import json
import sys

BASE_URL = "http://localhost:8000"

def test_pattern():
    print("🚀 Starting Pattern Detection Test")
    
    # 1. Health Check
    try:
        resp = httpx.get(f"{BASE_URL}/health", timeout=5.0)
        resp.raise_for_status()
        print("✅ Server is online")
    except Exception as e:
        print(f"❌ Server is offline: {e}")
        return

    # 2. Sequential Calculus Questions
    questions = [
        "What is the integral of x^2?",
        "Solve the integral of sin(x)cos(x)",
        "What about the integral of e^x * x?",
        "Now solve integral of 1/(1+x^2)",
        "And the integral of ln(x)?"
    ]
    
    session_id = None
    
    for i, q in enumerate(questions, 1):
        print(f"\n📝 Question {i}: {q}")
        
        payload = {"message": q}
        if session_id:
            payload["session_id"] = session_id
            
        try:
            resp = httpx.post(f"{BASE_URL}/chat", json=payload, timeout=60.0)
            resp.raise_for_status()
            data = resp.json()
            
            session_id = data["session_id"]
            analysis = data.get("intent_analysis", {})
            nudge = data.get("nudge_injected", False)
            
            print(f"   Intent: {analysis.get('bucket')}")
            print(f"   Struggle: {analysis.get('struggle')}")
            print(f"   Propensity: {analysis.get('propensity')}")
            print(f"   Entities: {analysis.get('entities')}")
            
            if nudge:
                print(f"   🎯 NUDGE TRIGGERED! Details: {data.get('nudge_details')}")
                print(f"   ✨ Response snippet: {data['response'][-100:]}")
            else:
                print("   ⚪ No nudge yet")
                
            # Wait a bit between requests to let async tasks process if needed
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Request failed: {e}")
            break

if __name__ == "__main__":
    test_pattern()
