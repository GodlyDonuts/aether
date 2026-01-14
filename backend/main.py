"""
Project AXON — Main FastAPI Application
The Semantic Monetization Layer for Generative Intelligence
"""

import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from backend.config import settings
from backend.gemini_client import gemini
from backend.models import ConversationState, IntentAnalysis, Nudge
from backend.pulse_monitor import pulse_monitor
from backend.axon_registry import axon_registry
from backend.synthesizer import synthesizer

# Validate configuration on startup
settings.validate()

app = FastAPI(
    title="Project AXON",
    description="The Semantic Monetization Layer for Generative Intelligence",
    version="0.2.0",
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
        "version": "0.2.0",
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
    1. Pulse Monitor analyzes intent
    2. If conversion threshold met, AXON Registry finds matching ad
    3. Synthesizer generates response with optional nudge
    """
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id not in sessions:
        sessions[session_id] = ConversationState(session_id=session_id)
    
    session = sessions[session_id]
    session.add_message("user", request.message)
    
    try:
        # Step 1: Pulse Monitor - Analyze intent
        intent_analysis = await pulse_monitor.analyze(session.messages)
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
            session.total_revenue_generated += 2.50
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            intent_analysis={
                "bucket": intent_analysis.intent_bucket.value,
                "struggle": intent_analysis.struggle_state.value,
                "propensity": intent_analysis.propensity_score,
                "entities": intent_analysis.detected_entities,
            },
            nudge_injected=nudge is not None,
            nudge_details={
                "product": nudge.product_name,
                "vendor": nudge.vendor_name,
                "relevance": f"{nudge.relevance_score:.0%}",
            } if nudge else None,
        )
        
    except Exception as e:
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
    """Get overall AXON analytics."""
    total_sessions = len(sessions)
    total_nudges = sum(len(s.nudges_shown) for s in sessions.values())
    total_revenue = sum(s.total_revenue_generated for s in sessions.values())
    
    return {
        "total_sessions": total_sessions,
        "total_nudges_shown": total_nudges,
        "total_revenue_generated": f"${total_revenue:.2f}",
        "average_nudges_per_session": total_nudges / total_sessions if total_sessions > 0 else 0,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)


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
