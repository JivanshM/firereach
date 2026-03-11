# FireReach — Agent Documentation

## Overview

FireReach is an autonomous outreach engine built for the Rabbitt AI ecosystem. It captures live buyer signals, generates AI-powered research briefs, and automatically sends hyper-personalized emails — all through a sequential agentic pipeline.

---

## Logic Flow

The agent follows a strict sequential reasoning chain:

```
User Input (ICP + Company + Email)
        │
        ▼
┌──────────────────────────────┐
│  1. tool_signal_harvester    │  ← Deterministic (API/Search based)
│     - Finnhub (financial)    │
│     - ATS endpoints (hiring) │
│     - GNews (news/events)    │
│     - HTTP inspection (tech) │
└─────────────┬────────────────┘
              │ Structured signals JSON
              ▼
┌──────────────────────────────┐
│  2. tool_research_analyst    │  ← AI-powered (Gemini 2.0 Flash)
│     - Analyzes signals       │
│     - Maps to user ICP       │
│     - Generates Account Brief│
└─────────────┬────────────────┘
              │ 2-paragraph Account Brief
              ▼
┌──────────────────────────────┐
│  3. tool_outreach_sender     │  ← AI + Automated Execution
│     - Generates email (AI)   │
│     - References live signals│
│     - Sends via Resend API   │
└──────────────────────────────┘
```

**Key Design Principles:**
- **Signal → Research → Send**: The agent NEVER sends without researching first.
- **Zero-Template Policy**: Every email explicitly references captured signals.
- **Deterministic Signals**: Tool 1 uses only API data — the LLM cannot "guess" signals.
- **Automated Execution**: The send action is triggered automatically once research is complete.

---

## Tool Schemas

### 1. `tool_signal_harvester`

**Type:** Deterministic  
**Purpose:** Fetch live buyer signals for a target company.

```json
{
  "name": "tool_signal_harvester",
  "parameters": {
    "company": { "type": "string", "description": "Target company name" },
    "domain": { "type": "string", "description": "Company website domain (optional)" },
    "finnhub_key": { "type": "string", "description": "Finnhub API key" },
    "gnews_key": { "type": "string", "description": "GNews API key" }
  },
  "returns": {
    "company": "string",
    "domain": "string",
    "signals": {
      "financial": { "source": "finnhub", "data": {} },
      "hiring": { "source": "ats_direct", "data": {} },
      "news": { "source": "gnews", "data": [] },
      "tech_stack": { "source": "tech_detection", "data": {} }
    }
  }
}
```

**Data Sources:**
| Signal Type | Source | Free Tier |
|---|---|---|
| Financial | Finnhub API | 60 calls/min |
| Hiring | Greenhouse/Lever direct ATS | Unlimited |
| News | GNews API | 100 req/day |
| Tech Stack | HTTP header/script inspection | Unlimited |

### 2. `tool_research_analyst`

**Type:** AI-powered (Gemini 2.0 Flash)  
**Purpose:** Generate a 2-paragraph Account Brief from signals + ICP.

```json
{
  "name": "tool_research_analyst",
  "parameters": {
    "icp": { "type": "string", "description": "User's Ideal Customer Profile" },
    "signals": { "type": "object", "description": "Output from tool_signal_harvester" },
    "gemini_key": { "type": "string", "description": "Gemini API key" }
  },
  "returns": {
    "account_brief": "string (2 paragraphs)",
    "status": "success | error",
    "icp_used": "string"
  }
}
```

### 3. `tool_outreach_automated_sender`

**Type:** AI + Execution  
**Purpose:** Generate a hyper-personalized email and send it.

```json
{
  "name": "tool_outreach_automated_sender",
  "parameters": {
    "account_brief": { "type": "string", "description": "From tool_research_analyst" },
    "signals": { "type": "object", "description": "From tool_signal_harvester" },
    "icp": { "type": "string", "description": "User's ICP" },
    "recipient_email": { "type": "string", "description": "Target email" },
    "gemini_key": { "type": "string" },
    "resend_key": { "type": "string" },
    "sender_email": { "type": "string" }
  },
  "returns": {
    "status": "sent | skipped | error",
    "subject": "string",
    "body": "string",
    "message": "string"
  }
}
```

---

## System Prompt — Agent Persona

### Signal Harvester
> No system prompt — this tool is deterministic (pure API calls).

### Research Analyst Persona
```
You are an elite B2B account research analyst at FireReach.
Your job is to analyze raw buyer signals and create a concise, actionable Account Brief.

RULES:
1. Write EXACTLY 2 paragraphs.
2. Paragraph 1: Summarize the company's current situation based on REAL signals.
3. Paragraph 2: Connect the company to the user's ICP with specific pain points.
4. Be specific, not generic. Use actual numbers and signal data.
5. Do NOT invent data.
6. Professional, analytical tone.
```

### Outreach Email Persona
```
You are an elite B2B copywriter at FireReach.

STRICT RULES:
1. ZERO TEMPLATES: Never use generic openings.
2. MUST cite at least 2 specific signals from the research.
3. Keep it SHORT: 4-6 sentences max.
4. End with a soft CTA.
5. Subject line must be specific and intriguing.
6. Output as JSON: { "subject": "...", "body": "..." }
```

---

## Architecture

- **Backend:** FastAPI (Python) with async tool execution
- **Frontend:** Vite + React with SSE streaming
- **LLM:** Google Gemini 2.0 Flash (function calling)
- **Email:** Resend API (100 free emails/day)
- **Signal APIs:** Finnhub, GNews, direct ATS endpoints
