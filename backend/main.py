"""
ReachAI Backend API Server
FastAPI application with endpoints for the autonomous outreach engine.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
import json
import asyncio
from contextlib import asynccontextmanager

from config import APP_HOST, APP_PORT, FRONTEND_URL
from agent import run_agent_pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✨ ReachAI is starting up...")
    yield
    print("✨ ReachAI is shutting down...")


app = FastAPI(
    title="ReachAI — Autonomous Outreach Engine",
    description="An AI-powered agent that captures buyer signals, generates research, and sends personalized outreach.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OutreachRequest(BaseModel):
    sender_name: str
    icp: str
    company: str
    domain: str = ""
    recipient_email: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@app.get("/", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        service="ReachAI Autonomous Outreach Engine",
        version="1.0.0",
    )


@app.post("/api/outreach")
async def run_outreach(request: OutreachRequest):
    """
    Run the full ReachAI outreach pipeline.
    Sequential flow: Signal Capture → Research → Automated Email.
    """
    try:
        result = await run_agent_pipeline(
            sender_name=request.sender_name,
            icp=request.icp,
            company=request.company,
            domain=request.domain,
            recipient_email=request.recipient_email,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/outreach/stream")
async def run_outreach_stream(request: OutreachRequest):
    """
    Stream the outreach pipeline — sends SSE events for each step.
    """
    async def event_generator():
        steps_collected = []

        async def on_step(step_name, step_data):
            event = {
                "step": step_name,
                "status": step_data.get("status", ""),
                "description": step_data.get("description", ""),
            }
            if step_data.get("status") == "completed":
                event["data"] = step_data.get("data", {})
            yield f"data: {json.dumps(event, default=str)}\n\n"

        # We can't use on_step as an async generator callback easily,
        # so we'll run the pipeline and yield results step by step
        from tools.signal_harvester import tool_signal_harvester
        from tools.research_analyst import tool_research_analyst
        from tools.outreach_sender import tool_outreach_automated_sender
        from config import AIML_API_KEY, AIML_BASE_URL, AIML_MODEL, GEMINI_API_KEY, FINNHUB_API_KEY, GNEWS_API_KEY

        # Step 1
        yield f"data: {json.dumps({'step': 'signal_harvester', 'status': 'running', 'description': 'Capturing live buyer signals...'})}\n\n"

        signals_result = await tool_signal_harvester(
            company=request.company,
            domain=request.domain,
            finnhub_key=FINNHUB_API_KEY,
            gnews_key=GNEWS_API_KEY,
        )

        yield f"data: {json.dumps({'step': 'signal_harvester', 'status': 'completed', 'data': signals_result}, default=str)}\n\n"

        # Step 2
        yield f"data: {json.dumps({'step': 'research_analyst', 'status': 'running', 'description': 'Performing web research & analyzing signals...'})}\n\n"

        research_result = await tool_research_analyst(
            icp=request.icp,
            signals=signals_result.get("signals", {}),
            company=request.company,
            domain=request.domain,
            aiml_key=AIML_API_KEY,
            aiml_base_url=AIML_BASE_URL,
            aiml_model=AIML_MODEL,
            gemini_key=GEMINI_API_KEY,
        )

        yield f"data: {json.dumps({'step': 'research_analyst', 'status': 'completed', 'data': research_result}, default=str)}\n\n"

        # Step 3
        yield f"data: {json.dumps({'step': 'outreach_sender', 'status': 'running', 'description': 'Generating personalized email...'})}\n\n"

        outreach_result = await tool_outreach_automated_sender(
            sender_name=request.sender_name,
            account_brief=research_result.get("account_brief", ""),
            signals=signals_result.get("signals", {}),
            icp=request.icp,
            recipient_email=request.recipient_email,
            aiml_key=AIML_API_KEY,
            aiml_base_url=AIML_BASE_URL,
            aiml_model=AIML_MODEL,
            gemini_key=GEMINI_API_KEY,
        )

        yield f"data: {json.dumps({'step': 'outreach_sender', 'status': 'completed', 'data': outreach_result}, default=str)}\n\n"

        # Final
        yield f"data: {json.dumps({'step': 'complete', 'status': 'done'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


if __name__ == "__main__":
    import uvicorn
    import os as _os
    is_dev = _os.getenv("RENDER") is None
    uvicorn.run("main:app", host=APP_HOST, port=int(APP_PORT), reload=is_dev)
