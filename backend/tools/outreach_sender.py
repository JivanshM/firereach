"""
Tool 3: Outreach Automated Sender (Execution)
Generates a hyper-personalized email from research + signals,
then automatically dispatches it via Resend.
"""

import google.generativeai as genai
import json

try:
    import resend
except ImportError:
    resend = None


EMAIL_SYSTEM_PROMPT = """You are an elite B2B copywriter at FireReach. You write emails that feel 
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


async def generate_email(
    account_brief: str,
    signals: dict,
    icp: str,
    recipient_email: str,
    gemini_key: str,
) -> dict:
    """Generate a hyper-personalized email using Gemini."""
    if not gemini_key:
        return {"error": "Gemini API key not configured"}

    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        user_prompt = f"""Generate a hyper-personalized outreach email based on this research.

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

        response = model.generate_content(
            [
                {"role": "user", "parts": [{"text": EMAIL_SYSTEM_PROMPT}]},
                {"role": "model", "parts": [{"text": '{"subject": "understood", "body": "I will generate a personalized email referencing real signals."}'}]},
                {"role": "user", "parts": [{"text": user_prompt}]},
            ]
        )

        raw_text = response.text.strip()
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0].strip()

        email_data = json.loads(raw_text)
        return {
            "subject": email_data.get("subject", ""),
            "body": email_data.get("body", ""),
            "status": "generated",
        }

    except json.JSONDecodeError:
        # Fallback: try to extract subject and body manually
        return {
            "subject": "Personalized Outreach",
            "body": raw_text,
            "status": "generated_fallback",
        }
    except Exception as e:
        return {"error": f"Email generation failed: {str(e)}"}


async def send_email(
    subject: str,
    body: str,
    recipient_email: str,
    sender_email: str,
    resend_key: str,
) -> dict:
    """Send the email via Resend API."""
    if not resend_key:
        return {
            "status": "skipped",
            "message": "Resend API key not configured. Email generated but not sent.",
            "subject": subject,
            "body": body,
        }

    if resend is None:
        return {
            "status": "error",
            "message": "Resend package not installed.",
        }

    try:
        resend.api_key = resend_key

        params = {
            "from": sender_email,
            "to": [recipient_email],
            "subject": subject,
            "html": body.replace("\n", "<br>"),
        }

        email_response = resend.Emails.send(params)

        return {
            "status": "sent",
            "message": f"Email sent successfully to {recipient_email}",
            "email_id": email_response.get("id", "unknown") if isinstance(email_response, dict) else str(email_response),
            "subject": subject,
            "body": body,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Send failed: {str(e)}",
            "subject": subject,
            "body": body,
        }


async def tool_outreach_automated_sender(
    account_brief: str,
    signals: dict,
    icp: str,
    recipient_email: str,
    gemini_key: str = "",
    resend_key: str = "",
    sender_email: str = "onboarding@resend.dev",
) -> dict:
    """
    Full outreach tool: Generate email + Send it.
    """
    # Step 1: Generate the email
    email = await generate_email(
        account_brief=account_brief,
        signals=signals,
        icp=icp,
        recipient_email=recipient_email,
        gemini_key=gemini_key,
    )

    if "error" in email:
        return {"status": "error", "message": email["error"]}

    # Step 2: Send the email
    result = await send_email(
        subject=email["subject"],
        body=email["body"],
        recipient_email=recipient_email,
        sender_email=sender_email,
        resend_key=resend_key,
    )

    return result
