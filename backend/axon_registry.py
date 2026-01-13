"""
Project AXON — AXON Registry
Bridges detected intent with ad inventory using SERP API.
Fetches relevant ads and products based on user intent.
"""

import os
import httpx
from typing import Optional
from backend.models import IntentAnalysis, Nudge


class AXONRegistry:
    """
    Real-time bridge to advertising data via SERP API.
    Matches user intent to relevant commercial opportunities.
    """
    
    def __init__(self):
        self.api_key = os.getenv("SERP_API_KEY", "")
        self.base_url = "https://serpapi.com/search"
    
    async def find_nudge(
        self,
        analysis: IntentAnalysis,
        location: str = "United States",
    ) -> Optional[Nudge]:
        """
        Find the best matching ad/product for the detected intent.
        
        Args:
            analysis: Intent analysis from Pulse Monitor
            location: User's location for local results
            
        Returns:
            Nudge with product recommendation or None
        """
        if not analysis.detected_entities:
            return None
        
        # Build search query from detected entities
        query = " ".join(analysis.detected_entities[:3])
        
        # Add commercial intent modifiers based on struggle state
        if analysis.struggle_state.value in ["moderate", "high"]:
            query += " best buy"
        
        try:
            result = await self._search_shopping(query, location)
            
            if result:
                return self._create_nudge(result, analysis)
            
            return None
            
        except Exception as e:
            print(f"AXON Registry error: {e}")
            return None
    
    async def _search_shopping(
        self,
        query: str,
        location: str,
    ) -> Optional[dict]:
        """
        Search for shopping results via SERP API.
        Falls back to mock data if no API key.
        """
        if not self.api_key:
            # Return mock data for development/demo
            return self._get_mock_result(query)
        
        params = {
            "engine": "google_shopping",
            "q": query,
            "location": location,
            "api_key": self.api_key,
            "num": 5,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Get the most relevant shopping result
            results = data.get("shopping_results", [])
            if results:
                return results[0]
            
            return None
    
    def _get_mock_result(self, query: str) -> dict:
        """
        Return mock shopping data for demo purposes.
        Simulates SERP API response structure.
        """
        query_lower = query.lower()
        
        # Domain-specific mock responses
        if any(word in query_lower for word in ["faucet", "plumbing", "wrench", "pipe"]):
            return {
                "title": "Delta Faucet Repair Kit - Complete Set",
                "source": "Home Depot",
                "price": "$24.99",
                "rating": 4.7,
                "reviews": 2847,
                "link": "https://homedepot.com/delta-repair-kit",
                "local_availability": "In stock at nearby store",
            }
        
        if any(word in query_lower for word in ["calculus", "math", "tutoring", "study"]):
            return {
                "title": "Brilliant.org Premium - Learn Calculus Interactively",
                "source": "Brilliant",
                "price": "$12.99/mo",
                "rating": 4.9,
                "reviews": 15420,
                "link": "https://brilliant.org/calculus",
                "local_availability": None,
            }
        
        if any(word in query_lower for word in ["laptop", "computer", "macbook", "coding"]):
            return {
                "title": "MacBook Air M3 - 15 inch",
                "source": "Apple Store",
                "price": "$1,299",
                "rating": 4.8,
                "reviews": 8932,
                "link": "https://apple.com/macbook-air",
                "local_availability": "Available for pickup today",
            }
        
        # Generic fallback
        return {
            "title": f"Top Rated {query.title()} Solution",
            "source": "Amazon",
            "price": "$29.99",
            "rating": 4.5,
            "reviews": 1250,
            "link": "https://amazon.com/search",
            "local_availability": "Prime delivery available",
        }
    
    def _create_nudge(
        self,
        result: dict,
        analysis: IntentAnalysis,
    ) -> Nudge:
        """Convert SERP result to Nudge object."""
        # Calculate relevance based on intent match
        base_relevance = 0.6
        
        # Boost for commercial/transactional intent
        if analysis.intent_bucket.value in ["commercial", "transactional"]:
            base_relevance += 0.15
        
        # Boost for high struggle state
        if analysis.struggle_state.value == "high":
            base_relevance += 0.15
        elif analysis.struggle_state.value == "moderate":
            base_relevance += 0.10
        
        relevance = min(base_relevance, 1.0)
        
        # Build natural nudge text
        nudge_text = self._generate_nudge_text(result, analysis)
        
        return Nudge(
            product_name=result.get("title", "Recommended Product"),
            vendor_name=result.get("source", "Online Retailer"),
            relevance_score=relevance,
            nudge_text=nudge_text,
            call_to_action=f"Check it out at {result.get('source', 'the store')}",
            local_availability=result.get("local_availability"),
        )
    
    def _generate_nudge_text(self, result: dict, analysis: IntentAnalysis) -> str:
        """Generate natural language nudge text."""
        product = result.get("title", "this product")
        source = result.get("source", "online")
        price = result.get("price", "")
        rating = result.get("rating", 0)
        local = result.get("local_availability", "")
        
        # Build contextual nudge based on struggle state
        if analysis.struggle_state.value == "high":
            prefix = "By the way, since you're working through this"
        elif analysis.struggle_state.value == "moderate":
            prefix = "If you'd like a little help"
        else:
            prefix = "You might also find this useful"
        
        nudge = f"{prefix}, **{product}** from {source}"
        
        if price:
            nudge += f" ({price})"
        
        if rating and rating >= 4.5:
            nudge += f" has excellent reviews ({rating}★)"
        
        if local:
            nudge += f". {local}."
        else:
            nudge += "."
        
        return nudge


# Singleton instance
axon_registry = AXONRegistry()
