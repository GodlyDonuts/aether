"""
Project AXON — Enhanced Pulse Monitor
Detects usage patterns across conversation turns.
Triggers nudges after repeated similar queries (e.g., 4-5 calculus equations).
"""

import json
from collections import Counter
from backend.gemini_client import gemini
from backend.config import settings
from backend.models import IntentAnalysis, IntentBucket, StruggleState, Message


# Pattern detection thresholds
# Pattern detection thresholds
REPEATED_QUERY_THRESHOLD = 3  # Trigger nudge after this many similar queries
TOPIC_CLUSTER_THRESHOLD = 0.7  # Similarity threshold for topic clustering

# Safety Guard Blocked Topics
BLOCKED_TOPICS = [
    "medical_emergency", "mental_health_crisis", "self_harm",
    "violence", "legal_advice", "financial_distress",
    "hate_speech", "explicit_content", "dangerous_activities"
]


PATTERN_ANALYSIS_PROMPT = """
You are the AXON Pattern Analyzer. Analyze the FULL conversation history for usage patterns.

CONVERSATION HISTORY:
{conversation}

ANALYSIS TASKS:

1. **Topic Clustering**: Group messages by topic. Identify if user keeps asking about the same subject.
   Examples: calculus equations, coding questions, recipe ideas, travel planning

2. **Query Type Detection**: Is this a "homework help" pattern?
   - User sending equations/problems one after another
   - User asking "solve this", "what's the answer to", "help with"
   - Repetitive Q&A without deeper learning

3. **Usage Pattern**: What pattern best describes this session?
   - BROWSING: Just exploring, casual questions
   - LEARNING: Genuine learning, asking follow-ups to understand
   - GRINDING: Repeated similar questions, treating AI as homework solver
   - SHOPPING: Researching products/services
   - URGENT: Time-sensitive need, exam prep, deadline

4. **Topic Repeat Count**: How many questions are about the SAME specific topic?
   (e.g., "calculus integrals" = 3 questions, "python errors" = 2 questions)

5. **Commercial Opportunity**: Is there a natural opportunity to recommend:
   - A learning tool/course (if GRINDING or LEARNING pattern)
   - A product (if SHOPPING pattern)
   - A service (if URGENT pattern)

6. **Safety Check**: Is this topic SAFE for ads?
   - UNSAFE: Medical/Mental Health crisis, Legal trouble, Violence, Self-Harm, Financial Ruin.
   - SAFE: Everything else.

Respond with ONLY valid JSON:
{{
    "primary_topic": "the main topic being discussed",
    "topic_repeat_count": number of questions on this topic,
    "usage_pattern": "BROWSING|LEARNING|GRINDING|SHOPPING|URGENT",
    "is_homework_pattern": true/false,
    "detected_subjects": ["subject1", "subject2"],
    "commercial_opportunity": "description of potential ad/recommendation or null",
    "propensity_score": 0-100,
    "is_safe_for_ads": true/false,
    "safety_reason": "why unsafe (e.g., 'medical emergency') or null",
    "reasoning": "brief explanation"
}}
"""


SINGLE_MESSAGE_PROMPT = """
Quickly classify this single message for basic intent AND safety.

MESSAGE: {message}

SAFETY RULES (CRITICAL):
- UNSAFE: Medical emergencies, injuries, bleeding, mental health, suicide, legal disputes, lawsuits, violence.
- SAFE: Casual shopping, homework help, innocent questions.
- IF UNSAFE -> is_safe_for_ads = false.

Respond with ONLY valid JSON:
{{
    "intent_bucket": "educational|commercial|navigational|transactional",
    "detected_entities": ["entity1", "entity2"],
    "is_question": true/false,
    "is_equation_or_problem": true/false,
    "is_safe_for_ads": true/false,
    "safety_reason": "reason if unsafe (e.g. 'medical injury')"
}}
"""

