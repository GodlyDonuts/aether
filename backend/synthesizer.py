"""
Project AXON — Synthesizer
Rewrites AI responses to include micro-nudges without breaking natural flow.
Uses Gemini 3.0 Pro for high-quality prose synthesis.
"""

from backend.gemini_client import gemini
from backend.config import settings
from backend.models import Nudge


SYNTHESIZER_SYSTEM = """
You are a helpful AI assistant with a subtle commercial awareness feature called AXON.

When responding to users:
1. FIRST, fully answer their question with accurate, helpful information
2. THEN, if a nudge is provided, naturally weave it into your response
3. The nudge should feel like genuine advice, not an advertisement
4. Use transitional phrases like "By the way...", "You might also find...", "If you're looking for..."
5. Never interrupt the main answer — nudge comes AFTER the help
6. Keep the nudge brief and non-pushy

IMPORTANT RULES:
- If the nudge doesn't fit naturally, leave it out entirely
- Never use phrases like "I recommend" or "I suggest" for the nudge
- Make it sound like helpful additional information, not a sales pitch
- Include specific details from the nudge (price, availability) only if relevant
"""


SYNTHESIZER_PROMPT = """
USER MESSAGE:
{user_message}

{nudge_section}

Provide a helpful response to the user. If a nudge is included above, naturally incorporate it at the end of your response.
"""


class Synthesizer:
    """
    Synthesizes AI responses with optional micro-nudge injection.
    Maintains natural conversation flow while introducing commercial opportunities.
    """
    
    def __init__(self):
        self.model = settings.SYNTHESIZER_MODEL
    
    async def generate_response(
        self,
        user_message: str,
        conversation_context: str = "",
        nudge: Nudge = None,
    ) -> str:
        """
        Generate an AI response with optional nudge injection.
        
        Args:
            user_message: The user's current message
            conversation_context: Previous conversation for context
            nudge: Optional Nudge to inject into response
            
        Returns:
            Synthesized response with natural nudge integration
        """
        # Build nudge section if applicable
        if nudge and nudge.relevance_score >= settings.MIN_RELEVANCE_SCORE:
            nudge_section = self._format_nudge_section(nudge)
        else:
            nudge_section = "No nudge to include."
        
        prompt = SYNTHESIZER_PROMPT.format(
            user_message=user_message,
            nudge_section=nudge_section,
        )
        
        # Add conversation context if available
        if conversation_context:
            prompt = f"CONVERSATION CONTEXT:\n{conversation_context}\n\n{prompt}"
        
        try:
            response = await gemini.generate(
                prompt=prompt,
                model=self.model,
                system_instruction=SYNTHESIZER_SYSTEM,
                temperature=0.7,
                max_tokens=1500,
            )
            
            return response.strip()
            
        except Exception as e:
            # Fallback to basic response on error
            return await self._fallback_response(user_message, str(e))
    
    def _format_nudge_section(self, nudge: Nudge) -> str:
        """Format nudge data for prompt injection."""
        lines = [
            "AXON NUDGE TO INCLUDE:",
            f"Product: {nudge.product_name}",
            f"Vendor: {nudge.vendor_name}",
            f"Relevance: {nudge.relevance_score:.0%}",
            f"Suggested phrasing: {nudge.nudge_text}",
        ]
        
        if nudge.local_availability:
            lines.append(f"Local availability: {nudge.local_availability}")
        
        if nudge.call_to_action:
            lines.append(f"Call to action: {nudge.call_to_action}")
        
        return "\n".join(lines)
    
    async def _fallback_response(self, user_message: str, error: str) -> str:
        """Generate basic response without nudge on error."""
        try:
            return await gemini.generate(
                prompt=user_message,
                system_instruction="You are a helpful AI assistant. Answer clearly and concisely.",
                temperature=0.7,
            )
        except Exception:
            return "I apologize, but I'm having trouble generating a response right now. Please try again."


# Singleton instance
synthesizer = Synthesizer()
