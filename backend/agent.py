"""
FireReach Agent Orchestrator
Implements sequential function-calling: Signal Capture → Research → Automated Delivery.
Primary LLM: GPT-4o via AIML API
Fallback LLM: Google Gemini (free tier)
"""

from tools.signal_harvester import tool_signal_harvester
from tools.research_analyst import tool_research_analyst
from tools.outreach_sender import tool_outreach_automated_sender
from config import (
    AIML_API_KEY, AIML_BASE_URL, AIML_MODEL,
    GEMINI_API_KEY,
    FINNHUB_API_KEY, GNEWS_API_KEY,
    BREVO_API_KEY, SENDER_EMAIL,
)


async def run_agent_pipeline(
    icp: str,
    company: str,
    domain: str,
    recipient_email: str,
    on_step: callable = None,
) -> dict:
    """
    Run the full FireReach agentic pipeline.
    
    Sequential flow:
    1. tool_signal_harvester → deterministic data fetching
    2. tool_research_analyst → AI analysis (Claude → Gemini fallback)
    3. tool_outreach_automated_sender → AI email gen + automated send
    """
    result = {
        "steps": [],
        "final_status": "pending",
    }

    # ─── Step 1: Signal Capture ──────────────────────────────────────
    step1 = {
        "tool": "tool_signal_harvester",
        "status": "running",
        "description": "Capturing live buyer signals...",
    }
    if on_step:
        await on_step("signal_harvester", step1)

    signals_result = await tool_signal_harvester(
        company=company,
        domain=domain,
        finnhub_key=FINNHUB_API_KEY,
        gnews_key=GNEWS_API_KEY,
    )

    step1["status"] = "completed"
    step1["data"] = signals_result
    result["steps"].append(step1)

    if on_step:
        await on_step("signal_harvester", step1)

    # ─── Step 2: Research Analysis ───────────────────────────────────
    step2 = {
        "tool": "tool_research_analyst",
        "status": "running",
        "description": "Performing web research & analyzing signals with Claude 3.5...",
    }
    if on_step:
        await on_step("research_analyst", step2)

    research_result = await tool_research_analyst(
        icp=icp,
        signals=signals_result.get("signals", {}),
        company=company,
        domain=domain,
        aiml_key=AIML_API_KEY,
        aiml_base_url=AIML_BASE_URL,
        aiml_model=AIML_MODEL,
        gemini_key=GEMINI_API_KEY,
    )

    step2["status"] = "completed"
    step2["data"] = research_result
    result["steps"].append(step2)

    if on_step:
        await on_step("research_analyst", step2)

    # ─── Step 3: Automated Outreach ──────────────────────────────────
    step3 = {
        "tool": "tool_outreach_automated_sender",
        "status": "running",
        "description": "Generating hyper-personalized email and sending...",
    }
    if on_step:
        await on_step("outreach_sender", step3)

    outreach_result = await tool_outreach_automated_sender(
        account_brief=research_result.get("account_brief", ""),
        signals=signals_result.get("signals", {}),
        icp=icp,
        recipient_email=recipient_email,
        aiml_key=AIML_API_KEY,
        aiml_base_url=AIML_BASE_URL,
        aiml_model=AIML_MODEL,
        gemini_key=GEMINI_API_KEY,
        brevo_key=BREVO_API_KEY,
        sender_email=SENDER_EMAIL,
    )

    step3["status"] = "completed"
    step3["data"] = outreach_result
    result["steps"].append(step3)

    if on_step:
        await on_step("outreach_sender", step3)

    # ─── Final Result ────────────────────────────────────────────────
    result["final_status"] = outreach_result.get("status", "unknown")
    result["summary"] = {
        "company": company,
        "signals_captured": bool(signals_result.get("signals")),
        "research_generated": research_result.get("status") == "success",
        "email_subject": outreach_result.get("subject", "N/A"),
        "email_status": outreach_result.get("status", "unknown"),
        "llm_used": outreach_result.get("llm_used", research_result.get("llm_used", "unknown")),
    }

    return result
