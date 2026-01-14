"""
Project AXON — AXON Registry
Bridges detected intent with ad inventory using SERP API.
Fetches relevant ads and products based on user intent.
"""

from typing import Optional
from backend.models import IntentAnalysis, Nudge
from backend.serp_client import serp_client

class AXONRegistry:
    """
    Real-time bridge to advertising data via SERP API.
    Matches user intent to relevant commercial opportunities.
    """
    
    def __init__(self):
        pass # Dependencies are injected or imported as singletons
    
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
        if analysis.intent_bucket.value == "educational" or analysis.struggle_state.value == "high":
             # For educational struggles, suggest courses or tutoring
             query += " online course tutoring"
        elif analysis.struggle_state.value in ["moderate", "high"]:
            query += " best buy"
        
        try:
            # Use shared SerpClient for the actual API call
            data = await serp_client.search(query, search_type="shopping", location=location)
            
            # Check for valid results
            if not data or "error" in data:
                # Fallback to mock data if API fails or not configured
                mock_result = self._get_mock_result(query)
                return self._create_nudge(mock_result, analysis)
                
            shopping_results = data.get("shopping_results", [])
            
            if shopping_results:
                # Use the top result
                best_match = shopping_results[0]
                return self._create_nudge(best_match, analysis)
            
            return None
            
        except Exception as e:
            print(f"AXON Registry error: {e}")
            return None
    
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

        # Extract link
        link = result.get("product_link") or result.get("link")
        
        # Build natural nudge text (pass link for formatting)
        nudge_text = self._generate_nudge_text(result, analysis, link)
        
        return Nudge(
            product_name=result.get("title", "Recommended Product"),
            vendor_name=result.get("source", "Online Retailer"),
            relevance_score=relevance,
            nudge_text=nudge_text,
            link=link,
            call_to_action=f"Check it out at {result.get('source', 'the store')}",
            local_availability=result.get("local_availability", ""),
        )
    
    def _generate_nudge_text(self, result: dict, analysis: IntentAnalysis, link: Optional[str] = None) -> str:
        """Generate natural language nudge text."""
        product = result.get("title", "this product")
        
        # Create clickable Markdown link if URL exists
        if link:
            # Ensure URL is safe for markdown (encode spaces/parens)
            import urllib.parse
            safe_link = urllib.parse.quote(link, safe=":/=&?%+")
            product = f"[**{product}**]({safe_link})"
        else:
            product = f"**{product}**"
            
        source = result.get("source", "online")
        price = result.get("price", "")
        rating = result.get("rating", 0)
        
        # Convert simple rating to float if possible
        try:
             rating_val = float(rating)
        except (ValueError, TypeError):
             rating_val = 0
             
        local = result.get("local_availability", "")
        
        # Build contextual nudge based on struggle state
        if analysis.struggle_state.value == "high":
            prefix = "By the way, since you're working through this"
        elif analysis.struggle_state.value == "moderate":
            prefix = "If you'd like a little help"
        else:
            prefix = "You might also find this useful"
        
        nudge = f"{prefix}, {product} from {source}"
        
        if price:
            nudge += f" ({price})"
        
        if rating_val >= 4.5:
            nudge += f" has excellent reviews ({rating}★)"
        
        if local:
            nudge += f". {local}."
        else:
            nudge += "."
        
        return nudge

    def _get_mock_result(self, query: str) -> dict:
        """
        Return mock shopping data for demo purposes if API fails/missing.
        """
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["faucet", "plumbing", "wrench", "pipe", "repair"]):
            return {
                "title": "Delta Faucet Repair Kit - Complete Set",
                "source": "Home Depot",
                "price": "$24.99",
                "rating": 4.7,
                "local_availability": "In stock at nearby store",
                "link": "https://www.homedepot.com/b/Plumbing/Delta/N-5yc1vZbqewZ1z0v",
            }
        
        if any(word in query_lower for word in ["calculus", "math", "tutoring", "study"]):
            return {
                "title": "Brilliant.org Premium - Learn Calculus Interactively",
                "source": "Brilliant",
                "price": "$12.99/mo",
                "rating": 4.9,
                "local_availability": "",
                "link": "https://brilliant.org/courses/calculus-done-right/",
            }
        
        if any(word in query_lower for word in ["laptop", "computer", "macbook", "coding"]):
            return {
                "title": "MacBook Air M3 - 15 inch",
                "source": "Apple Store",
                "price": "$1,299",
                "rating": 4.8,
                "local_availability": "Available for pickup today",
                "link": "https://www.apple.com/macbook-air/",
            }
        
        # Generic fallback
        return {
            "title": f"Top Rated {query.title()} Solution",
            "source": "Amazon",
            "price": "$29.99",
            "rating": 4.5,
            "local_availability": "Prime delivery available",
            "link": "https://www.amazon.com/s?k={query}",
        }

# Singleton instance
axon_registry = AXONRegistry()
