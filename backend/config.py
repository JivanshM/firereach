import os
from dotenv import load_dotenv

load_dotenv()

# LLM
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Signal Harvester APIs
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")

# Email Sending
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "onboarding@resend.dev")

# App
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
