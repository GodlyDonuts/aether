"""
Project AXON Configuration
Loads environment variables and defines model settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Settings:
    """Application settings loaded from environment."""
    
    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Model Configuration
    # Model Configuration
    PULSE_MONITOR_MODEL: str = "gemini-2.0-flash"  # Using 2.0 Flash as stable base for "3-flash" request
    SYNTHESIZER_MODEL: str = "gemini-2.0-flash"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # AXON Thresholds
    CONVERSION_THRESHOLD: int = 70  # 0-100 score to trigger nudge
    MIN_RELEVANCE_SCORE: float = 0.7  # Minimum ad relevance (70%)
    
    SERP_API_KEY: str = os.getenv("SERP_API_KEY", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required settings are present."""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required. Set it in .env file.")
        if not cls.SERP_API_KEY:
            print("Warning: SERP_API_KEY not found. Search grounding will be disabled.")
        return True


settings = Settings()
