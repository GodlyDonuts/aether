"""
Project AXON — Main FastAPI Application
The Semantic Monetization Layer for Generative Intelligence
"""

import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from backend.gemini_client import gemini
from backend.models import ConversationState, AXONResponse

# Validate configuration on startup
settings.validate()

app = FastAPI(
    title="Project AXON",
    description="The Semantic Monetization Layer for Generative Intelligence",
    version="0.1.0",
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


@app.get("/")
async def root():
    """Health check and API info."""
    return {
        "name": "Project AXON",
        "status": "online",
        "version": "0.1.0",
        "description": "The Semantic Monetization Layer for Generative Intelligence",
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
    Main chat endpoint.
    Processes user message through AXON pipeline.
    """
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id not in sessions:
        sessions[session_id] = ConversationState(session_id=session_id)
    
    session = sessions[session_id]
    session.add_message("user", request.message)
    
    # For Phase 0, just pass through to Gemini
    # Phase 1+ will add Pulse Monitor, Synthesizer, etc.
    try:
        response = await gemini.generate(
            prompt=request.message,
            system_instruction="You are a helpful AI assistant. Answer the user's question clearly and concisely.",
            temperature=0.7,
        )
        
        session.add_message("assistant", response)
        
        return ChatResponse(
            response=response,
            session_id=session_id,
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
        "current_intent": session.current_intent,
        "nudges_shown": len(session.nudges_shown),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
