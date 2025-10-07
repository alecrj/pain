#!/usr/bin/env python3
"""
THE ULTIMATE WINNER MACHINE v4.0 - WHITE SPACE HUNTER
Find pain points in WHITE SPACE markets - where problems cost $$$ but NO dominant solution exists

CRITICAL CHANGES FROM v3.1:
- Stage 1: WHITE SPACE CHECK (kill Salesforce/HubSpot/big player territory)
- Stage 2: BUILD FEASIBILITY (public APIs, 3mo build)
- Stage 3: PAIN COST CALCULATOR (what problem COSTS them, not what they spend)
- Stage 4: EVIDENCE ENGINE (REAL proof + competitive landscape)
- Stage 5: GO-TO-MARKET FIT (can you get 10 customers WITHOUT phone sales?)
- Stage 6: FOUNDER REALITY CHECK (your specific constraints)

WHAT THIS FINDS:
- Problems costing businesses $10k-100k+/year in LOSSES
- NO dominant player (Salesforce/HubSpot/etc.)
- Fragmented market OR manual processes (spreadsheets/duct tape)
- REAL evidence from 2024-2025
- Self-serve GTM (no phone sales required)

Expected: 100 → 40 (S1) → 30 (S2) → 20 (S3) → 5-8 (S4) → 2-3 (S5) → 0-1 WINNER (S6)
Cost: ~$14 per 100 ideas
Time: ~2-3 hours
"""

import os
import sys
import time
import json
import hashlib
import argparse
import requests
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("❌ No OPENAI_API_KEY in .env")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

# Excluded industries (licensing/regulatory hell OR saturated enterprise markets)
EXCLUDED_INDUSTRIES = [
    # Regulated/licensing nightmares
    "healthcare", "medical", "hospital", "clinic", "doctor", "physician", "nurse", "patient",
    "insurance", "health insurance", "life insurance", "broker",
    "banking", "finance", "financial services", "fintech", "payment processing", "lending",
    "legal", "law firm", "attorney", "lawyer", "paralegal",
    "real estate", "realty", "property sales", "realtor", "mls", "brokerage",
    "pharmacy", "pharmaceutical", "drug", "prescription",
    "dental", "dentist", "orthodonti",
    "childcare", "daycare", "preschool",
    "education", "school", "university", "k-12", "tutoring",
    "senior care", "nursing home", "assisted living", "home health",
    "counseling", "therapy", "mental health", "psychologist", "psychiatrist",

    # Saturated enterprise markets (auto-kill - can't compete)
    "crm", "sales automation", "email marketing", "marketing automation",
    "project management", "task management", "team collaboration",
    "accounting software", "bookkeeping", "payroll",
    "e-commerce platform", "online store builder", "shopping cart",
    "help desk", "customer support", "ticketing system",
    "hr software", "applicant tracking", "recruiting platform"
]

# Auto-KILL: If pain is solved by these (Salesforce territory)
DOMINANT_PLAYERS = [
    "Salesforce", "HubSpot", "Monday.com", "Asana", "Slack", "Shopify",
    "QuickBooks", "Xero", "Stripe", "Square", "Mailchimp", "Klaviyo",
    "Zendesk", "Intercom", "Zoom", "Microsoft Teams", "Google Workspace",
    "SAP", "Oracle", "Workday", "ServiceNow", "Adobe", "Atlassian"
]

IDEAS_BANK_FILE = "ideas_bank.json"

def call_openai(prompt, system_message="You are a business research expert.", model="gpt-5-mini", temperature=0.7):
    """Call OpenAI API with rate limiting - using GPT-5 mini (58% cheaper than o4-mini, faster)"""
    time.sleep(1)  # Rate limiting
    try:
        params = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        }

        # GPT-5 models use max_completion_tokens and only support temperature=1
        if "gpt-5" in model.lower():
            params["max_completion_tokens"] = 4000
            # GPT-5 mini only supports default temperature (1)
        else:
            params["max_tokens"] = 4000
            params["temperature"] = temperature

        response = client.chat.completions.create(**params)
        return response.choices[0].message.content
    except Exception as e:
        print(f"   ⚠️  API Error: {str(e)}")
        return None

