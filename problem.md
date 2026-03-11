Agentic AI Developer
 Problem Statement

Case Study: FireReach – The Autonomous Outreach Engine
The Scenario
In the Rabbitt AI ecosystem, we’ve identified a major bottleneck: SDRs and GTM teams waste 70% of their day manually "stitching" data together. They find a funding lead on news, check a job board for hiring trends, and then spend 20 minutes drafting and sending an email.
Your lead developer has tasked you with building FireReach: a lightweight, autonomous outreach engine. This agent doesn't just write emails; it researches accounts based on live signals and automatically executes the outreach.
The Mission:
Build a single-feature Autonomous Outreach Prototype. The user provides their "ICP" (Ideal Customer Profile) and a target company. The system must capture live data, reason through it, generate a personalized campaign, and send the email automatically.
1. The Agentic Toolset (Required)
You must implement a Function Calling architecture where the agent utilizes exactly three tools to fulfill the request:
tool_signal_harvester (Deterministic): A tool that fetches data for a company Captures Live Buyer Signals
Track a small but high‑value subset of intent triggers (for specific target companies) such as: 
Funding rounds
Leadership changes 
Hiring trends
Website visits & page-level activity 
G2 category surges 
Competitor tool churn 
Keyword search intent 
Social mentions 
Tech stack changes 
Product usage signals (if available)
 Note: This tool must be deterministic (API/Search based); LLMs should not "guess" the signals.

tool_research_analyst (Account Insight): An AI tool that takes the harvested signals + the user's ICP to generate a 2-paragraph "Account Brief" highlighting specific pain points and strategic alignment.
tool_outreach_automated_sender (Execution): An AI-driven tool that transforms the research into a hyper-personalized email and automatically dispatches it using a mail service.



Functional Requirements
Sequential Reasoning: The agent must demonstrate a logical flow: Signal Capture → Contextual Research → Automated Delivery.
Zero-Template Policy: The email sent must explicitly reference the captured signals (e.g., "I noticed you're hiring for 5 new engineering roles...").
Automated Execution: The "Send" action should be a tool call triggered by the agent once it is satisfied with the research.
The Technical Stack
LLM: Google Gemini API or Groq (Llama 3) or any other API of your choice.
Backend/Frontend: FastAPI (Python) or Node.js with a minimal React dashboard.
The "Rabbitt" Challenge Prompt
To pass, your agent must successfully handle this scenario:
User ICP: "We sell high-end cybersecurity training to Series B startups."
Task: "Find companies with recent growth signals and send a personalized outreach email to [candidate-email-here] that connects their expansion to our security training."
Submission Deliverables
GitHub Repository: Clean code showing the tool definitions and agentic logic.
Live URL: A working link to the deployed prototype (Vercel/Render).
Agent Documentation (DOCS.md):
Logic Flow: How the agent ensures the outreach is grounded in the harvested signals.
Tool Schemas: Documentation for the three required function calls.
System Prompt: The "Persona" and "Constraint" prompt used to guide the agent.
Evaluation Rubric
Category
Focus
Tool Chaining
Does the agent successfully move from Signal → Research → Automated Sending?
Outreach Quality
Does the email feel "human" and accurately reference the live data?
Automation Flow
Does the mail tool trigger correctly with the right context?
UI/UX & Documentation
Is the output clear and is the agentic loop well-documented?


