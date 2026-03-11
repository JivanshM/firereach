# 🔥 FireReach — Autonomous Outreach Engine

> An AI-powered agent that captures live buyer signals, generates research briefs, and sends hyper-personalized emails — all autonomously.

Built for the **Rabbitt AI** ecosystem.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- API Keys (see below)

### 1. Clone & Setup Backend

```bash
git clone https://github.com/YOUR_USERNAME/firereach.git
cd firereach

# Backend
cd backend
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt

# Create .env from example
cp .env.example .env
# Edit .env with your API keys
```

### 2. Setup Frontend

```bash
cd frontend
npm install
```

### 3. Get API Keys

| Service | Free Tier | Get Key |
|---|---|---|
| Google Gemini | Free tier available | [aistudio.google.com](https://aistudio.google.com/apikey) |
| Finnhub | 60 calls/min | [finnhub.io](https://finnhub.io/) |
| GNews | 100 req/day | [gnews.io](https://gnews.io/) |
| Resend | 100 emails/day | [resend.com](https://resend.com/) |

### 4. Run

```bash
# Terminal 1 — Backend
cd backend
python main.py

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open **http://localhost:5173**

---

## 🏗️ Architecture

```
Signal Capture (Deterministic) → Research Analysis (AI) → Email Generation & Send (AI + Execution)
```

**3 Tools:**
1. **`tool_signal_harvester`** — Fetches financial, hiring, news, and tech stack signals via APIs
2. **`tool_research_analyst`** — AI generates a 2-paragraph Account Brief with pain points
3. **`tool_outreach_automated_sender`** — AI writes a personalized email and sends it via Resend

See [DOCS.md](./DOCS.md) for full documentation.

---

## 📂 Project Structure

```
├── backend/
│   ├── main.py              # FastAPI server
│   ├── agent.py             # Agentic orchestrator
│   ├── config.py            # Environment config
│   └── tools/
│       ├── signal_harvester.py
│       ├── research_analyst.py
│       └── outreach_sender.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # React dashboard
│   │   └── index.css        # Design system
│   └── package.json
├── DOCS.md                  # Agent documentation
└── README.md
```

---

## 🧪 Test with Challenge Prompt

**ICP:** "We sell high-end cybersecurity training to Series B startups."  
**Task:** Find companies with recent growth signals and send a personalized outreach email.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI + Python 3.10+
- **Frontend:** Vite + React
- **LLM:** Google Gemini 2.0 Flash
- **Email:** Resend API
- **Signal APIs:** Finnhub, GNews, Greenhouse/Lever ATS

---

## 📄 License

MIT
