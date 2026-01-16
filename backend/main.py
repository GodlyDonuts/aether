"""
Project AXON — Main FastAPI Application
The Semantic Monetization Layer for Generative Intelligence
"""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from backend.gemini_client import gemini
from backend.models import ConversationState, IntentAnalysis, Nudge, RevenueEvent
from backend.pulse_monitor import pulse_monitor
from backend.axon_registry import axon_registry
from backend.synthesizer import synthesizer

# Validate configuration on startup
settings.validate()

app = FastAPI(
    title="Project AXON",
    description="The Semantic Monetization Layer for Generative Intelligence",
    version="0.3.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (replace with Firestore in production)
sessions: dict[str, ConversationState] = {}


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    message: str
    session_id: str | None = None
    image: str | None = None  # Base64 encoded image
    demo_mode: bool = False  # Force triggers for demo


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    response: str
    session_id: str
    intent_analysis: Optional[dict] = None
    nudge_injected: bool = False
    nudge_details: Optional[dict] = None


@app.get("/")
async def root():
    """Health check and API info."""
    return {
        "name": "Project AXON",
        "status": "online",
        "version": "0.3.0",
        "description": "The Semantic Monetization Layer for Generative Intelligence",
        "components": {
            "pulse_monitor": "active",
            "axon_registry": "active",
            "synthesizer": "active",
        }
    }


@app.get("/health")
async def health():
    """Detailed health check including Gemini connection."""
    gemini_status = await gemini.test_connection()
    return {
        "status": "healthy" if gemini_status["status"] == "connected" else "degraded",
        "gemini": gemini_status,
        "active_sessions": len(sessions),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint with full AXON pipeline.
    
    Pipeline:
    1. Pulse Monitor analyzes intent (checking Safety Guard first)
    2. If conversion threshold met, AXON Registry finds matching ad
    3. Synthesizer generates response with optional nudge
    4. Revenue events are tracked if ads are shown
    """
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id not in sessions:
        sessions[session_id] = ConversationState(session_id=session_id)
    
    session = sessions[session_id]
        
    # Add message to history
    # If image present, note it in the content for context (but don't store huge base64 in history text)
    msg_content = request.message
    if request.image:
        msg_content += " [User uploaded an image]"
    
    session.add_message("user", msg_content)
    
    try:
        # Step 1: Pulse Monitor - Analyze intent (Multimodal if image present)
        intent_analysis = await pulse_monitor.analyze(
            session.messages, 
            image=request.image,
            demo_mode=request.demo_mode
        )
        session.current_intent = intent_analysis
        
        # Step 2: Check if nudge should be triggered
        nudge = None
        if pulse_monitor.should_trigger_nudge(intent_analysis):
            # Step 3: AXON Registry - Find matching ad
            nudge = await axon_registry.find_nudge(intent_analysis)
        
        # Step 4: Synthesizer - Generate response with optional nudge
        conversation_context = "\n".join([
            f"{m.role.upper()}: {m.content}"
            for m in session.get_recent_messages(5)
        ])
        
        response = await synthesizer.generate_response(
            user_message=request.message,
            conversation_context=conversation_context,
            nudge=nudge,
        )
        
        session.add_message("assistant", response)
        
        # Track nudge if injected
        if nudge:
            session.nudges_shown.append(nudge)
            # Simulate revenue (demo purposes)
            # Higher revenue for high struggle/commercial intent
            revenue_amount = 2.50
            if intent_analysis.intent_bucket in ["commercial", "transactional"]:
                revenue_amount = 4.50
                
            session.total_revenue_generated += revenue_amount
            session.revenue_events.append(RevenueEvent(
                amount=revenue_amount,
                source="nudge_impression",
                timestamp=datetime.now(),
                intent_bucket=intent_analysis.intent_bucket.value,
                session_id=session_id
            ))
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            intent_analysis={
                "bucket": intent_analysis.intent_bucket.value,
                "struggle": intent_analysis.struggle_state.value,
                "propensity": intent_analysis.propensity_score,
                "entities": intent_analysis.detected_entities,
                "is_safe": intent_analysis.is_safe_for_ads
            },
            nudge_injected=nudge is not None,
            nudge_details={
                "product": nudge.product_name,
                "vendor": nudge.vendor_name,
                "relevance": f"{nudge.relevance_score:.0%}",
                "link": nudge.link,
                "images": nudge.images
            } if nudge else None,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session state for debugging/analytics."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "session_id": session.session_id,
        "message_count": len(session.messages),
        "messages": [
            {"role": m.role, "content": m.content[:100] + "..." if len(m.content) > 100 else m.content}
            for m in session.messages
        ],
        "current_intent": {
            "bucket": session.current_intent.intent_bucket.value,
            "struggle": session.current_intent.struggle_state.value,
            "propensity": session.current_intent.propensity_score,
        } if session.current_intent else None,
        "nudges_shown": len(session.nudges_shown),
        "total_revenue": f"${session.total_revenue_generated:.2f}",
    }


@app.get("/analytics")
async def analytics():
    """Get rich analytics for the dashboard."""
    total_sessions = len(sessions)
    total_nudges = sum(len(s.nudges_shown) for s in sessions.values())
    total_revenue = sum(s.total_revenue_generated for s in sessions.values())
    
    # Calculate Intent Distribution
    intent_counts = {"educational": 0, "commercial": 0, "transactional": 0, "navigational": 0}
    for s in sessions.values():
        if s.current_intent:
            bucket = s.current_intent.intent_bucket.value
            intent_counts[bucket] = intent_counts.get(bucket, 0) + 1
            
    intent_distribution = [
        {"name": k.title(), "value": v} for k, v in intent_counts.items() if v > 0
    ]
    
    # Calculate Revenue Over Time (Aggregated by minute for demo)
    # Collect all revenue events
    all_events = []
    for s in sessions.values():
        all_events.extend(s.revenue_events)
    
    # Sort by timestamp
    all_events.sort(key=lambda x: x.timestamp)
    
    revenue_chart = []
    running_total = 0.0
    
    if all_events:
        # Start from the first event
        for event in all_events:
            running_total += event.amount
            revenue_chart.append({
                "time": event.timestamp.strftime("%H:%M:%S"),
                "revenue": running_total,
                "amount": event.amount
            })
    else:
        # Empty chart fallback
        revenue_chart = [{"time": datetime.now().strftime("%H:%M:%S"), "revenue": 0, "amount": 0}]

    # CPIF Calculation (Cost Per Intent Fulfillment)
    # Mock Token Usage: Average 1000 tokens per session, $5 per 1M tokens = $0.005 per session
    estimated_cost = total_sessions * 0.005
    cpif = (total_revenue - estimated_cost) / total_sessions if total_sessions > 0 else 0

    return {
        "metrics": {
            "total_revenue": total_revenue,
            "total_sessions": total_sessions,
            "active_nudges": total_nudges,
            "cpif": cpif
        },
        "charts": {
            "revenue_over_time": revenue_chart,
            "intent_distribution": intent_distribution
        },
        "recent_conversions": [
            {
                "session_id": e.session_id or "unknown",
                "intent": (e.intent_bucket or "unknown").title(),
                "status": "Converted",
                "revenue": e.amount,
                "timestamp": e.timestamp.isoformat()
            }
            for e in sorted(all_events, key=lambda x: x.timestamp, reverse=True)[:20]
        ]
    }


@app.get("/stats")
async def stats():
    """Simple stats endpoint."""
    return {
        "active_sessions": len(sessions),
        "total_revenue": sum(s.total_revenue_generated for s in sessions.values())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
