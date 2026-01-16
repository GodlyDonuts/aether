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

    def _get_mock_result(self, query: str, intent: IntentAnalysis) -> Nudge:
        """
        Return mock shopping data for demo purposes if API fails/missing.
        """
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["faucet", "plumbing", "wrench", "pipe", "repair"]):
            # DEMO HARDCODING for Faucet/Repair Kit
            # If standard demo flow, return the rich visual ad
            if "faucet" in str(intent.detected_entities).lower() or "repair" in str(intent.detected_entities).lower():
                return Nudge(
                    id="nudge_demo_faucet",
                    product_name="Universal Faucet Repair Kit",
                    vendor_name="Delta Faucet",
                    price=24.99,
                    currency="USD",
                    rationale="Based on your image, this is the exact repair kit for your Delta faucet.",
                    relevance_score=0.98,
                    link="https://www.deltafaucet.com/parts/product/RP77739",
                    images=[
                        "/assets/nudge_gen.png", # AI Gen (Nano Banana)
                        "https://media.deltafaucet.com/elvis/OnWhite/MD/RP77739_WEB.png", # Real 1
                        "https://m.media-amazon.com/images/I/71wwM+y7H+L._AC_SL1500_.jpg" # Real 2
                    ]
                )

            return Nudge(
                id="nudge_123",
                product_name=f"Top Rated {intent.recommended_category or 'Product'}",
                vendor_name="Premium Partner",
                price=29.99,
                currency="USD",
                rationale="High buying intent detected for this category.",
                relevance_score=0.89,
                link=f"https://www.google.com/search?q={urllib.parse.quote(intent.recommended_category or 'product')}",
                images=["/assets/nudge_gen.png"]
            )
        
        if any(word in query_lower for word in ["calculus", "math", "tutoring", "study"]):
            return Nudge(
                id="nudge_demo_math",
                product_name="Calculus Done Right",
                vendor_name="Brilliant.org",
                price=12.99,
                currency="USD",
                rationale="Learn calculus interactively.",
                relevance_score=0.95,
                link="https://brilliant.org/courses/calculus-done-right/",
                images=[]
            )
        
        if any(word in query_lower for word in ["laptop", "computer", "macbook", "coding"]):
            return Nudge(
                id="nudge_demo_laptop",
                product_name="MacBook Air M3 - 15 inch",
                vendor_name="Apple Store",
                price=1299.00,
                currency="USD",
                rationale="Perfect for coding and creative work.",
                relevance_score=0.92,
                link="https://www.apple.com/macbook-air/",
                images=[]
            )
        
        # Generic fallback
        return Nudge(
            id="nudge_generic",
            product_name=f"Top Rated {query.title()} Solution",
            vendor_name="Trusted Partner",
            price=29.99,
            currency="USD",
            rationale="Highly relevant to your search.",
            relevance_score=0.85,
            link=f"https://www.google.com/search?q={urllib.parse.quote(query)}",
            images=[]
        )


# Singleton instance
axon_registry = AXONRegistry()
