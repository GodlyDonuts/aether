"""
Project AXON Data Models
Pydantic models for Intent Graph, Nudges, and Conversation State.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class IntentBucket(str, Enum):
    """Classification of user intent type."""
    EDUCATIONAL = "educational"
    COMMERCIAL = "commercial"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"


class StruggleState(str, Enum):
    """User's current struggle level."""
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    HIGH = "high"


class Message(BaseModel):
    """A single message in the conversation."""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class IntentAnalysis(BaseModel):
    """Result of Pulse Monitor analysis."""
    intent_bucket: IntentBucket
    struggle_state: StruggleState
    propensity_score: int = Field(..., ge=0, le=100)
    detected_entities: list[str] = Field(default_factory=list)
    recommended_category: Optional[str] = None
    grounding_data: Optional[str] = None
    reasoning: Optional[str] = None
    is_safe_for_ads: bool = True
    safety_reason: Optional[str] = None


class Nudge(BaseModel):
    """A micro-nudge to be injected into the response."""
    product_name: str
    vendor_name: str
    relevance_score: float = Field(..., ge=0, le=1)
    nudge_text: str
    link: Optional[str] = None
    call_to_action: Optional[str] = None
    local_availability: Optional[str] = None


class ConversationState(BaseModel):
    """Full state of an AXON conversation session."""
    session_id: str
    messages: list[Message] = Field(default_factory=list)
    current_intent: Optional[IntentAnalysis] = None
    nudges_shown: list[Nudge] = Field(default_factory=list)
    total_revenue_generated: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content))
    
    def get_recent_messages(self, count: int = 20) -> list[Message]:
        """Get the last N messages for context."""
        return self.messages[-count:]


class AXONResponse(BaseModel):
    """Response from the AXON system."""
    response: str
    intent_analysis: Optional[IntentAnalysis] = None
    nudge_injected: Optional[Nudge] = None
    session_id: str
