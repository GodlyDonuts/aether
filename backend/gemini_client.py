"""
Project AXON Gemini 3.0 Client
Wrapper for Google's Generative AI SDK.
"""

from google import genai
from google.genai import types
from backend.config import settings


class GeminiClient:
    """Client for interacting with Gemini 3.0 models."""
    
    def __init__(self):
        """Initialize the Gemini client with API key."""
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    
    async def generate(
        self,
        prompt: str,
        model: str = None,
        system_instruction: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        Generate a response from Gemini.
        
        Args:
            prompt: The user prompt
            model: Model to use (defaults to PULSE_MONITOR_MODEL)
            system_instruction: Optional system instruction
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
            
        Returns:
            Generated text response
        """
        model = model or settings.PULSE_MONITOR_MODEL
        
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        if system_instruction:
            config.system_instruction = system_instruction
        
        response = await self.client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )
        
        return response.text
    
    async def test_connection(self) -> dict:
        """Test the Gemini API connection."""
        try:
            response = await self.generate(
                prompt="Say 'AXON online' if you can hear me.",
                temperature=0.1,
                max_tokens=50,
            )
            return {
                "status": "connected",
                "model": settings.PULSE_MONITOR_MODEL,
                "response": response.strip(),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }


# Singleton instance
gemini = GeminiClient()
