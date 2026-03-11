"""
Tool 2: Research Analyst (Account Insight)
Takes harvested signals + ICP, performs its OWN internet research (web search + site scraping),
then generates a 2-paragraph Account Brief grounded in both API data and live web findings.
Primary: Claude 3.5 Sonnet via AIML API
Fallback: Google Gemini (free tier)
"""

import asyncio
import json
import re
import httpx
from openai import AsyncOpenAI
import google.generativeai as genai

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None


# ─── Internet Research Functions ─────────────────────────────────────────────

async def _web_search(query: str, max_results: int = 5) -> list[dict]:
    """Search the web via DuckDuckGo and extract result snippets."""
    results = []
    if DDGS is None:
        return [{"error": "duckduckgo-search package not installed"}]

    try:
        # Run synchronous DDGS in a thread to avoid blocking
        def _search():
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=max_results))

        raw = await asyncio.to_thread(_search)
        for r in raw:
            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "url": r.get("href", ""),
            })
    except Exception as e:
        results.append({"error": f"Web search failed: {str(e)}"})
    return results


async def _scrape_company_site(domain: str) -> dict:
    """Scrape a company's homepage and about page for context."""
    site_info = {"homepage": "", "about": ""}
    if not domain:
        return site_info

    clean_domain = domain.strip().rstrip("/")
    if not clean_domain.startswith("http"):
        clean_domain = f"https://{clean_domain}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        # Fetch homepage
        try:
            resp = await client.get(clean_domain, headers=headers)
            if resp.status_code == 200 and BeautifulSoup:
                soup = BeautifulSoup(resp.text, "html.parser")
                # Extract meta description
                meta_desc = soup.find("meta", attrs={"name": "description"})
                desc = meta_desc["content"] if meta_desc and meta_desc.get("content") else ""
                # Extract og:description as fallback
                if not desc:
                    og_desc = soup.find("meta", attrs={"property": "og:description"})
                    desc = og_desc["content"] if og_desc and og_desc.get("content") else ""
                # Extract title
                title = soup.title.get_text(strip=True) if soup.title else ""
                # Extract main heading text
                headings = " | ".join(
                    h.get_text(strip=True) for h in soup.find_all(["h1", "h2"], limit=5) if h.get_text(strip=True)
                )
                site_info["homepage"] = f"Title: {title}. Description: {desc}. Headings: {headings}"[:800]
        except Exception:
            pass

        # Fetch about page (try common paths)
        for path in ["/about", "/about-us", "/company", "/about/"]:
            try:
                resp = await client.get(f"{clean_domain}{path}", headers=headers)
                if resp.status_code == 200 and BeautifulSoup:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    # Remove scripts/styles
                    for tag in soup(["script", "style", "nav", "footer", "header"]):
                        tag.decompose()
                    text = soup.get_text(separator=" ", strip=True)
                    # Clean and truncate
                    text = re.sub(r"\s+", " ", text)[:1200]
                    if len(text) > 100:
                        site_info["about"] = text
                        break
            except Exception:
                continue

    return site_info


async def perform_web_research(company: str, domain: str, icp: str) -> dict:
    """
    Perform independent internet research about the company.
    Runs web searches and website scraping in parallel.
    """
    # Build targeted search queries
    search_tasks = [
        _web_search(f'"{company}" company news funding 2025 2026'),
        _web_search(f'"{company}" {_extract_icp_keywords(icp)}'),
        _scrape_company_site(domain),
    ]

    search_results, icp_results, site_data = await asyncio.gather(*search_tasks)

    return {
        "web_search_general": search_results,
        "web_search_icp_aligned": icp_results,
        "company_website": site_data,
    }


def _extract_icp_keywords(icp: str) -> str:
    """Extract the most relevant keywords from the ICP for targeted searching."""
    # Remove common filler words, keep the meaty terms
    stop_words = {
        "we", "sell", "to", "the", "a", "an", "and", "or", "for", "of",
        "in", "on", "at", "our", "is", "are", "that", "this", "with",
    }
    words = icp.lower().split()
    keywords = [w.strip(".,;:!?\"'") for w in words if w.strip(".,;:!?\"'") not in stop_words]
    return " ".join(keywords[:8])


# ─── LLM Prompt & Calls ─────────────────────────────────────────────────────

RESEARCH_SYSTEM_PROMPT = """You are an elite B2B account research analyst at FireReach.
Your job is to analyze raw buyer signals AND independent web research findings to create
a concise, actionable Account Brief.

You have access to THREE data sources:
A) API-harvested signals (financial, hiring, news, tech stack)
B) Live web search results (DuckDuckGo snippets about the company)
C) Company website content (homepage/about page text)

RULES:
1. Write EXACTLY 2 paragraphs.
2. Paragraph 1: Summarize the company's current situation using ALL available data sources.
   Cross-reference API signals with web search findings for richer context.
   Reference specific data points (funding amounts, hiring numbers, news events, tech stack,
   and any additional insights found via web search).
3. Paragraph 2: Connect the company's situation to the user's ICP. Identify specific pain points
   and explain the strategic alignment — why THIS company needs what the ICP offers RIGHT NOW.
   Use web research findings to strengthen the argument.
4. Be specific, not generic. Use actual numbers and signal data.
5. Do NOT invent data. Only reference information that was actually provided in the sources.
6. Clearly distinguish between confirmed API data and web search findings.
7. Write in a professional, analytical tone."""


