"""
Tool 2: Research Analyst (Account Insight)
Takes harvested signals + ICP to generate a 2-paragraph Account Brief.
Uses Google Gemini for AI analysis.
"""

import google.generativeai as genai
import json


RESEARCH_SYSTEM_PROMPT = """You are an elite B2B account research analyst at FireReach. 
Your job is to analyze raw buyer signals and create a concise, actionable Account Brief.

RULES:
1. Write EXACTLY 2 paragraphs.
2. Paragraph 1: Summarize the company's current situation based on the REAL signals provided. 
   Reference specific data points (funding, hiring numbers, news, tech stack).
3. Paragraph 2: Connect the company's situation to the user's ICP. Identify specific pain points 
   and explain the strategic alignment — why THIS company needs what the ICP offers RIGHT NOW.
4. Be specific, not generic. Use actual numbers and signal data.
5. Do NOT invent data. Only reference signals that were actually provided.
6. Write in a professional, analytical tone."""


async def tool_research_analyst(
    icp: str,
    signals: dict,
    gemini_key: str,
) -> dict:
    """
    Generate a 2-paragraph Account Brief from ICP + harvested signals.
    """
    if not gemini_key:
        return {
            "account_brief": (
                "⚠️ Gemini API key not configured. Cannot generate research analysis. "
                "Please set GEMINI_API_KEY in your .env file."
            ),
            "status": "error",
        }

    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        user_prompt = f"""Analyze the following buyer signals for this target company and create an Account Brief.

USER'S ICP (Ideal Customer Profile):
{icp}

HARVESTED SIGNALS:
{json.dumps(signals, indent=2, default=str)}

Write a 2-paragraph Account Brief:
- Paragraph 1: Company situation analysis based on the signals
- Paragraph 2: Strategic alignment with the user's ICP and specific pain points"""

        response = model.generate_content(
            [
                {"role": "user", "parts": [{"text": RESEARCH_SYSTEM_PROMPT}]},
                {"role": "model", "parts": [{"text": "Understood. I will analyze the signals and create a precise, data-driven Account Brief."}]},
                {"role": "user", "parts": [{"text": user_prompt}]},
            ]
        )

        account_brief = response.text.strip()

        return {
            "account_brief": account_brief,
            "status": "success",
            "icp_used": icp,
        }

    except Exception as e:
        return {
            "account_brief": f"Error generating research: {str(e)}",
            "status": "error",
        }
