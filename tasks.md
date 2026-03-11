# FireReach MVP — Task Tracker

## 1. Project Setup & GitHub
- [x] Initialize project structure (FastAPI backend + React frontend)
- [x] Create GitHub public repo and push initial code
- [x] Set up `.env` for API keys, `requirements.txt`, `package.json`

## 2. Backend — Core Agent Architecture
- [x] Set up FastAPI server with CORS
- [x] Implement the agentic orchestrator (function-calling loop)
- [x] Define tool schemas for all 3 tools

## 3. Tool 1 — `tool_signal_harvester`
- [x] Implement funding/financial signals (Finnhub free API)
- [x] Implement hiring signals (direct ATS: Greenhouse/Lever endpoints)
- [x] Implement news/event signals (GNews API)
- [x] Implement tech stack detection (HTTP header/script inspection)
- [x] Aggregate all signals into structured JSON output

## 4. Tool 2 — `tool_research_analyst`
- [x] Build prompt that takes ICP + harvested signals
- [x] Generate 2-paragraph "Account Brief" with pain points & strategic alignment
- [x] Return structured research output

## 5. Tool 3 — `tool_outreach_automated_sender`
- [x] Build email generation prompt (zero-template, references live signals)
- [x] Integrate email sending (Resend free tier)
- [x] Implement the automated send action

## 6. Frontend — React Dashboard
- [x] Create minimal React UI with form inputs (ICP, target company, email)
- [x] Display agent reasoning flow (Signal → Research → Send)
- [x] Show email preview and send status
- [x] Style with premium modern design

## 7. Agent Documentation (DOCS.md)
- [x] Document logic flow
- [x] Document tool schemas
- [x] Document system prompt / persona

## 8. Deployment & Testing
- [/] Test with the Rabbitt Challenge Prompt
- [ ] Deploy to Vercel (frontend) + Render (backend)
- [x] Final GitHub cleanup and README
