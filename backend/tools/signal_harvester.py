"""
Tool 1: Signal Harvester (Deterministic)
Fetches live buyer signals for a target company using free APIs.
NO LLM guessing — all data is from real API calls.
"""

import httpx
import re
from typing import Any


async def fetch_funding_signals(company: str, finnhub_key: str) -> dict:
    """Fetch funding/financial signals from Finnhub."""
    signals = {"source": "finnhub", "data": []}
    if not finnhub_key:
        signals["data"] = [{"note": "Finnhub API key not configured — skipped"}]
        return signals

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            # Search for company symbol
            resp = await client.get(
                "https://finnhub.io/api/v1/search",
                params={"q": company, "token": finnhub_key},
            )
            resp.raise_for_status()
            results = resp.json().get("result", [])

            if not results:
                signals["data"] = [{"note": f"No stock symbol found for '{company}'"}]
                return signals

            symbol = results[0].get("symbol", "")
            display_symbol = results[0].get("description", company)

            # Fetch company profile
            profile_resp = await client.get(
                "https://finnhub.io/api/v1/stock/profile2",
                params={"symbol": symbol, "token": finnhub_key},
            )
            profile = profile_resp.json() if profile_resp.status_code == 200 else {}

            # Fetch recent news
            news_resp = await client.get(
                "https://finnhub.io/api/v1/company-news",
                params={
                    "symbol": symbol,
                    "from": "2025-01-01",
                    "to": "2026-12-31",
                    "token": finnhub_key,
                },
            )
            news = news_resp.json()[:5] if news_resp.status_code == 200 else []

            signals["data"] = {
                "symbol": symbol,
                "company_name": display_symbol,
                "profile": {
                    "industry": profile.get("finnhubIndustry", "Unknown"),
                    "market_cap": profile.get("marketCapitalization", "N/A"),
                    "ipo_date": profile.get("ipo", "N/A"),
                    "website": profile.get("weburl", "N/A"),
                    "country": profile.get("country", "N/A"),
                    "employees": profile.get("employeeTotal", "N/A"),
                },
                "recent_news": [
                    {
                        "headline": n.get("headline", ""),
                        "summary": n.get("summary", "")[:200],
                        "source": n.get("source", ""),
                        "url": n.get("url", ""),
                        "datetime": n.get("datetime", ""),
                    }
                    for n in news
                ],
            }
        except Exception as e:
            signals["data"] = [{"error": f"Finnhub API error: {str(e)}"}]

    return signals


async def fetch_hiring_signals(company: str) -> dict:
    """Fetch hiring signals from direct ATS endpoints (Greenhouse, Lever)."""
    signals = {"source": "ats_direct", "data": []}

    slug = re.sub(r"[^a-z0-9]", "", company.lower().strip())
    ats_endpoints = [
        {
            "platform": "Greenhouse",
            "url": f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
        },
        {
            "platform": "Lever",
            "url": f"https://api.lever.co/v0/postings/{slug}",
        },
    ]

    jobs_found = []
    async with httpx.AsyncClient(timeout=10) as client:
        for endpoint in ats_endpoints:
            try:
                resp = await client.get(endpoint["url"])
                if resp.status_code == 200:
                    data = resp.json()
                    # Greenhouse format
                    if endpoint["platform"] == "Greenhouse":
                        raw_jobs = data.get("jobs", []) if isinstance(data, dict) else data
                    else:
                        raw_jobs = data if isinstance(data, list) else []

                    for job in raw_jobs[:10]:
                        title = job.get("title", job.get("text", "Unknown"))
                        location = ""
                        if endpoint["platform"] == "Greenhouse":
                            loc = job.get("location", {})
                            location = loc.get("name", "") if isinstance(loc, dict) else str(loc)
                        else:
                            loc_parts = job.get("categories", {}).get("location", "")
                            location = loc_parts

                        jobs_found.append({
                            "title": title,
                            "location": location,
                            "platform": endpoint["platform"],
                        })
            except Exception:
                continue

    if jobs_found:
        # Analyze hiring departments
        dept_counts: dict[str, int] = {}
        for job in jobs_found:
            title_lower = job["title"].lower()
            if any(kw in title_lower for kw in ["engineer", "developer", "software", "devops", "sre"]):
                dept_counts["Engineering"] = dept_counts.get("Engineering", 0) + 1
            elif any(kw in title_lower for kw in ["sales", "account", "business development", "sdr"]):
                dept_counts["Sales"] = dept_counts.get("Sales", 0) + 1
            elif any(kw in title_lower for kw in ["marketing", "content", "seo", "growth"]):
                dept_counts["Marketing"] = dept_counts.get("Marketing", 0) + 1
            elif any(kw in title_lower for kw in ["product", "pm", "design", "ux"]):
                dept_counts["Product/Design"] = dept_counts.get("Product/Design", 0) + 1
            else:
                dept_counts["Other"] = dept_counts.get("Other", 0) + 1

        signals["data"] = {
            "total_open_roles": len(jobs_found),
            "department_breakdown": dept_counts,
            "sample_roles": jobs_found[:5],
        }
    else:
        signals["data"] = {"total_open_roles": 0, "note": f"No ATS listings found for '{company}'"}

    return signals