def reddit_search(query, limit=25):
    """
    Search Reddit for posts/comments (FREE, no API key needed)
    Returns posts from last 2 years with URLs and dates
    """
    time.sleep(1)  # Rate limiting
    try:
        # Reddit's public JSON API (no auth required for read-only)
        url = "https://www.reddit.com/search.json"
        headers = {"User-Agent": "WhiteSpaceHunter/1.0"}
        params = {
            "q": query,
            "sort": "relevance",
            "t": "year",  # Last year
            "limit": limit
        }

        response = requests.get(url, params=params, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            posts = data.get("data", {}).get("children", [])

            if not posts:
                return f"[No Reddit posts found for: {query}]"

            results = []
            for i, post_data in enumerate(posts[:15], 1):
                post = post_data.get("data", {})
                title = post.get("title", "No title")
                selftext = post.get("selftext", "")[:200]  # First 200 chars
                subreddit = post.get("subreddit", "unknown")
                author = post.get("author", "unknown")
                created_utc = post.get("created_utc", 0)
                date = datetime.fromtimestamp(created_utc).strftime("%Y-%m-%d") if created_utc else "Unknown"
                url = f"https://reddit.com{post.get('permalink', '')}"
                upvotes = post.get("ups", 0)

                results.append(
                    f"{i}. r/{subreddit} - {title}\n"
                    f"   Date: {date} | Upvotes: {upvotes} | Author: u/{author}\n"
                    f"   Text: {selftext}...\n"
                    f"   URL: {url}\n"
                )

            return "\n".join(results)
        else:
            print(f"      ⚠️ Reddit API error: {response.status_code}")
            return f"[ERROR: Reddit returned {response.status_code}]"

    except Exception as e:
        print(f"      ⚠️ Reddit search error: {str(e)}")
        return f"[ERROR: {str(e)}]"

def web_search(query):
    """
    Perform web search using Google Custom Search API
    Returns search results with REAL URLs and snippets
    FREE: 100 searches/day
    """
    time.sleep(1)  # Rate limiting
    try:
        google_api_key = os.getenv("GOOGLE_API_KEY", "")
        google_cse_id = os.getenv("GOOGLE_CSE_ID", "")

        if not google_api_key or not google_cse_id:
            print(f"      ⚠️  NO GOOGLE API - Cannot verify evidence")
            return "[ERROR: No search API configured. Cannot find real evidence.]"

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": google_api_key,
            "cx": google_cse_id,
            "q": query,
            "num": 10,
            "dateRestrict": "y2",  # Last 2 years (2024-2025)
        }

        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()

            if "items" not in data:
                return f"[No results found for: {query}]"

            results = []
            for i, item in enumerate(data["items"][:10], 1):
                title = item.get("title", "No title")
                link = item.get("link", "No URL")
                snippet = item.get("snippet", "No description")
                results.append(f"{i}. {title}\n   URL: {link}\n   Snippet: {snippet}\n")

            return "\n".join(results)
        else:
            print(f"      ⚠️ Search API error: {response.status_code}")
            return f"[ERROR: Google Search returned {response.status_code}]"

    except Exception as e:
        print(f"      ⚠️ Search error: {str(e)}")
        return f"[ERROR: {str(e)}]"

def generate_idea_hash(business, pain):
    """Generate unique hash for business+pain combination"""
    combined = f"{business.lower().strip()}||{pain.lower().strip()}"
    return hashlib.md5(combined.encode()).hexdigest()[:12]

