# FireReach MVP — Task Tracker

## 1. Project Setup & GitHub
- [ ] Initialize project structure (FastAPI backend + React frontend)
- [ ] Create GitHub public repo and push initial code
- [ ] Set up `.env` for API keys, `requirements.txt`, `package.json`

## 2. Backend — Core Agent Architecture
- [ ] Set up FastAPI server with CORS
- [ ] Implement the agentic orchestrator (LLM function-calling loop)
- [ ] Define tool schemas for all 3 tools

## 3. Tool 1 — `tool_signal_harvester`
- [ ] Implement funding/financial signals (Finnhub free API)
- [ ] Implement hiring signals (direct ATS: Greenhouse/Lever endpoints)
- [ ] Implement news/event signals (NewsAPI / GNews)
- [ ] Implement tech stack detection (HTTP header/script inspection)
- [ ] Aggregate all signals into structured JSON output

## 4. Tool 2 — `tool_research_analyst`
- [ ] Build prompt that takes ICP + harvested signals
- [ ] Generate 2-paragraph "Account Brief" with pain points & strategic alignment
- [ ] Return structured research output

## 5. Tool 3 — `tool_outreach_automated_sender`
- [ ] Build email generation prompt (zero-template, references live signals)
- [ ] Integrate email sending (SMTP / Resend free tier)
- [ ] Implement the automated send action

## 6. Frontend — React Dashboard
- [ ] Create minimal React UI with form inputs (ICP, target company, email)
- [ ] Display agent reasoning flow (Signal → Research → Send)
- [ ] Show email preview and send status
- [ ] Style with premium modern design

## 7. Agent Documentation (DOCS.md)
- [ ] Document logic flow
- [ ] Document tool schemas
- [ ] Document system prompt / persona

## 8. Deployment & Testing
- [ ] Test with the Rabbitt Challenge Prompt
- [ ] Deploy to Vercel (frontend) + Render (backend)
- [ ] Final GitHub cleanup and README