def _build_user_prompt(icp: str, signals: dict, web_research: dict = None) -> str:
    prompt = f"""Analyze ALL available data sources for this target company and create an Account Brief.

USER'S ICP (Ideal Customer Profile):
{icp}

═══ SOURCE A: API-HARVESTED SIGNALS ═══
{json.dumps(signals, indent=2, default=str)}
"""

    if web_research:
        general_results = web_research.get("web_search_general", [])
        icp_results = web_research.get("web_search_icp_aligned", [])
        site_data = web_research.get("company_website", {})

        prompt += f"""
═══ SOURCE B: LIVE WEB SEARCH RESULTS ═══
General company search:
{json.dumps(general_results, indent=2, default=str)}

ICP-aligned search:
{json.dumps(icp_results, indent=2, default=str)}

═══ SOURCE C: COMPANY WEBSITE CONTENT ═══
Homepage: {site_data.get('homepage', 'N/A')}
About page: {site_data.get('about', 'N/A')}
"""

    prompt += """
Write a 2-paragraph Account Brief:
- Paragraph 1: Company situation analysis (cross-reference all data sources)
- Paragraph 2: Strategic alignment with the user's ICP and specific pain points"""

    return prompt


async def _call_claude(user_prompt: str, aiml_key: str, aiml_base_url: str, aiml_model: str) -> str:
    """Call Claude 3.5 Sonnet via AIML API."""
    client = AsyncOpenAI(api_key=aiml_key, base_url=aiml_base_url)

    response = await client.chat.completions.create(
        model=aiml_model,
        messages=[
            {"role": "system", "content": RESEARCH_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1024,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()


async def _call_gemini(user_prompt: str, gemini_key: str) -> str:
    """Fallback: Call Google Gemini."""
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    response = model.generate_content(
        [
            {"role": "user", "parts": [{"text": RESEARCH_SYSTEM_PROMPT}]},
            {"role": "model", "parts": [{"text": "Understood. I will analyze all data sources and create a precise, data-driven Account Brief."}]},
            {"role": "user", "parts": [{"text": user_prompt}]},
        ]
    )

    return response.text.strip()


# ─── Main Tool Entry Point ───────────────────────────────────────────────────

async def tool_research_analyst(
    icp: str,
    signals: dict,
    company: str = "",
    domain: str = "",
    aiml_key: str = "",
    aiml_base_url: str = "https://api.aimlapi.com/v1",
    aiml_model: str = "claude-3-5-sonnet-latest",
    gemini_key: str = "",
) -> dict:
    """
    Generate a 2-paragraph Account Brief from ICP + harvested signals + independent web research.
    Performs its own internet searching to enrich the analysis beyond API-only data.
    Primary: Claude 3.5 Sonnet via AIML API
    Fallback: Google Gemini (free tier)
    """
    # Phase 1: Perform independent web research (parallel with no LLM cost)
    web_research = None
    if company:
        try:
            print(f"🔍 Research analyst performing independent web research for '{company}'...")
            web_research = await perform_web_research(company, domain, icp)
            print(f"✅ Web research complete — found {len(web_research.get('web_search_general', []))} general results, "
                  f"{len(web_research.get('web_search_icp_aligned', []))} ICP-aligned results")
        except Exception as e:
            print(f"⚠️ Web research failed (non-fatal): {e}")
            web_research = None

    # Phase 2: Build enriched prompt and call LLM
    user_prompt = _build_user_prompt(icp, signals, web_research)
    llm_used = ""

    # Try primary: Claude via AIML API
    if aiml_key:
        try:
            account_brief = await _call_claude(user_prompt, aiml_key, aiml_base_url, aiml_model)
            llm_used = "Claude 3.5 Sonnet (via AIML API)"
            return {
                "account_brief": account_brief,
                "status": "success",
                "llm_used": llm_used,
                "icp_used": icp,
                "web_research_performed": web_research is not None,
            }
        except Exception as e:
            print(f"⚠️ AIML API failed: {e}. Falling back to Gemini...")

    # Fallback: Google Gemini
    if gemini_key:
        try:
            account_brief = await _call_gemini(user_prompt, gemini_key)
            llm_used = "Google Gemini 2.0 Flash (fallback)"
            return {
                "account_brief": account_brief,
                "status": "success",
                "llm_used": llm_used,
                "icp_used": icp,
                "web_research_performed": web_research is not None,
            }
        except Exception as e:
            return {
                "account_brief": f"Both LLMs failed. AIML error + Gemini error: {str(e)}",
                "status": "error",
            }

    return {
        "account_brief": "⚠️ No LLM API key configured. Set AIML_API_KEY or GEMINI_API_KEY in .env",
        "status": "error",
    }
