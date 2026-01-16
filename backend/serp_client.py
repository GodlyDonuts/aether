import httpx
import json
from typing import Optional, List, Dict, Any
from backend.config import settings

class SerpClient:
    """
    Client for interacting with the SERP API (SerpApi).
    Used to ground commercial intent with real-time search data.
    """
    BASE_URL = "https://serpapi.com/search"

    def __init__(self):
        self.api_key = settings.SERP_API_KEY

    async def search(self, query: str, search_type: str = "search", location: str = "United States") -> Dict[str, Any]:
        """
        Perform a search via SerpApi.
        
        Args:
            query: The search query.
            search_type: 'search' (web) or 'shopping'.
            location: Geo-location for the search (e.g., 'United States', 'New York, NY')
            
        Returns:
            Dict containing search results.
        """
        if not self.api_key:
            return {"error": "SERP_API_KEY not configured"}

        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google_shopping" if search_type == "shopping" else "google",
            "location": location,
            "num": 5, # We only need top results for grounding
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.BASE_URL, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"SERP API Error: {e}")
                return {"error": str(e)}

    def extract_shopping_data(self, char_limit: int = 1000, data: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Extract relevant shopping info from raw SERP response.
        Returns a dict with formatted string and extracted images.
        """
        if "error" in data:
            return {"text": "", "images": []}

        results_text = []
        images = []
        
        # Handle Shopping Results
        if "shopping_results" in data:
            for item in data["shopping_results"][:3]:
                title = item.get("title", "Unknown Product")
                price = item.get("price", "N/A")
                merchant = item.get("source", "Unknown Seller")
                rating = item.get("rating", "")
                reviews = item.get("reviews", "")
                thumbnail = item.get("thumbnail")
                
                if thumbnail:
                    images.append(thumbnail)
                
                entry = f"- {title} ({price}) from {merchant}"
                if rating:
                    entry += f" [{rating} stars"
                    if reviews:
                        entry += f" ({reviews} reviews)"
                    entry += "]"
                
                results_text.append(entry)
        
        # Handle Organic Results (fallback if used for intent verification)
        elif "organic_results" in data:
            for item in data["organic_results"][:3]:
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                results_text.append(f"- {title}: {snippet}")

        return {
            "text": "\n".join(results_text)[:char_limit],
            "images": images[:2] # Limit to 2 real images
        }

# Singleton
serp_client = SerpClient()
