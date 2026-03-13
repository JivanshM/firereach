"""
Tool 3: Outreach Automated Sender (Execution)
Generates a hyper-personalized email from research + signals.
Primary LLM: GPT-4o via AIML API
Fallback: Google Gemini (free tier)
"""

import json
import httpx
from openai import AsyncOpenAI
import google.generativeai as genai


EMAIL_SYSTEM_PROMPT = """You are an elite B2B copywriter at ReachAI. You write emails that feel 
written by a thoughtful human, not an AI.

STRICT RULES — VIOLATION = FAILURE:
1. ZERO TEMPLATES: Never use generic openings like "I hope this finds you well" or "I wanted to reach out."
2. MUST cite at least 2 specific signals from the research (e.g., "I noticed your team just raised a 
   Series B" or "Your 5 new engineering roles suggest rapid scaling").
3. Keep it SHORT: 4-6 sentences max. No walls of text.
4. End with a soft CTA — suggest value, don't hard-sell.
5. Subject line must be specific and intriguing, NOT generic.
6. Write the response as JSON with keys: "subject" and "body"
7. Sign off as the sender, keep it professional but warm.

OUTPUT FORMAT (strict JSON):
{
  "subject": "your subject line here",
  "body": "your email body here"
}"""


def _build_email_prompt(sender_name: str, account_brief: str, signals: dict, icp: str, recipient_email: str) -> str:
    return f"""Generate a hyper-personalized outreach email based on this research.

SENDER NAME:
{sender_name}

ACCOUNT BRIEF:
{account_brief}

RAW SIGNALS:
{json.dumps(signals, indent=2, default=str)}

SENDER'S ICP:
{icp}

RECIPIENT EMAIL:
{recipient_email}

Generate a JSON response with "subject" and "body" keys. 
The email MUST reference specific signals from the data above."""


def _parse_email_json(raw_text: str) -> dict:
    """Parse email JSON from LLM response, handling markdown code blocks."""
    text = raw_text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    try:
        email_data = json.loads(text)
        return {
            "subject": email_data.get("subject", ""),
            "body": email_data.get("body", ""),
            "status": "generated",
        }
    except json.JSONDecodeError:
        return {
            "subject": "Personalized Outreach",
            "body": text,
            "status": "generated_fallback",
        }


async def _generate_email_claude(prompt: str, aiml_key: str, aiml_base_url: str, aiml_model: str) -> str:
    """Generate email via Claude 3.5 Sonnet (AIML API)."""
    client = AsyncOpenAI(api_key=aiml_key, base_url=aiml_base_url)

    response = await client.chat.completions.create(
        model=aiml_model,
        messages=[
            {"role": "system", "content": EMAIL_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1024,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()


async def _generate_email_gemini(prompt: str, gemini_key: str) -> str:
    """Fallback: Generate email via Google Gemini."""
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    response = model.generate_content(
        [
            {"role": "user", "parts": [{"text": EMAIL_SYSTEM_PROMPT}]},
            {"role": "model", "parts": [{"text": '{"subject": "understood", "body": "I will generate a personalized email referencing real signals."}'}]},
            {"role": "user", "parts": [{"text": prompt}]},
        ]
    )

    return response.text.strip()


async def generate_email(
    sender_name: str,
    account_brief: str,
    signals: dict,
    icp: str,
    recipient_email: str,
    aiml_key: str = "",
    aiml_base_url: str = "https://api.aimlapi.com/v1",
    aiml_model: str = "claude-3-5-sonnet-latest",
    gemini_key: str = "",
) -> dict:
    """Generate a hyper-personalized email. Claude primary, Gemini fallback."""
    prompt = _build_email_prompt(sender_name, account_brief, signals, icp, recipient_email)
    llm_used = ""

    # Try primary: GPT-4o via AIML API
    if aiml_key:
        try:
            raw_text = await _generate_email_claude(prompt, aiml_key, aiml_base_url, aiml_model)
            result = _parse_email_json(raw_text)
            result["llm_used"] = f"{aiml_model} (via AIML API)"
            return result
        except Exception as e:
            print(f"⚠️ AIML API failed for email gen: {e}. Falling back to Gemini...")

    # Fallback: Google Gemini
    if gemini_key:
        try:
            raw_text = await _generate_email_gemini(prompt, gemini_key)
            result = _parse_email_json(raw_text)
            result["llm_used"] = "Google Gemini 2.0 Flash (fallback)"
            return result
        except Exception as e:
            return {"error": f"Both LLMs failed. Last error: {str(e)}"}

    return {"error": "No LLM API key configured. Set AIML_API_KEY or GEMINI_API_KEY in .env"}


async def tool_outreach_automated_sender(
    sender_name: str,
    account_brief: str,
    signals: dict,
    icp: str,
    recipient_email: str,
    aiml_key: str = "",
    aiml_base_url: str = "https://api.aimlapi.com/v1",
    aiml_model: str = "gpt-4o",
    gemini_key: str = "",
) -> dict:
    """
    Full outreach tool: Generate email.
    Primary LLM: GPT-4o (AIML API)
    Fallback LLM: Google Gemini (free)
    """
    # Step 1: Generate the email
    email = await generate_email(
        sender_name=sender_name,
        account_brief=account_brief,
        signals=signals,
        icp=icp,
        recipient_email=recipient_email,
        aiml_key=aiml_key,
        aiml_base_url=aiml_base_url,
        aiml_model=aiml_model,
        gemini_key=gemini_key,
    )

    if "error" in email:
        return {"status": "error", "message": email["error"]}

    # Return the generated email (sending is handled by frontend EmailJS)
    return {
        "status": "completed",
        "subject": email["subject"],
        "body": email["body"],
        "llm_used": email.get("llm_used", "unknown"),
        "message": "Email generated successfully."
    }
