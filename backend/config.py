import os
from dotenv import load_dotenv

load_dotenv()

# LLM — Primary: GPT-4o via AIML API
AIML_API_KEY = os.getenv("AIML_API_KEY", "")
AIML_BASE_URL = os.getenv("AIML_BASE_URL", "https://api.aimlapi.com/v1")
AIML_MODEL = os.getenv("AIML_MODEL", "gpt-4o")

# LLM — Fallback: Google Gemini (free tier)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Signal Harvester APIs
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")

# App
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("PORT", os.getenv("APP_PORT", "8000")))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