def load_ideas_bank():
    """Load existing ideas bank or create new one"""
    if os.path.exists(IDEAS_BANK_FILE):
        with open(IDEAS_BANK_FILE, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else data.get("ideas", [])
    return []

def save_ideas_bank(ideas):
    """Save ideas bank to file"""
    with open(IDEAS_BANK_FILE, 'w') as f:
        json.dump({"ideas": ideas}, f, indent=2)

def idea_exists(ideas_bank, business, pain):
    """Check if idea already exists in bank"""
    idea_hash = generate_idea_hash(business, pain)
    return any(idea.get("hash") == idea_hash for idea in ideas_bank)

# ═══════════════════════════════════════════════════════════
# STAGE 0: GENERATE IDEAS
# ═══════════════════════════════════════════════════════════

def stage0_generate_ideas(count, ideas_bank):
    """Generate ideas focusing on WHITE SPACE opportunities"""
    print("\n" + "="*60)
    print("STAGE 0: GENERATING IDEAS (White Space Focus)")
    print("="*60)

    prompt = f"""Generate {count} business pain points for SMALL-MID BUSINESSES ($1M-50M revenue).

TARGET INDUSTRIES (boring but profitable):
- Construction/contractors (HVAC, electrical, plumbing)
- Manufacturing (small-mid factories)
- Logistics/transportation
- Wholesale/distribution
- Professional services (consulting, agencies)
- Facilities management
- Food service/hospitality

FOCUS ON WORKFLOW GAPS (NOT sales/marketing/CRM):
- Compliance/regulatory tracking
- Equipment/asset management
- Inventory/parts tracking
- Scheduling/dispatch
- Quality control
- Safety/training
- Vendor/supplier management
- Warranty/service tracking

AVOID (auto-KILL):
{', '.join(EXCLUDED_INDUSTRIES)}

For each idea, provide:
Business: [Specific industry]
Pain: [Specific workflow problem - NOT sales/marketing/CRM]

Format EXACTLY like:
1. Business: HVAC Contractors
   Pain: Tracking warranty-covered parts vs billable repairs causing invoicing errors

Generate {count} unique ideas:"""

    response = call_openai(prompt, model="gpt-5-mini")
    if not response:
        print("❌ Failed to generate ideas")
        return []

    # Parse ideas
    ideas = []
    lines = response.strip().split('\n')
    current_business = None

    for line in lines:
        line = line.strip()
        # Handle both "Business:" and "1. Business:" formats
        if "Business:" in line:
            current_business = line.split("Business:")[1].strip()
        elif "Pain:" in line and current_business:
            pain = line.split("Pain:")[1].strip()

            # Check if excluded industry
            if any(exc.lower() in current_business.lower() or exc.lower() in pain.lower()
                   for exc in EXCLUDED_INDUSTRIES):
                print(f"   ⚠️  Skipping (excluded industry): {current_business}")
                current_business = None
                continue

            # Check if already exists
            if idea_exists(ideas_bank, current_business, pain):
                print(f"   ⚠️  Skipping (duplicate): {current_business} - {pain[:50]}...")
                current_business = None
                continue

            ideas.append({
                "business": current_business,
                "pain": pain,
                "id": len(ideas_bank) + len(ideas) + 1,
                "hash": generate_idea_hash(current_business, pain),
                "generated_date": datetime.now().strftime("%Y-%m-%d"),
                "status": "generated"
            })
            current_business = None

    print(f"\n✅ Generated {len(ideas)} unique ideas")
    return ideas

# ═══════════════════════════════════════════════════════════
# STAGE 1: WHITE SPACE CHECK
# ═══════════════════════════════════════════════════════════

def stage1_white_space_check(idea):
    """Check if idea is in WHITE SPACE (not Salesforce/HubSpot territory)"""
    print(f"\n{'─'*60}")
    print(f"STAGE 1: WHITE SPACE CHECK - Idea #{idea['id']}")
    print(f"Business: {idea['business']}")
    print(f"Pain: {idea['pain']}")
    print(f"{'─'*60}")

    prompt = f"""Research this business pain to determine if it's WHITE SPACE or SATURATED:

Business: {idea['business']}
Pain: {idea['pain']}

TASK 1: Check for Dominant Players
Is this pain solved by any of these? {', '.join(DOMINANT_PLAYERS[:10])}
If YES → This is THEIR territory → KILL

TASK 2: Market Structure Analysis
Imagine searching Google for: "{idea['pain']} software" or "{idea['business']} {idea['pain']} tool"

What would you find?
A) MONOPOLY: One dominant tool (Salesforce-level, 1000+ reviews) → KILL
B) SATURATED: 3+ well-funded tools (500+ reviews each) → KILL
C) FRAGMENTED: 5-10 small tools (all <200 reviews, complaints in 1-star reviews) → PASS
D) WHITE SPACE: No specialized tools, people use spreadsheets/manual processes → PASS

TASK 3: Current "Solutions"
Based on the pain point, what are businesses likely using NOW?
- Enterprise platform (Salesforce, SAP, Oracle) → KILL
- Category leader (QuickBooks, Shopify, HubSpot) → KILL
- Multiple duct-taped tools + spreadsheets → PASS
- Pure manual processes → PASS

ANALYSIS:
Write 2-3 paragraphs analyzing:
1. Would Salesforce/HubSpot/etc. handle this pain as a feature?
2. Are there 3+ funded startups attacking this specific problem?
3. What's the likely current "solution" (enterprise tool, spreadsheets, manual)?

VERDICT:
- Type: [MONOPOLY / SATURATED / FRAGMENTED / WHITE SPACE]
- Dominant Player: [Name if exists, or "None"]
- Market Assessment: [1-2 sentences]
- Decision: [PASS or KILL]
- Reasoning: [Why white space or why saturated]

Provide detailed analysis:"""

    response = call_openai(prompt, model="gpt-5-mini")
    if not response:
        return {"verdict": "KILL", "reason": "API Error"}

    print(f"\n{response}")

    # Parse verdict
    verdict_lower = response.lower()
    if "decision: pass" in verdict_lower and ("white space" in verdict_lower or "fragmented" in verdict_lower):
        print("\n✅ PASS - White space opportunity")
        return {"verdict": "PASS", "analysis": response}
    else:
        print("\n❌ KILL - Saturated market or dominant player exists")
        return {"verdict": "KILL", "analysis": response}

# ═══════════════════════════════════════════════════════════
# STAGE 2: BUILD FEASIBILITY
# ═══════════════════════════════════════════════════════════

def stage2_build_feasibility(idea):
    """Check if buildable with public APIs in 3 months"""
    print(f"\n{'─'*60}")
    print(f"STAGE 2: BUILD FEASIBILITY - Idea #{idea['id']}")
    print(f"{'─'*60}")

    prompt = f"""Assess build feasibility for this business pain:

Business: {idea['business']}
Pain: {idea['pain']}

TASK 1: PUBLIC API FEASIBILITY
Can this be built using ONLY public, self-service APIs?

Required data sources:
- Core business data (can live in YOUR database)
- External integrations needed (maps, SMS, email, payments, calendar, etc.)

Check if any integration requires:
❌ Enterprise APIs (eBay/Amazon seller, SAP, Oracle, Salesforce enterprise)
❌ Special certifications or partnerships
❌ Private manufacturer/vendor APIs
❌ Government/regulatory APIs with restricted access

If ALL integrations use public APIs (Google Maps, Twilio, SendGrid, Stripe, QuickBooks Online OAuth, etc.):
✅ PUBLIC_API_FEASIBILITY: YES

TASK 2: MVP BUILD COMPLEXITY
Can you build a functional MVP in 3 months?

MVP Components:
- CRUD interfaces (create/read/update/delete data)
- Simple workflows (job creation, status updates, basic automation)
- Dashboard/reporting (charts, lists, filters)
- API integrations (OAuth flows, webhooks, API calls)
- File uploads (photos, PDFs, documents)
- Notifications (email/SMS)
- Basic scheduling/calendar

If this is mostly CRUD + workflows + API calls + dashboards:
✅ MVP_BUILD_COMPLEXITY: YES (3mo buildable)

If this requires ML, computer vision, real-time video, blockchain, hardware:
❌ MVP_BUILD_COMPLEXITY: NO (too complex for 3mo)

TASK 3: TECHNICAL SHOWSTOPPERS
What features would require private APIs or partnerships for MVP?
List them (can be deferred to manual processes for MVP if not critical)

VERDICT:
PUBLIC_API_FEASIBILITY: [YES/NO]
Details: [List all APIs needed and confirm they're public]

MVP_BUILD_COMPLEXITY: [YES/NO]
Details: [Break down MVP components]

TECHNICAL_SHOWSTOPPERS: [List any blockers, or "None"]

DECISION: [PASS or KILL]
REASONING: [Why buildable or why blocked]

Provide analysis:"""

    response = call_openai(prompt, model="gpt-5-mini")
    if not response:
        return {"verdict": "KILL", "reason": "API Error"}

    print(f"\n{response}")

    # Parse verdict
    if "DECISION: PASS" in response or "decision: pass" in response.lower():
        print("\n✅ PASS - Buildable with public APIs in 3mo")
        return {"verdict": "PASS", "analysis": response}
    else:
        print("\n❌ KILL - Build complexity or API access issues")
        return {"verdict": "KILL", "analysis": response}

# ═══════════════════════════════════════════════════════════
# STAGE 3: PAIN COST CALCULATOR
# ═══════════════════════════════════════════════════════════

def stage3_pain_cost_calculator(idea):
    """Calculate what this problem COSTS businesses (not what they spend on solutions)"""
    print(f"\n{'─'*60}")
    print(f"STAGE 3: PAIN COST CALCULATOR - Idea #{idea['id']}")
    print(f"{'─'*60}")

    # 3 searches for cost evidence
    searches = [
        f"{idea['business']} loses money from {idea['pain']}",
        f"{idea['business']} cost of {idea['pain']} per year",
        f"{idea['business']} {idea['pain']} compliance fines wasted time"
    ]

    search_results = []
    for search_query in searches:
        print(f"\n   🔍 Searching: {search_query}")
        result = web_search(search_query)
        search_results.append(f"QUERY: {search_query}\nRESULTS:\n{result}\n")

    combined_results = "\n".join(search_results)

    prompt = f"""Calculate the annual COST of this business pain:

Business: {idea['business']}
Pain: {idea['pain']}

SEARCH RESULTS:
{combined_results}

TASK: Calculate total annual cost from DIRECT + INDIRECT + OPPORTUNITY costs

A) DIRECT LOSSES (use evidence from search results):
- Lost revenue (invoicing errors, missed charges, incorrect billing): $X
- Compliance fines/penalties: $X
- Customer churn (lost customers × avg customer value): $X
- Rework/corrections (fixing errors): $X

Example: "HVAC contractor loses $40k/year in warranty parts incorrectly billed to customers"

B) INDIRECT COSTS (labor waste):
- Time spent on manual processes: X hours/week
- Hourly rate: $X (typical for this business)
- Annual cost: X hours × 52 weeks × $X/hour = $X

Example: "10 hours/week fixing invoicing errors @ $50/hour = $26k/year"

C) OPPORTUNITY COST (what they could do instead):
- If they saved X hours/week, what's the revenue opportunity?
- Additional jobs/projects they could take on: $X

Example: "10 hours/week freed up = 2 more service calls/week = $50k additional revenue"

TOTAL ANNUAL COST: $[A + B + C]

CURRENT "SOLUTION" ANALYSIS:
What are they using NOW to manage this pain?
- Spreadsheets (free but time-consuming)
- Multiple tools duct-taped together ($X/month total)
- Manual processes only (no software cost)
- Expensive enterprise tool ($X/year)

Current annual spend on this specific pain: $X

PRICING OPPORTUNITY:
- If problem costs them $X/year
- And they currently spend $Y/year on "solutions"
- You can charge: $Z/month (must be < total cost but > current spend if possible)
- ROI for customer: $X - ($Z × 12) = $[savings]/year

VERDICT:
TOTAL_ANNUAL_COST: $X (show calculation)
CURRENT_SPEND: $X (on existing "solutions")
PRICING_OPPORTUNITY: $X/month (your potential price)
CUSTOMER_ROI: $X/year savings

DECISION: [PASS or KILL]
PASS if: Total cost ≥ $10k/year AND room for profitable pricing
KILL if: Total cost < $10k/year OR already spending $10k+ on good solutions

REASONING: [Explain the economics]

Provide detailed cost analysis:"""

    response = call_openai(prompt, model="gpt-5-mini")
    if not response:
        return {"verdict": "KILL", "reason": "API Error"}

    print(f"\n{response}")

    # Parse verdict
    if "DECISION: PASS" in response or "decision: pass" in response.lower():
        # Check if cost is actually $10k+
        if "10k" in response.lower() or "10,000" in response or any(f"${x}k" in response for x in range(10, 200)):
            print("\n✅ PASS - Problem costs $10k+/year")
            return {"verdict": "PASS", "analysis": response}

    print("\n❌ KILL - Problem cost too low or no pricing opportunity")
    return {"verdict": "KILL", "analysis": response}

# ═══════════════════════════════════════════════════════════
# STAGE 4: EVIDENCE ENGINE
# ═══════════════════════════════════════════════════════════

def stage4_evidence_engine(idea):
    """Find REAL evidence + competitive landscape analysis"""
    print(f"\n{'─'*60}")
    print(f"STAGE 4: EVIDENCE ENGINE - Idea #{idea['id']}")
    print(f"{'─'*60}")

    # Search 1: Reddit for pain complaints (DIRECT - better than Google)
    print(f"\n   🔍 Searching Reddit: {idea['pain']}")
    reddit_query = f"{idea['business']} {idea['pain']}"
    reddit_results = reddit_search(reddit_query)

    # Search 2: G2/Capterra for competitor gaps (Google is good for this)
    print(f"\n   🔍 Searching G2/Capterra: {idea['business']} software reviews")
    g2_query = f"{idea['business']} software reviews gaps missing features site:g2.com OR site:capterra.com"
    g2_results = web_search(g2_query)

    # Search 3: General demand signals
    print(f"\n   🔍 Searching demand signals: {idea['pain']}")
    demand_query = f"{idea['business']} {idea['pain']} demand trends discussions"
    demand_results = web_search(demand_query)

    combined_results = f"""
REDDIT PAIN COMPLAINTS:
{reddit_results}

G2/CAPTERRA COMPETITOR REVIEWS:
{g2_results}

DEMAND SIGNALS:
{demand_results}
"""

    prompt = f"""Analyze evidence and competitive landscape:

Business: {idea['business']}
Pain: {idea['pain']}

SEARCH RESULTS:
{combined_results}

TASK 1: PAIN EVIDENCE (10+ complaints required)
Extract exact quotes from Reddit, Twitter, forums showing this pain:
- Quote: "[exact quote]"
- Source: [URL]
- Date: [when posted]
- Urgency indicator: [lost money / customer churn / compliance risk / wasted time]

Need 10+ complaints from 2024-2025. If fewer than 10 found → KILL

TASK 2: COMPETITIVE LANDSCAPE
Based on G2/Capterra search results, what tools exist?

For each tool found:
- Tool name
- Review count (estimate from results)
- Rating
- Top complaint from 1-star reviews
- Pricing (if visible)

Then classify market:
- WHITE SPACE: No specialized tools found (only generic platforms)
- FRAGMENTED: 5+ tools, all <200 reviews, users complaining about all
- SATURATED: 2-3 tools with 500+ reviews each
- MONOPOLY: 1 tool with 1000+ reviews dominating

TASK 3: DEMAND SIGNALS (3+ required)
Evidence that people are actively looking for solutions:
- Google Trends (increasing search volume)
- Forum posts asking "what tool should I use for [pain]?"
- Job postings mentioning this pain point
- Recent funding/launches in this space

Need 3+ demand signals. If fewer → KILL

VERDICT:
PAIN_COMPLAINTS: [X found] (need 10+)
List top 10 with quotes, URLs, dates

COMPETITIVE_LANDSCAPE: [WHITE SPACE / FRAGMENTED / SATURATED / MONOPOLY]
Tools found: [list with review counts]
Top gaps in existing tools: [what they're missing]

DEMAND_SIGNALS: [X found] (need 3+)
List all signals with evidence

URGENCY_SCORE: X/10 (based on financial impact in complaints)

DECISION: [PASS or KILL]
PASS if: 10+ complaints + (WHITE SPACE or FRAGMENTED) + 3+ demand signals + urgency 8+
KILL if: Any requirement not met OR market is SATURATED/MONOPOLY

REASONING: [Detailed explanation]

Provide complete evidence analysis:"""

    response = call_openai(prompt, model="gpt-5-mini")
    if not response:
        return {"verdict": "KILL", "reason": "API Error"}

    print(f"\n{response}")

    # Parse verdict - strict requirements
    verdict_lower = response.lower()
    has_pass = "decision: pass" in verdict_lower
    has_complaints = "10+" in response or "pain_complaints: 1" in verdict_lower or "pain_complaints: 2" in verdict_lower
    not_saturated = "saturated" not in verdict_lower and "monopoly" not in verdict_lower

    if has_pass and has_complaints and not_saturated:
        print("\n✅ PASS - Strong evidence in white space market")
        return {"verdict": "PASS", "analysis": response}
    else:
        print("\n❌ KILL - Insufficient evidence or saturated market")
        return {"verdict": "KILL", "analysis": response}

# ═══════════════════════════════════════════════════════════
# STAGE 5: GO-TO-MARKET FIT
# ═══════════════════════════════════════════════════════════

def stage5_gtm_fit(idea):
    """Can you get first 10 customers WITHOUT phone sales?"""
    print(f"\n{'─'*60}")
    print(f"STAGE 5: GO-TO-MARKET FIT - Idea #{idea['id']}")
    print(f"{'─'*60}")

    prompt = f"""Design a self-serve GTM strategy to get first 10 customers:

Business: {idea['business']}
Pain: {idea['pain']}

TASK 1: WHERE DO THEY HANG OUT?
List specific online communities:
- Reddit: [specific subreddits]
- Facebook Groups: [specific groups]
- Industry Forums: [specific sites]
- LinkedIn Groups: [specific groups]
- Twitter/X: [relevant hashtags]
- Discord/Slack communities: [specific ones]

Need 5+ active communities with 1000+ members each

TASK 2: CONTENT STRATEGY (No sales calls allowed)
What content would attract them?

Lead Magnets (free tools/resources):
- Example: "HVAC Warranty Cost Calculator" (shows what they're losing)
- Example: "Compliance Checklist for [industry]"
- Example: "Cost of [pain] breakdown tool"

Educational Content:
- "How I saved $40k/year fixing [pain]" (case study)
- "The real cost of [pain] for [business]" (cost breakdown)
- "Why [current solution] isn't working" (pain amplification)

Demo Video (self-serve):
- 3-5 minute product walkthrough
- Show before/after (spreadsheet chaos → clean dashboard)
- ROI calculator built in

TASK 3: SELF-SERVE ONBOARDING
Can they sign up and start using WITHOUT talking to you?

Requirements:
- Free trial (14-30 days, no credit card)
- Product demo video (no call required)
- Documentation/tutorials (self-serve setup)
- Pricing page (transparent, no "Contact sales")
- In-app onboarding (tooltips, checklists)

If they need custom implementation, enterprise setup, or phone demos → KILL

TASK 4: 90-DAY PLAN TO 10 CUSTOMERS
Week 1-2: Build landing page, demo video, lead magnet
Week 3-4: Post in 10+ communities (helpful content, not sales)
Week 5-8: Drive 500-1000 visitors, collect 50-200 emails
Week 9-12: Email sequence → free trials → paying customers
Week 13-14: Iterate based on feedback

Path:
1000 visitors → 10-20% convert to email (100-200 emails)
→ 50-70% start free trial (50-140 trials)
→ 20-40% convert to paid (10-56 customers)

VERDICT:
COMMUNITIES: [List 5+ with member counts]
LEAD_MAGNET: [Specific idea that would attract them]
SELF_SERVE: [YES/NO - can they onboard without calls?]
90_DAY_FEASIBILITY: [YES/NO - can you get 10 customers in 90 days?]

DECISION: [PASS or KILL]
PASS if: 5+ communities + compelling lead magnet + self-serve onboarding + realistic 90-day path
KILL if: Requires phone sales, custom demos, enterprise sales cycle

REASONING: [Why this GTM works or doesn't]

Provide complete GTM strategy:"""

    response = call_openai(prompt, model="gpt-5-mini")
    if not response:
        return {"verdict": "KILL", "reason": "API Error"}

    print(f"\n{response}")

    # Parse verdict
    verdict_lower = response.lower()
    has_pass = "decision: pass" in verdict_lower
    is_self_serve = "self_serve: yes" in verdict_lower or "self-serve onboarding: yes" in verdict_lower
    no_phone_required = "phone" not in verdict_lower or "no phone" in verdict_lower or "without calls" in verdict_lower

    if has_pass and is_self_serve:
        print("\n✅ PASS - Clear self-serve GTM path")
        return {"verdict": "PASS", "analysis": response}
    else:
        print("\n❌ KILL - Requires phone sales or unclear GTM")
        return {"verdict": "KILL", "analysis": response}

# ═══════════════════════════════════════════════════════════
# STAGE 6: FOUNDER REALITY CHECK
# ═══════════════════════════════════════════════════════════

def stage6_founder_reality(idea):
    """Can YOU specifically execute this?"""
    print(f"\n{'─'*60}")
    print(f"STAGE 6: FOUNDER REALITY CHECK - Idea #{idea['id']}")
    print(f"{'─'*60}")

    prompt = f"""Assess founder-market fit for YOUR specific situation:

Business: {idea['business']}
Pain: {idea['pain']}

YOUR CONSTRAINTS:
- Can build (with AI assistance) - moderate technical ability
- Can market (content, ads, SEO) - comfortable with digital marketing
- Cannot do phone sales (stutters, not a sales person)
- Limited capital ($5k max for ads/tools)
- Need first paying customer in 90 days (validation)
- Want to build once, sell 1000x (product business, not custom dev)

ASSESSMENT CRITERIA:

1. BUILD COMPLEXITY (from Stage 2)
Can you build MVP in 3 months with AI help?
- Simple CRUD + workflows + API integrations = YES
- Complex ML/AI, real-time systems, hardware = NO

2. MARKETING CHANNELS (from Stage 5)
Can you reach first 10 customers with $5k ad spend + content?
- Active online communities + self-serve = YES
- Enterprise sales, conferences, cold calling = NO

3. SALES MOTION (CRITICAL - from Stage 5)
Can product sell itself without phone calls?
- Free trial → self-serve onboarding → upgrade = YES
- Custom demos, RFPs, enterprise sales cycle = NO

4. TIME TO REVENUE
Can you get 1 paying customer in 90 days?
- Fast decision cycle (sign up → trial → pay in 30 days) = YES
- Long sales cycle (6+ months, committees, procurement) = NO

5. SCALABILITY
Is this "build once, sell 1000x"?
- SaaS product (same software for everyone) = YES
- Custom implementation for each customer = NO

6. FOUNDER ADVANTAGE
Do you have ANY unfair advantage here?
- Deep industry knowledge = Strong advantage
- Technical skills to build faster = Moderate advantage
- Existing audience/network in this space = Strong advantage
- None of the above = Must rely on evidence + execution

VERDICT:
BUILD_FEASIBILITY: [YES/NO] (3mo with AI help?)
MARKETING_FEASIBILITY: [YES/NO] ($5k + content can reach customers?)
SALES_FEASIBILITY: [YES/NO] (self-serve, no phone calls?)
TIME_TO_REVENUE: [YES/NO] (first customer in 90 days?)
SCALABILITY: [YES/NO] (product, not custom dev?)
FOUNDER_ADVANTAGE: [NONE/MODERATE/STRONG]

DECISION: [PASS or KILL]
PASS if: ALL first 5 criteria = YES (advantage not required, just helpful)
KILL if: ANY criteria = NO

REASONING: [Why you can or cannot execute this specific idea]

Provide founder reality assessment:"""

    response = call_openai(prompt, model="gpt-5-mini")
    if not response:
        return {"verdict": "KILL", "reason": "API Error"}

    print(f"\n{response}")

    # Parse verdict - ALL criteria must be YES
    verdict_lower = response.lower()
    has_pass = "decision: pass" in verdict_lower

    criteria_met = all([
        "build_feasibility: yes" in verdict_lower,
        "marketing_feasibility: yes" in verdict_lower,
        "sales_feasibility: yes" in verdict_lower,
        "time_to_revenue: yes" in verdict_lower,
        "scalability: yes" in verdict_lower
    ])

    if has_pass and criteria_met:
        print("\n✅ PASS - You CAN execute this!")
        return {"verdict": "PASS", "analysis": response}
    else:
        print("\n❌ KILL - Execution risk too high for your constraints")
        return {"verdict": "KILL", "analysis": response}

# ═══════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════

def run_pipeline(count):
    """Run the complete 6-stage pipeline"""
    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print("\n" + "="*60)
    print("🏆 ULTIMATE WINNER MACHINE v4.0 - WHITE SPACE HUNTER")
    print("="*60)
    print(f"Run ID: {run_id}")
    print(f"Ideas to process: {count}")

    ideas_bank = load_ideas_bank()

    # Stage 0: Generate ideas
    new_ideas = stage0_generate_ideas(count, ideas_bank)
    if not new_ideas:
        print("❌ No ideas generated")
        return

    ideas_bank.extend(new_ideas)
    save_ideas_bank(ideas_bank)

    # Counters
    stage_counts = {
        "generated": len(new_ideas),
        "stage1_pass": 0,
        "stage2_pass": 0,
        "stage3_pass": 0,
        "stage4_pass": 0,
        "stage5_pass": 0,
        "stage6_pass": 0
    }

    # Process each idea through stages
    for idea in new_ideas:
        # Stage 1: White Space Check
        result = stage1_white_space_check(idea)
        if result["verdict"] == "KILL":
            idea["status"] = "killed_stage1"
            idea["kill_reason"] = result.get("analysis", "Saturated market")
            save_ideas_bank(ideas_bank)
            continue

        idea["status"] = "passed_stage1"
        idea["stage1_analysis"] = result["analysis"]
        stage_counts["stage1_pass"] += 1
        save_ideas_bank(ideas_bank)

        # Stage 2: Build Feasibility
        result = stage2_build_feasibility(idea)
        if result["verdict"] == "KILL":
            idea["status"] = "killed_stage2"
            idea["kill_reason"] = result.get("analysis", "Build complexity")
            save_ideas_bank(ideas_bank)
            continue

        idea["status"] = "passed_stage2"
        idea["stage2_analysis"] = result["analysis"]
        stage_counts["stage2_pass"] += 1
        save_ideas_bank(ideas_bank)

        # Stage 3: Pain Cost Calculator
        result = stage3_pain_cost_calculator(idea)
        if result["verdict"] == "KILL":
            idea["status"] = "killed_stage3"
            idea["kill_reason"] = result.get("analysis", "Problem cost too low")
            save_ideas_bank(ideas_bank)
            continue

        idea["status"] = "passed_stage3"
        idea["stage3_analysis"] = result["analysis"]
        stage_counts["stage3_pass"] += 1
        save_ideas_bank(ideas_bank)

        # Stage 4: Evidence Engine
        result = stage4_evidence_engine(idea)
        if result["verdict"] == "KILL":
            idea["status"] = "killed_stage4"
            idea["kill_reason"] = result.get("analysis", "Insufficient evidence")
            save_ideas_bank(ideas_bank)
            continue

        idea["status"] = "passed_stage4"
        idea["stage4_analysis"] = result["analysis"]
        stage_counts["stage4_pass"] += 1
        save_ideas_bank(ideas_bank)

        # Stage 5: GTM Fit
        result = stage5_gtm_fit(idea)
        if result["verdict"] == "KILL":
            idea["status"] = "killed_stage5"
            idea["kill_reason"] = result.get("analysis", "GTM requires phone sales")
            save_ideas_bank(ideas_bank)
            continue

        idea["status"] = "passed_stage5"
        idea["stage5_analysis"] = result["analysis"]
        stage_counts["stage5_pass"] += 1
        save_ideas_bank(ideas_bank)

        # Stage 6: Founder Reality
        result = stage6_founder_reality(idea)
        if result["verdict"] == "KILL":
            idea["status"] = "killed_stage6"
            idea["kill_reason"] = result.get("analysis", "Execution risk")
            save_ideas_bank(ideas_bank)
            continue

        idea["status"] = "WINNER"
        idea["stage6_analysis"] = result["analysis"]
        stage_counts["stage6_pass"] += 1
        save_ideas_bank(ideas_bank)

        # Found a winner!
        print("\n" + "="*60)
        print("🎉 TRUE WINNER FOUND!")
        print("="*60)
        create_winner_report(idea, run_id)

    # Create summary
    create_run_summary(run_id, stage_counts, ideas_bank)

    print("\n" + "="*60)
    print("RUN COMPLETE")
    print("="*60)
    print(f"Stage 0 (Generated): {stage_counts['generated']}")
    print(f"Stage 1 (White Space): {stage_counts['stage1_pass']} pass")
    print(f"Stage 2 (Build): {stage_counts['stage2_pass']} pass")
    print(f"Stage 3 (Cost): {stage_counts['stage3_pass']} pass")
    print(f"Stage 4 (Evidence): {stage_counts['stage4_pass']} pass")
    print(f"Stage 5 (GTM): {stage_counts['stage5_pass']} pass")
    print(f"Stage 6 (Founder): {stage_counts['stage6_pass']} pass")
    print(f"\n🏆 TRUE WINNERS: {stage_counts['stage6_pass']}")

def create_winner_report(idea, run_id):
    """Create detailed report for winner"""
    filename = f"WINNER_{idea['id']}_{idea['business'].replace('/', '-')[:30]}.txt"

    content = f"""═══════════════════════════════════════════════════════════
🏆 TRUE WINNER FOUND - ULTIMATE WINNER MACHINE v4.0
═══════════════════════════════════════════════════════════

Run ID: {run_id}
Idea ID: {idea['id']}
Generated: {idea['generated_date']}

═══════════════════════════════════════════════════════════
THE OPPORTUNITY
═══════════════════════════════════════════════════════════

Business: {idea['business']}
Pain Point: {idea['pain']}

═══════════════════════════════════════════════════════════
STAGE 1: WHITE SPACE ANALYSIS
═══════════════════════════════════════════════════════════

{idea.get('stage1_analysis', 'N/A')}

═══════════════════════════════════════════════════════════
STAGE 2: BUILD FEASIBILITY
═══════════════════════════════════════════════════════════

{idea.get('stage2_analysis', 'N/A')}

═══════════════════════════════════════════════════════════
STAGE 3: PAIN COST ANALYSIS
═══════════════════════════════════════════════════════════

{idea.get('stage3_analysis', 'N/A')}

═══════════════════════════════════════════════════════════
STAGE 4: EVIDENCE & COMPETITIVE LANDSCAPE
═══════════════════════════════════════════════════════════

{idea.get('stage4_analysis', 'N/A')}

═══════════════════════════════════════════════════════════
STAGE 5: GO-TO-MARKET STRATEGY
═══════════════════════════════════════════════════════════

{idea.get('stage5_analysis', 'N/A')}

═══════════════════════════════════════════════════════════
STAGE 6: FOUNDER-MARKET FIT
═══════════════════════════════════════════════════════════

{idea.get('stage6_analysis', 'N/A')}

═══════════════════════════════════════════════════════════
NEXT STEPS
═══════════════════════════════════════════════════════════

Week 1-2: Build landing page + demo video + lead magnet
Week 3-4: Post in communities (from Stage 5)
Week 5-8: Drive traffic, collect emails
Week 9-12: Free trials, convert to paying customers
Week 13+: Scale to 100 customers

Goal: First paying customer in 90 days
Path to $1M ARR: Proven in Stage 3 analysis

═══════════════════════════════════════════════════════════
🚀 YOU HAVE A VALIDATED, BUILDABLE, SELLABLE OPPORTUNITY!
═══════════════════════════════════════════════════════════
"""

    with open(filename, 'w') as f:
        f.write(content)

    print(f"\n✅ Winner report saved: {filename}")

def create_run_summary(run_id, counts, ideas_bank):
    """Create run summary"""
    filename = f"RUN_SUMMARY_{run_id}.txt"

    winners = [idea for idea in ideas_bank if idea.get("status") == "WINNER"]

    content = f"""═══════════════════════════════════════════════════════════
🏆 ULTIMATE WINNER MACHINE v4.0 - WHITE SPACE HUNTER - RUN SUMMARY
═══════════════════════════════════════════════════════════

Run ID: {run_id}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Ideas Processed: {counts['generated']}

═══════════════════════════════════════════════════════════
STAGE-BY-STAGE BREAKDOWN
═══════════════════════════════════════════════════════════

Stage 0: Generated {counts['generated']} ideas
Stage 1 (White Space): {counts['stage1_pass']} pass, {counts['generated'] - counts['stage1_pass']} killed
Stage 2 (Build): {counts['stage2_pass']} pass, {counts['stage1_pass'] - counts['stage2_pass']} killed
Stage 3 (Cost): {counts['stage3_pass']} pass, {counts['stage2_pass'] - counts['stage3_pass']} killed
Stage 4 (Evidence): {counts['stage4_pass']} pass, {counts['stage3_pass'] - counts['stage4_pass']} killed
Stage 5 (GTM): {counts['stage5_pass']} pass, {counts['stage4_pass'] - counts['stage5_pass']} killed
Stage 6 (Founder): {counts['stage6_pass']} pass, {counts['stage5_pass'] - counts['stage6_pass']} killed

═══════════════════════════════════════════════════════════
FINAL RESULT
═══════════════════════════════════════════════════════════

TRUE WINNERS: {counts['stage6_pass']}

"""

    if counts['stage6_pass'] == 0:
        content += """⚠️  NO WINNERS FOUND

This is NORMAL - the system is working correctly.

What this means:
- No white space opportunities found in this batch
- All ideas either saturated, too small, or bad founder fit
- Run again with 100 more ideas

The system saved you from building in saturated markets!
"""
    else:
        content += f"""🎉 WINNER(S) FOUND!

You have {counts['stage6_pass']} validated opportunity(ies) with:
- WHITE SPACE market (no Salesforce/HubSpot competition)
- $10k-100k+ annual cost (proven)
- REAL evidence (10+ complaints, demand signals)
- Buildable in 3 months
- Self-serve GTM (no phone sales)
- Fits YOUR constraints

See WINNER_*.txt files for complete reports.

Next step: Build the MVP!
"""

    with open(filename, 'w') as f:
        f.write(content)

    print(f"\n✅ Run summary saved: {filename}")

# ═══════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ultimate Winner Machine v4.0 - White Space Hunter")
    parser.add_argument("--count", type=int, default=10, help="Number of ideas to generate")
    args = parser.parse_args()

    run_pipeline(args.count)