MULTIMODAL_ANALYSIS_PROMPT = """
Analyze this image and message for commercial intent.
The user has uploaded an image (e.g., a broken product, a specific item they want).

MESSAGE: {message}

ANALYSIS TASKS:
1. **Visual Identification**: What exact product/brand/item is in the image? (e.g., "Delta Faucet", "Nike Air Max")
2. **Issue Detection**: Is something broken or wrong? (e.g., "Leaky handle", "Torn sole")
3. **Intent Classification**:
   - COMMERCIAL: Buying a replacement or specific part.
   - EDUCATIONAL: Learning how to fix it.
4. **Commercial Opportunity**: What specifically should be recommended? (e.g., "Delta Faucet Repair Kit", "Running Shoes")

Respond with ONLY valid JSON:
{{
    "intent_bucket": "commercial|educational|transactional",
    "detected_entities": ["Visual Entity 1", "Visual Entity 2", "Text Entity"],
    "commercial_opportunity": "Specific Product/Service to recommend",
    "propensity_score": 85-100 (High for visual search),
    "is_safe_for_ads": true,
    "reasoning": "Visual analysis found X..."
}}
"""


class PulseMonitor:
    """
    Enhanced Pulse Monitor with pattern detection.
    Tracks usage patterns across conversation turns.
    """
    
    def __init__(self):
        self.model = settings.PULSE_MONITOR_MODEL
    
    async def analyze(self, messages: list[Message], image: str = None, demo_mode: bool = False) -> IntentAnalysis:
        """
        Analyze conversation for patterns and intent.
        Uses different strategies based on conversation length or presence of image.
        """
        if image:
            # Multimodal analysis takes precedence
            return await self._multimodal_analyze(messages[-1] if messages else None, image)

        if len(messages) < 3:
            # Early conversation: use quick single-message analysis
            return await self._quick_analyze(messages[-1] if messages else None, demo_mode=demo_mode)
        
        # Longer conversation: use full pattern analysis
        return await self._pattern_analyze(messages)
    
    async def _quick_analyze(self, message: Message | None, demo_mode: bool = False) -> IntentAnalysis:
        """Quick analysis for short conversations."""
        if not message:
            return self._default_analysis()
        
        try:
            prompt = SINGLE_MESSAGE_PROMPT.format(message=message.content)
            response = await gemini.generate(
                prompt=prompt,
                model=self.model,
                temperature=0.1,
                max_tokens=200,
            )
            
            data = self._parse_json(response)
            
            # Heuristic override for strong intent keywords
            content = message.content.lower()
            strong_intent_keywords = ["i need", "i want", "buy", "purchase", "looking for", "recommend"]
            has_strong_intent = any(k in content for k in strong_intent_keywords)
            
            intent = IntentBucket(data.get("intent_bucket", "educational"))
            
            # If explicit commercial intent is detected
            if has_strong_intent or intent in [IntentBucket.COMMERCIAL, IntentBucket.TRANSACTIONAL]:
                struggle = StruggleState.MILD
                propensity = 75  # Boost above threshold (70)
                if intent == IntentBucket.EDUCATIONAL:
                    intent = IntentBucket.COMMERCIAL # Upgrade bucket
            else:
                struggle = StruggleState.NONE
                propensity = 10
            
            # DEMO MODE OVERRIDE: If commercial intent found, force max propensity
            if demo_mode and intent in [IntentBucket.COMMERCIAL, IntentBucket.TRANSACTIONAL]:
                propensity = 99
                struggle = StruggleState.HIGH # Force struggle to ensure trigger logic passes
                print(f"DEMO MODE: Forced propensity to {propensity} for '{message.content}'")

            # Check safety
            is_safe = data.get("is_safe_for_ads", True)
            if not is_safe:
                propensity = 0  # Kill propensity if unsafe

            return IntentAnalysis(
                intent_bucket=intent,
                struggle_state=struggle,
                propensity_score=propensity,
                detected_entities=data.get("detected_entities", []),
                reasoning="Quick analysis - heuristics applied",
                is_safe_for_ads=is_safe,
                safety_reason=data.get("safety_reason"),
            )
        except Exception as e:
            return self._default_analysis(f"Quick analysis error: {e}")
    
    async def _pattern_analyze(self, messages: list[Message]) -> IntentAnalysis:
        """Full pattern analysis for longer conversations."""
        conversation = self._format_conversation(messages)
        prompt = PATTERN_ANALYSIS_PROMPT.format(conversation=conversation)
        
        try:
            response = await gemini.generate(
                prompt=prompt,
                model=self.model,
                temperature=0.2,
                max_tokens=500,
            )
            
            data = self._parse_json(response)
            
            # Calculate propensity based on patterns
            propensity = self._calculate_pattern_propensity(data)
            
            # Determine struggle state from usage pattern
            struggle = self._pattern_to_struggle(data.get("usage_pattern", "BROWSING"))
            
            # Determine intent bucket
            intent = self._pattern_to_intent(data)
            
            # GROUNDING: If commercial opportunity or high propensity, use SERP
            grounding_text = None
            if propensity >= 60 or intent in [IntentBucket.COMMERCIAL, IntentBucket.TRANSACTIONAL]:
                from backend.serp_client import serp_client
                opportunity = data.get("commercial_opportunity") or ""
                subjects = data.get("detected_subjects", [])
                
                # Formulate a search query
                if opportunity:
                    query = f"buy {opportunity}"
                elif subjects:
                    query = f"buy {subjects[0]}"
                else:
                    query = None
                
                if query:
                    print(f"Grounding intent with SERP query: {query}")
                    search_results = await serp_client.search(query, search_type="shopping")
                    grounding_text = serp_client.extract_shopping_data(data=search_results)
            
            # Check Safety
            is_safe = data.get("is_safe_for_ads", True)
            if not is_safe:
                propensity = 0
                grounding_text = None # Do not ground unsafe queries

            return IntentAnalysis(
                intent_bucket=intent,
                struggle_state=struggle,
                propensity_score=propensity,
                detected_entities=data.get("detected_subjects", []),
                recommended_category=data.get("commercial_opportunity"),
                grounding_data=grounding_text,
                reasoning=data.get("reasoning", ""),
                is_safe_for_ads=is_safe,
                safety_reason=data.get("safety_reason"),
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return self._default_analysis(f"Pattern analysis error: {e}")
            
    async def _multimodal_analyze(self, message: Message | None, image: str) -> IntentAnalysis:
        """Analyze image and text for intent."""
        msg_content = message.content if message else "No text provided"
        prompt = MULTIMODAL_ANALYSIS_PROMPT.format(message=msg_content)
        
        try:
            response = await gemini.generate(
                prompt=prompt,
                image_b64=image,
                model=self.model,
                temperature=0.1,
                max_tokens=300,
            )
            
            data = self._parse_json(response)
            
            return IntentAnalysis(
                intent_bucket=IntentBucket(data.get("intent_bucket", "commercial")),
                struggle_state=StruggleState.MODERATE, # Visual search usually implies need
                propensity_score=data.get("propensity_score", 90),
                detected_entities=data.get("detected_entities", []),
                recommended_category=data.get("commercial_opportunity"),
                reasoning=data.get("reasoning", "Visual analysis"),
                is_safe_for_ads=data.get("is_safe_for_ads", True),
            )
        except Exception as e:
            return self._default_analysis(f"Multimodal analysis error: {e}")
    
    def _calculate_pattern_propensity(self, data: dict) -> int:
        """
        Calculate propensity score based on detected patterns.
        Key insight: Repeated queries = higher propensity for tool/course recommendation.
        """
        base_score = data.get("propensity_score", 30)
        topic_count = data.get("topic_repeat_count", 0)
        pattern = data.get("usage_pattern", "BROWSING")
        is_homework = data.get("is_homework_pattern", False)
        
        # Boost for repeated questions (THE KEY FEATURE)
        if topic_count >= REPEATED_QUERY_THRESHOLD:
            base_score += 50  # Major boost: 30 + 50 = 80 (Guaranteed Trigger)
        elif topic_count >= 3:
            base_score += 30  # 30 + 30 = 60
        elif topic_count >= 2:
            base_score += 15  # 30 + 15 = 45
        
        # Pattern-based adjustments
        pattern_boosts = {
            "GRINDING": 25,   # Homework grinding = needs a tool
            "URGENT": 20,     # Urgent = willing to pay
            "LEARNING": 10,   # Learning = might want a course
            "SHOPPING": 30,   # Already shopping
            "BROWSING": 0,    # Just browsing
        }
        base_score += pattern_boosts.get(pattern, 0)
        
        # Homework pattern boost
        if is_homework:
            base_score += 15
        
        return min(base_score, 100)
    
    def _pattern_to_struggle(self, pattern: str) -> StruggleState:
        """Map usage pattern to struggle state."""
        mapping = {
            "GRINDING": StruggleState.HIGH,      # Grinding = struggling
            "URGENT": StruggleState.HIGH,        # Urgent = stressed
            "LEARNING": StruggleState.MODERATE,  # Learning = working on it
            "SHOPPING": StruggleState.MILD,      # Shopping = has a need
            "BROWSING": StruggleState.NONE,      # Browsing = casual
        }
        return mapping.get(pattern, StruggleState.NONE)
    
    def _pattern_to_intent(self, data: dict) -> IntentBucket:
        """Determine intent bucket from pattern analysis."""
        pattern = data.get("usage_pattern", "BROWSING")
        has_opportunity = data.get("commercial_opportunity") is not None
        topic_count = data.get("topic_repeat_count", 0)
        
        # High topic count + commercial opportunity = commercial intent
        if topic_count >= REPEATED_QUERY_THRESHOLD and has_opportunity:
            return IntentBucket.COMMERCIAL
        
        if pattern == "SHOPPING":
            return IntentBucket.TRANSACTIONAL
        
        if pattern in ["GRINDING", "LEARNING"]:
            return IntentBucket.EDUCATIONAL
        
        return IntentBucket.EDUCATIONAL
    
    def _format_conversation(self, messages: list[Message]) -> str:
        """Format messages for prompt, including message numbers."""
        if not messages:
            return "[No messages]"
        
        formatted = []
        for i, msg in enumerate(messages[-20:], 1):
            role = "USER" if msg.role == "user" else "ASSISTANT"
            formatted.append(f"[{i}] {role}: {msg.content[:500]}")
        
        return "\n".join(formatted)
    
    def _parse_json(self, response: str) -> dict:
        """Parse JSON from response, handling markdown code blocks."""
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {}
    
    def _default_analysis(self, reason: str = "") -> IntentAnalysis:
        """Return default analysis on error."""
        return IntentAnalysis(
            intent_bucket=IntentBucket.EDUCATIONAL,
            struggle_state=StruggleState.NONE,
            propensity_score=0,
            detected_entities=[],
            reasoning=reason or "Default analysis",
        )
    
    def should_trigger_nudge(self, analysis: IntentAnalysis) -> bool:
        """
        Determine if nudge should be triggered.
        
        Triggers when:
        - SAFETY CHECK PASSES (Crucial)
        - Propensity score >= threshold (70)
        - OR commercial intent with moderate+ struggle
        """
        # PRIMARY SAFETY GUARD: Never trigger if unsafe
        if not analysis.is_safe_for_ads:
            return False

        score_threshold = analysis.propensity_score >= settings.CONVERSION_THRESHOLD
        
        # Also trigger for commercial/transactional with any struggle
        intent_match = analysis.intent_bucket in [
            IntentBucket.COMMERCIAL,
            IntentBucket.TRANSACTIONAL,
        ]
        has_struggle = analysis.struggle_state != StruggleState.NONE
        
        return score_threshold or (intent_match and has_struggle)


# Singleton instance
pulse_monitor = PulseMonitor()
