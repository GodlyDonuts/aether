# PROJECT AXON — Implementation Plan

> **The Semantic Monetization Layer for Generative Intelligence**

---

## Overview

This plan outlines the phased development of Project AXON, transforming AI chat from a monetization dead-end into a revenue-generating bridge. The architecture leverages **Gemini 3.0** as the core intelligence layer.

---

## 🤖 Gemini 3.0 Integration Strategy

Gemini 3.0 brings critical capabilities that make AXON possible:

| Capability | AXON Use Case |
|------------|---------------|
| **Native Tool Use** | Direct calls to Google Ads API, Merchant Center, Maps API without custom orchestration |
| **2M+ Token Context** | Build a complete Intent Graph over 20+ conversation turns |
| **Multimodal Reasoning** | Extract brand/product info from user-uploaded images (e.g., faucet photo) |
| **Thinking Mode** | Complex reasoning for determining "Conversion Threshold" and ad relevance |
| **Grounding with Search** | Real-time inventory checks and local business availability |

### Required APIs & SDKs
```
google-genai           # Gemini 3.0 Python SDK
google-ads             # Google Ads API Client
google-cloud-aiplatform # Vertex AI Safety Filters
graphql-core           # AXON Registry queries
```

### Model Configuration
```python
# Recommended models per component
PULSE_MONITOR_MODEL = "gemini-3.0-flash"      # Low-latency intent analysis
SYNTHESIZER_MODEL   = "gemini-3.0-pro"        # High-quality prose rewriting
SAFETY_GUARD_MODEL  = "gemini-3.0-flash"      # Fast safety classification
```

---

## 📋 Phase 0: Foundation & Infrastructure

**Duration:** 1-2 days  
**Goal:** Set up the development environment and core architecture

### Tasks
- [ ] Initialize project structure (Python FastAPI backend)
- [ ] Configure Gemini 3.0 API authentication
- [ ] Set up Google Ads API sandbox credentials
- [ ] Create base data models for Intent Graph
- [ ] Implement basic conversation state management
- [ ] Set up logging and monitoring infrastructure

### Deliverables
- `/backend` — FastAPI server with Gemini 3.0 integration
- `/models` — Pydantic models for Intent, Nudge, ConversationState
- `/config` — Environment configuration and API keys

---

## 📋 Phase 1: The Pulse Monitor (Intent Detection)

**Duration:** 2-3 days  
**Goal:** Analyze conversation history and detect commercial intent

### Tasks
- [ ] Design Intent Bucket taxonomy (Educational, Commercial, Navigational, Transactional)
- [ ] Implement conversation history buffer (last 10-20 turns)
- [ ] Build "Latent Commercial Intent" classifier using Gemini 3.0 Flash
- [ ] Create "Struggle State" detection algorithm
- [ ] Develop "Conversion Threshold" scoring system (0-100 scale)
- [ ] Add session persistence for multi-turn tracking

### Gemini 3.0 Prompt Engineering
```python
PULSE_MONITOR_PROMPT = """
Analyze this conversation for commercial intent signals:

CONVERSATION:
{conversation_history}

Classify into:
1. Intent Bucket: [Educational | Commercial | Navigational | Transactional]
2. Struggle State: [None | Mild | Moderate | High]
3. Propensity Score: 0-100 (likelihood of commercial action)
4. Detected Entities: Products, brands, services mentioned
5. Recommended Category: Google Ads category ID

Return structured JSON.
"""
```

### Deliverables
- `PulseMonitor` class with real-time intent analysis
- Intent Graph data structure
- Demo: User asking about "Calculus" → detect "Struggle State" by query #3

---

## 📋 Phase 2: AXON Registry (Ad Matching Engine)

**Duration:** 2-3 days  
**Goal:** Bridge between detected intent and Google Ads inventory

### Tasks
- [ ] Design GraphQL schema for AXON Registry
- [ ] Integrate Google Ads API for ad inventory queries
- [ ] Implement Merchant Center integration for product availability
- [ ] Build relevance scoring algorithm (target: 85%+ match)
- [ ] Create local inventory lookup (Google Maps API integration)
- [ ] Add real-time bidding simulation for demo purposes

### Architecture
```
Intent Graph → AXON Registry → Google Ads API
                    ↓
              Relevance Filter (>70% match)
                    ↓
              Ad Candidate Selection
```

### Deliverables
- `AXONRegistry` service with GraphQL endpoint
- Ad matching algorithm with relevance scoring
- Local inventory availability checker

---

## 📋 Phase 3: The Synthesizer (Micro-Nudge Injection)

**Duration:** 2-3 days  
**Goal:** Seamlessly weave ads into AI responses without breaking flow

### Tasks
- [ ] Design "Hyper-Relevant Sidenote" format
- [ ] Implement Gemini 3.0 Pro rewriting pipeline
- [ ] Create A/B testing framework for nudge styles
- [ ] Build natural language transition phrases
- [ ] Ensure ad disclosure compliance (FTC guidelines)
- [ ] Develop "Non-Intrusive" UI component for frontend

### Gemini 3.0 System Instruction
```python
SYNTHESIZER_SYSTEM = """
You are a helpful AI assistant. When an AXON nudge is triggered,
naturally incorporate the recommendation into your response.

RULES:
1. The nudge must feel like genuine advice, not an advertisement
2. Use transitional phrases like "By the way...", "You might find..."
3. Only suggest if directly relevant to the user's stated need
4. Never interrupt the main answer — nudge comes AFTER the help
5. Include specifics: brand name, availability, location if relevant

NUDGE DATA:
{nudge_payload}
"""
```

