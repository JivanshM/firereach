# ReachAI  Autonomous Outreach Engine

> An AI-powered agent that captures **live buyer signals**, performs **independent web research**, generates **AI-driven Account Briefs**, and prepares **hyper-personalized emails** — sent directly from your browser.

---

## Quick Start (One Click)

**Windows:** Double-click `local.bat` — it installs dependencies, starts both servers, and opens your browser.

### Manual Setup

**Prerequisites:** Python 3.10+ | Node.js 18+

`ash
git clone https://github.com/YourRepo/reachai.git
cd reachai

# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env        # then edit .env with your API keys
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
`

Open **http://localhost:5173**

---

## API Keys Required

| Service | Purpose | Free Tier | Get Key |
|---------|---------|-----------|---------|
| **AIML API** | LLM (GPT-4o) for research + email generation | Free tier | [aimlapi.com](https://aimlapi.com/) |
| **Google Gemini** | Fallback LLM (Gemini 2.0 Flash) | 100% free | [aistudio.google.com](https://aistudio.google.com/apikey) |
| **Finnhub** | Financial signals, company profiles | 60 calls/min | [finnhub.io](https://finnhub.io/register) |
| **GNews** | Latest company news articles | 100 req/day | [gnews.io](https://gnews.io/) |
| **EmailJS** | Client-side email dispatch (configure in frontend) | 200 emails/mo | [emailjs.com](https://www.emailjs.com/) |

**No API key needed for:** DuckDuckGo web search, company website scraping, Greenhouse/Lever ATS hiring data, tech stack detection.

---

## Architecture

`
User Input (ICP + Company + Email)
        |
        v
+------------------------------+
|  1. tool_signal_harvester    |  Deterministic (API-based)
|     - Finnhub (financial)    |
|     - ATS endpoints (hiring) |
|     - GNews (news/events)    |
|     - HTTP inspection (tech) |
+-------------|----------------+
              | Structured signals JSON
              v
+------------------------------+
|  2. tool_research_analyst    |  AI + Active Web Research
|     - DuckDuckGo search      |
|     - Company site scraping  |
|     - Cross-references all   |
|       data with ICP          |
|     - Generates Account Brief|
+-------------|----------------+
              | 2-paragraph Account Brief
              v
+------------------------------+
|  3. tool_outreach_sender     |  AI Generation
|     - Generates email (AI)   |
|     - References live signals|
|     - Returned to Frontend   |
+-------------|----------------+
              | Sends via EmailJS (Client-Side)
              v
`

**Key Design Principles:**
- **Signal -> Research -> Send** — The agent never sends without researching first
- **Active Web Research** — Tool 2 performs its own DuckDuckGo searches and website scraping
- **Zero-Template Policy** — Every email explicitly references captured signals
- **Deterministic Signals** — Tool 1 uses only API data, the LLM cannot guess signals
- **Automated Execution** — Send is triggered automatically once research is complete

---

## Project Structure

`
firereach/
+-- backend/
|   +-- main.py                 # FastAPI server + SSE streaming
|   +-- agent.py                # Agentic orchestrator (3-tool pipeline)
|   +-- config.py               # Environment config loader
|   +-- tools/
|   |   +-- signal_harvester.py # Tool 1: Deterministic signal capture
|   |   +-- research_analyst.py # Tool 2: Web research + AI analysis
|   |   +-- outreach_sender.py  # Tool 3: Email gen + Resend dispatch
|   +-- requirements.txt
|   +-- .env.example
+-- frontend/
|   +-- src/
|   |   +-- App.jsx             # React dashboard with SSE streaming
|   |   +-- index.css           # Premium design system
|   +-- package.json
|   +-- vite.config.js          # Dev proxy to backend
+-- DOCS.md                     # Agent documentation (tool schemas, prompts)
+-- local.bat                   # One-click Windows launcher
+-- README.md
`

---

## The Rabbitt Challenge Prompt

**ICP:** `We sell high-end cybersecurity training to Series B startups.`
**Task:** `Find companies with recent growth signals and send a personalized outreach email to [candidate-email-here] that connects their expansion to our security training.`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI (Python) with async tool execution |
| **Frontend** | Vite + React with SSE streaming |
| **Primary LLM** | GPT-4o via AIML API |
| **Fallback LLM** | Google Gemini 2.0 Flash |
| **Web Research** | DuckDuckGo search + BeautifulSoup scraping |
| **Email** | EmailJS (Client-side) |
| **Signal APIs** | Finnhub, GNews, Greenhouse/Lever ATS |

---

## License

MIT
