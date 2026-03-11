"""
FireReach Agent Orchestrator
Implements sequential function-calling: Signal Capture → Research → Automated Delivery.
Uses Gemini for reasoning, but tool execution is deterministic where required.
"""

import json
from tools.signal_harvester import tool_signal_harvester
from tools.research_analyst import tool_research_analyst
from tools.outreach_sender import tool_outreach_automated_sender
from config import GEMINI_API_KEY, FINNHUB_API_KEY, GNEWS_API_KEY, RESEND_API_KEY, SENDER_EMAIL


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
    2. tool_research_analyst → AI analysis
    3. tool_outreach_automated_sender → AI email gen + automated send
    
    Args:
        icp: User's Ideal Customer Profile description
        company: Target company name
        domain: Target company's website domain
        recipient_email: Email to send the outreach to
        on_step: Optional async callback(step_name, step_data) for streaming updates
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
        "description": "Analyzing signals and generating Account Brief...",
    }
    if on_step:
        await on_step("research_analyst", step2)

    research_result = await tool_research_analyst(
        icp=icp,
        signals=signals_result.get("signals", {}),
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
        "description": "Generating and sending personalized email...",
    }
    if on_step:
        await on_step("outreach_sender", step3)

    outreach_result = await tool_outreach_automated_sender(
        account_brief=research_result.get("account_brief", ""),
        signals=signals_result.get("signals", {}),
        icp=icp,
        recipient_email=recipient_email,
        gemini_key=GEMINI_API_KEY,
        resend_key=RESEND_API_KEY,
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
    }

    return result