async def fetch_news_signals(company: str, gnews_key: str) -> dict:
    """Fetch latest news signals from GNews API."""
    signals = {"source": "gnews", "data": []}

    if not gnews_key:
        signals["data"] = [{"note": "GNews API key not configured — skipped"}]
        return signals

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(
                "https://gnews.io/api/v4/search",
                params={
                    "q": company,
                    "lang": "en",
                    "max": 5,
                    "sortby": "publishedAt",
                    "apikey": gnews_key,
                },
            )
            resp.raise_for_status()
            articles = resp.json().get("articles", [])

            signals["data"] = [
                {
                    "title": a.get("title", ""),
                    "description": a.get("description", "")[:200],
                    "source": a.get("source", {}).get("name", ""),
                    "url": a.get("url", ""),
                    "published_at": a.get("publishedAt", ""),
                }
                for a in articles
            ]
        except Exception as e:
            signals["data"] = [{"error": f"GNews API error: {str(e)}"}]

    return signals


async def fetch_tech_stack(domain: str) -> dict:
    """Detect tech stack via HTTP headers and script inspection."""
    signals = {"source": "tech_detection", "data": {}}

    if not domain:
        signals["data"] = {"note": "No domain provided"}
        return signals

    # Clean domain
    if not domain.startswith("http"):
        domain = f"https://{domain}"

    detected: dict[str, list[str]] = {
        "hosting": [],
        "frameworks": [],
        "analytics": [],
        "cdn": [],
        "security": [],
        "other": [],
    }

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        try:
            resp = await client.get(domain)
            headers = dict(resp.headers)
            body = resp.text[:50000]  # First 50k chars

            # Header-based detection
            server = headers.get("server", "").lower()
            if "nginx" in server:
                detected["hosting"].append("Nginx")
            if "apache" in server:
                detected["hosting"].append("Apache")
            if "cloudflare" in headers.get("cf-ray", "") or "cloudflare" in server:
                detected["cdn"].append("Cloudflare")
            if "x-vercel" in headers or "vercel" in headers.get("server", "").lower():
                detected["hosting"].append("Vercel")
            if headers.get("x-powered-by", ""):
                detected["frameworks"].append(headers["x-powered-by"])

            # Body-based detection
            tech_patterns = {
                "React": [r"react", r"_react", r"__NEXT_DATA__"],
                "Next.js": [r"__NEXT_DATA__", r"_next/"],
                "Vue.js": [r"vue\.js", r"__vue__"],
                "Angular": [r"ng-version", r"angular"],
                "jQuery": [r"jquery"],
                "Google Analytics": [r"google-analytics\.com", r"gtag", r"UA-\d+"],
                "Google Tag Manager": [r"googletagmanager\.com"],
                "HubSpot": [r"hubspot", r"hs-scripts"],
                "Segment": [r"segment\.com", r"analytics\.js"],
                "Intercom": [r"intercom", r"widget\.intercom\.io"],
                "Stripe": [r"stripe\.com", r"js\.stripe"],
                "WordPress": [r"wp-content", r"wp-includes"],
                "Shopify": [r"shopify", r"cdn\.shopify"],
            }

            for tech, patterns in tech_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, body, re.IGNORECASE):
                        category = "analytics" if tech in ["Google Analytics", "Google Tag Manager", "Segment", "HubSpot"] else "frameworks"
                        if tech not in detected[category]:
                            detected[category].append(tech)
                        break

            signals["data"] = {k: v for k, v in detected.items() if v}
            if not signals["data"]:
                signals["data"] = {"note": "No technologies confidently detected"}

        except Exception as e:
            signals["data"] = {"error": f"Tech detection error: {str(e)}"}

    return signals


async def tool_signal_harvester(
    company: str,
    domain: str = "",
    finnhub_key: str = "",
    gnews_key: str = "",
) -> dict[str, Any]:
    """
    Main signal harvester tool. Fetches ALL signals for a target company.
    This is deterministic — no LLM guessing.
    """
    import asyncio

    funding, hiring, news, tech = await asyncio.gather(
        fetch_funding_signals(company, finnhub_key),
        fetch_hiring_signals(company),
        fetch_news_signals(company, gnews_key),
        fetch_tech_stack(domain),
    )

    return {
        "company": company,
        "domain": domain,
        "signals": {
            "financial": funding,
            "hiring": hiring,
            "news": news,
            "tech_stack": tech,
        },
    }