### Example Output
> "By the way, if you're struggling with this specific integration, [Branded Partner] has a specialized visualization tool for this exact theorem."

### Deliverables
- `Synthesizer` class with Gemini 3.0 Pro integration
- Nudge template library
- A/B testing harness

---

## 📋 Phase 4: Safety Guard (Content Filtering)

**Duration:** 1-2 days  
**Goal:** Prevent ads from appearing in sensitive contexts

### Tasks
- [ ] Integrate Vertex AI Safety Filters
- [ ] Define blocked categories (medical emergency, mental health, violence, etc.)
- [ ] Implement topic classification pre-filter
- [ ] Create override rules for advertiser exclusions
- [ ] Build audit logging for safety decisions
- [ ] Add manual review queue for edge cases

### Blocked Categories
```python
BLOCKED_TOPICS = [
    "medical_emergency",
    "mental_health_crisis",
    "child_safety",
    "violence",
    "self_harm",
    "legal_advice",
    "financial_distress"
]
```

### Deliverables
- `SafetyGuard` service with Vertex AI integration
- Topic classification pipeline
- Audit trail for all ad injection decisions

---

## 📋 Phase 5: Attribution Engine (Analytics)

**Duration:** 2-3 days  
**Goal:** Track "Assisted Conversions" and measure CPIF

### Tasks
- [ ] Design attribution data model
- [ ] Implement session tracking across conversation turns
- [ ] Build "Cost Per Intent Fulfillment" (CPIF) calculator
- [ ] Create conversion event tracking
- [ ] Develop real-time analytics dashboard
- [ ] Add A/B experiment tracking

### Metrics Schema
```typescript
interface AXONAnalytics {
  session_id: string;
  nudges_shown: number;
  nudge_relevance_scores: number[];
  conversions: {
    type: "click" | "purchase" | "lead";
    revenue: number;
    attribution_weight: number;
  }[];
  cpif: number;  // Cost Per Intent Fulfillment
}
```

### Deliverables
- Attribution tracking service
- Analytics dashboard (React frontend)
- CPIF calculation engine

---

## 📋 Phase 6: Demo Build (Hackathon Showcase)

**Duration:** 1-2 days  
**Goal:** Create the "Invisible Revenue Stream" demonstration

### Demo Flow
1. **Stage 1 (Baseline):** User asks "How do I fix a leaky faucet?" → Standard answer (Revenue = $0)
2. **Stage 2 (Intent Building):** Follow-up questions about wrench types
3. **Stage 3 (Multimodal):** User uploads faucet photo → Gemini Vision identifies brand
4. **Stage 4 (AXON Trigger):** System suggests local hardware store with part in stock
5. **Stage 5 (Dashboard Reveal):** Show 85% relevance match, $2.50 lead generated

### Tasks
- [ ] Build demo conversation script
- [ ] Create real-time dashboard with live metrics
- [ ] Implement multimodal image recognition for brand detection
- [ ] Set up mock Google Ads inventory
- [ ] Add "Before/After AXON" toggle for judges
- [ ] Record backup video demo

### Deliverables
- Interactive demo application
- Judge-facing analytics dashboard
- Presentation deck with live integration

---

## 🗓 Timeline Overview

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 0: Foundation | Days 1-2 | None |
| Phase 1: Pulse Monitor | Days 3-5 | Phase 0 |
| Phase 2: AXON Registry | Days 6-8 | Phase 0 |
| Phase 3: Synthesizer | Days 9-11 | Phases 1, 2 |
| Phase 4: Safety Guard | Days 12-13 | Phase 3 |
| Phase 5: Attribution | Days 14-16 | Phases 3, 4 |
| Phase 6: Demo Build | Days 17-18 | All Phases |

**Total Estimated Time:** 18 days (can be compressed for hackathon)

---

## 🔧 Tech Stack Summary

| Layer | Technology |
|-------|------------|
| **AI Core** | Gemini 3.0 Pro/Flash (google-genai SDK) |
| **Backend** | Python FastAPI + GraphQL |
| **Ad Integration** | Google Ads API, Merchant Center API |
| **Safety** | Vertex AI Safety Filters |
| **Database** | Firestore (conversation state) |
| **Analytics** | BigQuery + Custom Dashboard |
| **Frontend** | React + TailwindCSS |

---

## ⚡ Quick Start Commands

```bash
# Clone and setup
cd /Users/sairamen/projects/Aether
python -m venv venv && source venv/bin/activate
pip install google-genai google-ads google-cloud-aiplatform fastapi uvicorn

# Set environment
export GOOGLE_API_KEY="your-gemini-api-key"
export GOOGLE_ADS_DEVELOPER_TOKEN="your-ads-token"

# Run backend
uvicorn backend.main:app --reload
```

---

## 📝 What You Need to Do

### Immediate Actions
1. **Get API Access:**
   - Apply for Google Ads API sandbox access
   - Generate Gemini 3.0 API key from AI Studio
   - Enable Vertex AI in your GCP project

2. **Set Up Dev Environment:**
   - Create virtual environment
   - Install required dependencies
   - Configure environment variables

3. **Start with Phase 0:**
   - Initialize FastAPI project structure
   - Test Gemini 3.0 connection
   - Create base models

### Key Decisions Needed
- [ ] **Hosting:** Cloud Run vs. GKE for production demo?
- [ ] **Database:** Firestore vs. PostgreSQL for intent graph?
- [ ] **Demo scope:** Full multimodal or text-only for MVP?

---

> **Next Step:** Shall I start implementing Phase 0 and set up the foundational backend with Gemini 3.0 integration?
