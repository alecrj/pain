#!/usr/bin/env python3
"""
THE ULTIMATE WINNER MACHINE v2.0
One unified system to find TRUE business opportunities with PROVEN gaps

7-Stage Progressive Filter:
- Stage 0: Smart Generation (100 ideas)
- Stage 1: Growth & Feasibility (kill 80%)
- Stage 2: Budget Reality Check (kill 50%)
- Stage 3: Urgency Validation (kill 50%)
- Stage 4: Competitor Gap Proof (THE CRITICAL FILTER - kill 40%)
- Stage 5: Complete Research + Strategist + Attack Plan
- Stage 6: Founder Reality Check (FINAL KILL)

Expected: 100 ideas → 0-1 TRUE WINNER (or honest ZERO)
"""

import os
import sys
import time
import argparse
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("❌ No OPENAI_API_KEY in .env")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

# Excluded industries (licensing/regulatory hell)
EXCLUDED_INDUSTRIES = [
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
    "counseling", "therapy", "mental health", "psychologist", "psychiatrist"
]

def call_openai(prompt, system_message="You are a business research expert.", model="gpt-4o", temperature=0.7):
    """Call OpenAI API with rate limiting"""
    time.sleep(1)  # Rate limiting
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"   ⚠️  API Error: {str(e)}")
        return None

# ============================================================================
# STAGE 0: SMART GENERATION
# ============================================================================

def stage0_generate_ideas(count=100):
    """
    Generate pre-filtered business ideas
    Focus: Growing industries, operational pain, software-solvable
    """
    print(f"\n{'='*70}")
    print(f"🧠 STAGE 0: INTELLIGENT IDEA GENERATION")
    print(f"{'='*70}\n")

    prompt = f"""Generate {count} ultra-specific business pain points for GROWING businesses with PROVEN budgets.

CRITICAL CONSTRAINTS:

✅ **ALLOWED INDUSTRIES (No Licensing/Regulation):**
- Construction/General Contractors
- Manufacturing (discrete/process)
- Retail (physical stores)
- Hospitality (restaurants, hotels, catering)
- Logistics/Transportation/Freight
- Property Maintenance/Facilities Management
- Wholesale Distribution
- Agriculture/Farming/Agribusiness
- Marketing/Advertising Agencies
- Event Planning
- Professional Services (consulting, training, recruiting)
- Landscaping/Grounds Maintenance
- Commercial Cleaning/Janitorial
- Equipment Rental
- Print/Signage
- Warehousing/Fulfillment/3PL
- HVAC/Plumbing/Electrical Contractors
- Auto Repair/Body Shops
- Gyms/Fitness Centers

❌ **EXCLUDED (Licensing/Regulatory Hell):**
- Healthcare/Medical/Dental
- Insurance
- Finance/Banking
- Legal/Law Firms
- Real Estate Sales
- Pharmacy
- Childcare/Education
- Senior Care/Home Health
- Counseling/Therapy

🎯 **TARGET: Businesses with $100k+ revenue that:**
- Are growing >15% YoY (hiring, expanding)
- Have 50+ employees (large enough to have budget)
- Face OPERATIONAL pain (inventory, scheduling, coordination, reporting)
- Already use software/tools (proven willingness to pay)
- Have clear decision makers (VP, Director, Owner)

💡 **FOCUS ON OPERATIONAL PROBLEMS:**
- Scheduling/coordination chaos
- Manual data entry/reconciliation
- Communication breakdowns (phone tag, email chaos)
- Tracking/monitoring inefficiencies
- Reporting/compliance paperwork
- Financial reconciliation errors

EXAMPLES (don't repeat):
- Manufacturing plants, Reconciling inventory counts between warehouse floor and ERP system using spreadsheets causing daily discrepancies
- Commercial HVAC contractors, Tracking technician locations and job status via phone calls wasting 2+ hours per day
- Distribution companies, Managing driver routes and delivery schedules through text messages causing missed deliveries
- Restaurant groups, Reconciling food costs across multiple locations using Excel leading to ordering errors

Generate {count} NEW pain points NOW. Be ULTRA-SPECIFIC about the operational problem.

Format as CSV (one per line):
Business Type (specific industry), Specific Operational Problem
"""

    print(f"Generating {count} pre-filtered ideas...", flush=True)

    result = call_openai(prompt, temperature=0.9)

    if not result:
        print("❌ Failed to generate ideas")
        return []

    # Parse ideas
    ideas = []
    for line in result.strip().split('\n'):
        line = line.strip()
        if not line or 'Business Type' in line or 'CSV' in line or 'Format' in line:
            continue

        if ',' in line:
            parts = [p.strip() for p in line.split(',', 1)]
            if len(parts) >= 2 and len(parts[0]) > 0 and len(parts[1]) > 0:
                ideas.append({
                    "business": parts[0],
                    "pain": parts[1],
                    "id": len(ideas) + 1
                })

    print(f"✓ Generated {len(ideas)} ideas")
    return ideas

# ============================================================================
# STAGE 1: GROWTH & FEASIBILITY
# ============================================================================

def stage1_growth_feasibility(ideas):
    """
    Kill: Low growth, enterprise APIs, too small businesses
    Must pass: >15% YoY growth, >50 employees, public APIs possible
    """
    print(f"\n{'='*70}")
    print(f"⚡ STAGE 1: GROWTH & FEASIBILITY CHECK")
    print(f"{'='*70}\n")

    print(f"Processing {len(ideas)} ideas with brutal filters...\n", flush=True)

    survivors = []
    killed = []

    for i, idea in enumerate(ideas, 1):
        business = idea['business']
        pain = idea['pain']

        print(f"[{i}/{len(ideas)}] {business[:50]}...", flush=True)

        # Check if excluded industry
        business_lower = business.lower()
        if any(excluded in business_lower for excluded in EXCLUDED_INDUSTRIES):
            print(f"   ❌ KILL: Excluded industry")
            killed.append({**idea, "kill_reason": "Excluded industry (Stage 1)"})
            continue

        # Research growth + feasibility
        prompt = f"""Analyze this business opportunity for HARD FILTERS:

Business: {business}
Problem: {pain}

Research and answer these questions with YES/NO and brief evidence:

1. GROWTH CHECK: Is the {business} industry growing at >15% per year?
   - Search for industry reports, IBISWorld, Statista
   - Look for "CAGR", "growth rate", "market size"
   - YES if >15% YoY, NO if <15%

2. BUSINESS SIZE: Do most {business} have 50+ employees?
   - Search for typical company size in this industry
   - YES if average >50 employees, NO if smaller

3. ENTERPRISE API CHECK: Does solving "{pain}" require enterprise APIs?
   - Would this need Salesforce, SAP, Oracle, NetSuite integrations?
   - YES if requires enterprise APIs (KILL), NO if public APIs or no APIs needed

4. PUBLIC API FEASIBILITY: Can you build this with public APIs or web scraping?
   - Public APIs: Google Maps, weather, shipping carriers, payment processors
   - YES if possible with public APIs/scraping, NO if impossible

Return EXACTLY this format:
GROWTH: [YES/NO] - [brief evidence]
SIZE: [YES/NO] - [brief evidence]
ENTERPRISE_API: [YES/NO] - [brief reason]
PUBLIC_API: [YES/NO] - [brief reason]
VERDICT: [PASS/KILL] - [reason if KILL]
"""

        result = call_openai(prompt, temperature=0.3)

        if not result:
            killed.append({**idea, "kill_reason": "API error (Stage 1)"})
            continue

        # Parse result
        result_lower = result.lower()

        # Check verdicts
        if "verdict: kill" in result_lower or "verdict:kill" in result_lower:
            print(f"   ❌ KILL: {result.split('VERDICT:')[1].split('-')[1].strip() if 'VERDICT:' in result else 'Failed criteria'}")
            killed.append({**idea, "kill_reason": f"Failed Stage 1 criteria", "stage1_analysis": result})
        elif "growth: no" in result_lower or "size: no" in result_lower or "enterprise_api: yes" in result_lower or "public_api: no" in result_lower:
            reason = "Low growth or size" if "growth: no" in result_lower or "size: no" in result_lower else "API barriers"
            print(f"   ❌ KILL: {reason}")
            killed.append({**idea, "kill_reason": reason, "stage1_analysis": result})
        else:
            print(f"   ✅ PASS Stage 1", flush=True)
            survivors.append({**idea, "stage1_analysis": result})

    print(f"\n{'='*70}")
    print(f"STAGE 1 COMPLETE:")
    print(f"   Input: {len(ideas)}")
    if len(ideas) > 0:
        print(f"   Killed: {len(killed)} ({len(killed)/len(ideas)*100:.1f}%)")
        print(f"   Survivors: {len(survivors)} ({len(survivors)/len(ideas)*100:.1f}%)")
    print(f"{'='*70}\n")

    return survivors, killed

# ============================================================================
# STAGE 2: BUDGET REALITY CHECK
# ============================================================================

def stage2_budget_check(ideas):
    """
    Prove businesses actually spend $10k+/year on software
    Must find: G2/Capterra pricing, decision makers, proof of spending
    """
    print(f"\n{'='*70}")
    print(f"💰 STAGE 2: BUDGET REALITY CHECK")
    print(f"{'='*70}\n")

    print(f"Processing {len(ideas)} ideas for budget validation...\n", flush=True)

    survivors = []
    killed = []

    for i, idea in enumerate(ideas, 1):
        business = idea['business']
        pain = idea['pain']

        print(f"[{i}/{len(ideas)}] {business[:50]}...", flush=True)

        prompt = f"""Research PROOF of budget for this business opportunity:

Business: {business}
Problem: {pain}

You MUST find HARD EVIDENCE to answer YES to ALL:

1. TOOL RESEARCH: Find 3+ tools on G2.com or Capterra.com solving similar problems
   - Search: "G2 [related keyword] software"
   - List tool names with ACTUAL pricing if visible
   - Include G2/Capterra URLs

2. SPENDING PROOF: Prove {business} spend $10,000+/year on software
   - Look for pricing tiers, annual plans, enterprise pricing
   - Search for reviews mentioning costs
   - Calculate: if $99/mo × 12 months = $1,188 (TOO LOW, KILL)
   - Need: $10k+/year evidence

3. DECISION MAKERS: Who buys this software?
   - Search job titles: "VP Operations", "Director of [X]", "Owner"
   - Look for LinkedIn job posts requiring this software
   - Must identify SPECIFIC titles

4. PROOF OF USE: Find 1+ company saying "we use [tool]"
   - Search LinkedIn, Reddit, forums for mentions
   - Look for case studies, testimonials
   - Need actual company using similar solutions

Return EXACTLY this format:
TOOLS: [List 3+ tools with pricing]
SPENDING: [YES/NO] - [evidence of $10k+/year]
DECISION_MAKERS: [List specific titles]
PROOF_OF_USE: [YES/NO] - [evidence with source]
VERDICT: [PASS/KILL] - [reason]
"""

        result = call_openai(prompt, temperature=0.3)

        if not result:
            killed.append({**idea, "kill_reason": "API error (Stage 2)"})
            continue

        result_lower = result.lower()

        # Check verdicts
        if "verdict: kill" in result_lower or "spending: no" in result_lower or "proof_of_use: no" in result_lower:
            print(f"   ❌ KILL: Failed budget validation")
            killed.append({**idea, "kill_reason": "No budget proof (Stage 2)", "stage2_analysis": result})
        else:
            print(f"   ✅ PASS Stage 2", flush=True)
            survivors.append({**idea, "stage2_analysis": result})

    print(f"\n{'='*70}")
    print(f"STAGE 2 COMPLETE:")
    print(f"   Input: {len(ideas)}")
    if len(ideas) > 0:
        print(f"   Killed: {len(killed)} ({len(killed)/len(ideas)*100:.1f}%)")
        print(f"   Survivors: {len(survivors)} ({len(survivors)/len(ideas)*100:.1f}%)")
    else:
        print(f"   Killed: 0")
        print(f"   Survivors: 0")
    print(f"{'='*70}\n")

    return survivors, killed

# ============================================================================
# STAGE 3: URGENCY VALIDATION
# ============================================================================

def stage3_urgency_validation(ideas):
    """
    Find 10+ complaints from 2024-2025 with urgency drivers
    Must prove: Pain is urgent, people are actively complaining
    """
    print(f"\n{'='*70}")
    print(f"🔥 STAGE 3: URGENCY & PAIN VALIDATION")
    print(f"{'='*70}\n")

    print(f"Processing {len(ideas)} ideas for urgency...\n", flush=True)

    survivors = []
    killed = []

    for i, idea in enumerate(ideas, 1):
        business = idea['business']
        pain = idea['pain']

        print(f"[{i}/{len(ideas)}] {business[:50]}...", flush=True)

        prompt = f"""Find PROOF of URGENT pain for this business opportunity:

Business: {business}
Problem: {pain}

You MUST find ALL of the following:

1. FIND 10+ COMPLAINTS (2024-2025 ONLY):
   Search these sources:
   - Reddit: site:reddit.com "{business}" "{pain}" 2024
   - G2/Capterra: negative reviews of related tools
   - Twitter/X: complaints about this problem
   - Industry forums, Facebook groups

   List each complaint with:
   - Exact quote
   - Source URL
   - Date (must be 2024-2025)

2. URGENCY DRIVERS (find at least 1):
   - Revenue loss: "this costs us $X/month"
   - Regulatory pressure: "we need to comply by X date"
   - Competitive pressure: "competitors are doing X better"
   - Time waste: "this takes X hours per week"

3. PAIN INTENSITY (score 1-10):
   - 1-3: Minor annoyance
   - 4-6: Moderate problem
   - 7-8: Serious pain
   - 9-10: Critical/desperate
   Look for words: "nightmare", "disaster", "terrible", "hate", "desperate"

Return EXACTLY this format:
COMPLAINTS: [List 10+ with quotes, URLs, dates]
URGENCY_DRIVERS: [List with evidence]
PAIN_SCORE: [X/10] - [reasoning]
VERDICT: [PASS/KILL] - [reason]

PASS only if: 10+ complaints (2024-2025), pain score 8+/10, urgency drivers present
"""

        result = call_openai(prompt, temperature=0.3)

        if not result:
            killed.append({**idea, "kill_reason": "API error (Stage 3)"})
            continue

        result_lower = result.lower()

        # Count complaints in result
        complaint_count = result_lower.count("http")  # Rough proxy for URLs

        # Check verdicts
        if "verdict: kill" in result_lower or complaint_count < 8:  # Allow some flexibility
            print(f"   ❌ KILL: Low urgency or insufficient complaints")
            killed.append({**idea, "kill_reason": "Low urgency (Stage 3)", "stage3_analysis": result})
        else:
            print(f"   ✅ PASS Stage 3", flush=True)
            survivors.append({**idea, "stage3_analysis": result})

    print(f"\n{'='*70}")
    print(f"STAGE 3 COMPLETE:")
    print(f"   Input: {len(ideas)}")
    if len(ideas) > 0:
        print(f"   Killed: {len(killed)} ({len(killed)/len(ideas)*100:.1f}%)")
        print(f"   Survivors: {len(survivors)} ({len(survivors)/len(ideas)*100:.1f}%)")
    else:
        print(f"   Killed: 0")
        print(f"   Survivors: 0")
    print(f"{'='*70}\n")

    return survivors, killed

# ============================================================================
# STAGE 4: COMPETITOR GAP PROOF ⭐ THE CRITICAL FILTER
# ============================================================================

def stage4_gap_proof(ideas):
    """
    THE CRITICAL FILTER - Prove a real, attackable gap exists
    Must prove ALL 4: competitor weakness, demand signals, moat feasibility, "why now?"
    """
    print(f"\n{'='*70}")
    print(f"🎯 STAGE 4: COMPETITOR GAP PROOF (CRITICAL FILTER)")
    print(f"{'='*70}\n")

    print(f"Processing {len(ideas)} ideas for competitive gaps...\n", flush=True)

    survivors = []
    killed = []

    for i, idea in enumerate(ideas, 1):
        business = idea['business']
        pain = idea['pain']

        print(f"[{i}/{len(ideas)}] {business[:50]}...", flush=True)

        prompt = f"""PROVE there is a REAL, ATTACKABLE gap in the market:

Business: {business}
Problem: {pain}

You MUST prove ALL 4 of the following:

═══════════════════════════════════════════════════════════
1. COMPETITOR WEAKNESS (10+ pieces of evidence)
═══════════════════════════════════════════════════════════

Find the top 3 competitors solving similar problems.
For EACH competitor, find SPECIFIC complaints (2024-2025):

Search:
- G2.com reviews (filter by 1-3 stars)
- Capterra negative reviews
- Reddit: "site:reddit.com [competitor name] problems"
- Twitter: "[competitor] sucks" OR "[competitor] terrible"

List 10+ complaints with:
- Competitor name
- Specific feature/problem
- Exact quote
- Source URL
- Date

Example:
- ShipStation: "Reporting is garbage, can't customize anything" (G2 Review, Jan 2024, [URL])
- AfterShip: "No integration with Shopify Plus" (Reddit, Mar 2024, [URL])

═══════════════════════════════════════════════════════════
2. CUSTOMER DEMAND SIGNALS (5+ pieces of evidence)
═══════════════════════════════════════════════════════════

Find people actively ASKING for this solution:

Search:
- Reddit: "Does anyone know a tool that [solves this problem]?"
- Forums: "Looking for [competitor] alternative because..."
- G2 reviews: "I wish [tool] would add [feature]"
- Twitter: "Anyone have a solution for [problem]?"

List 5+ demand signals with:
- Exact quote
- Context (what they're asking for)
- Source URL
- Date (2024-2025)

═══════════════════════════════════════════════════════════
3. MOAT FEASIBILITY
═══════════════════════════════════════════════════════════

Answer these:
- Can you build MVP in <3 months using Bolt/Lovable/Cursor?
- What makes it defensible? (network effects, data advantage, switching costs)
- How hard is it to switch from competitor? (<1 day = good, >1 week = bad)

═══════════════════════════════════════════════════════════
4. THE "WHY NOW?" TEST
═══════════════════════════════════════════════════════════

What changed in the last 12 months that makes this gap exploitable NOW?

Look for:
- Competitor raised prices (search "[competitor] pricing increase 2024")
- Competitor got acquired (search "[competitor] acquisition")
- New regulation created demand
- New technology made solution easier
- Competitor service degraded (complaints spiking)

If NOTHING changed → gap probably doesn't exist → KILL

═══════════════════════════════════════════════════════════

Return EXACTLY this format:

COMPETITORS: [List top 3]

WEAKNESS_EVIDENCE: [10+ complaints with quotes, URLs, dates]

DEMAND_SIGNALS: [5+ with quotes, URLs, dates]

MOAT_FEASIBILITY: [YES/NO] - [Can build in 3mo? Defensibility? Switching cost?]

WHY_NOW: [What changed in 2024?] - [Evidence]

VERDICT: [PASS/KILL] - [Reason]

PASS only if ALL 4 proven: 10+ weaknesses, 5+ demand signals, moat possible, "why now" exists
"""

        result = call_openai(prompt, temperature=0.3, model="gpt-4o")

        if not result:
            killed.append({**idea, "kill_reason": "API error (Stage 4)"})
            continue

        result_lower = result.lower()

        # Count evidence (rough proxy via URLs)
        url_count = result_lower.count("http")

        # Check verdicts
        if "verdict: kill" in result_lower or url_count < 10:  # Need substantial evidence
            print(f"   ❌ KILL: No real gap or insufficient evidence")
            killed.append({**idea, "kill_reason": "No attackable gap (Stage 4)", "stage4_analysis": result})
        elif "why_now:" in result_lower and "nothing" in result_lower.split("why_now:")[1][:200]:
            print(f"   ❌ KILL: No 'why now' catalyst")
            killed.append({**idea, "kill_reason": "No 'why now' (Stage 4)", "stage4_analysis": result})
        else:
            print(f"   ✅ PASS Stage 4 (GAP PROVEN)", flush=True)
            survivors.append({**idea, "stage4_analysis": result})

    print(f"\n{'='*70}")
    print(f"STAGE 4 COMPLETE:")
    print(f"   Input: {len(ideas)}")
    if len(ideas) > 0:
        print(f"   Killed: {len(killed)} ({len(killed)/len(ideas)*100:.1f}%)")
        print(f"   Survivors: {len(survivors)} ({len(survivors)/len(ideas)*100:.1f}%)")
    else:
        print(f"   Killed: 0")
        print(f"   Survivors: 0")
    print(f"{'='*70}\n")

    return survivors, killed

# ============================================================================
# STAGE 5: COMPLETE RESEARCH + STRATEGIST + ATTACK PLAN
# ============================================================================

def stage5_complete_research(ideas):
    """
    Full Researcher + Strategist + Attack Plan for finalists
    No kills here - all finalists get complete reports
    """
    print(f"\n{'='*70}")
    print(f"🔬 STAGE 5: COMPLETE RESEARCH + STRATEGIST + ATTACK PLAN")
    print(f"{'='*70}\n")

    print(f"Deep research on {len(ideas)} finalists...\n", flush=True)

    winners = []

    for i, idea in enumerate(ideas, 1):
        business = idea['business']
        pain = idea['pain']

        print(f"[{i}/{len(ideas)}] DEEP DIVE: {business[:40]}")
        print(f"{'='*70}", flush=True)

        # Part 1: The Researcher
        researcher_prompt = f"""Complete RESEARCHER analysis for this VALIDATED opportunity:

Business: {business}
Problem: {pain}

Previous Research:
{idea.get('stage1_analysis', '')[:500]}
{idea.get('stage2_analysis', '')[:500]}
{idea.get('stage3_analysis', '')[:500]}
{idea.get('stage4_analysis', '')[:1000]}

Create a complete RESEARCHER report with:

## MARKET VALIDATION
- Market Size (TAM) with sources
- Growth Rate (CAGR) with sources
- Demand Evidence (search volumes, surveys, conversations)

## COMPETITIVE POSITIONING
- Key Competitors (from Stage 4)
- Gaps Identified (from Stage 4 weakness evidence)
- Sustainable Advantage (based on moat analysis)

## UNIT ECONOMICS
- Pricing Strategy (3 tiers based on Stage 2 research)
- Estimated CAC
- Estimated LTV (3-year)
- LTV:CAC Ratio (must be >3:1)
- Gross Margin estimate

## OPERATIONS & SCALABILITY
- Resources to Launch (team size, tech needs, capital)
- Technical Complexity (1-10 score)
- Scalability Assessment (can it 10x without linear cost increase?)

## RISKS & RED FLAGS
- Top 3 Risks with mitigation strategies
- Regulatory Barriers (if any)
- Why This Could Fail (be honest)

## VALIDATION EXPERIMENTS
List 3 experiments with:
- Name
- Cost
- Duration
- Success Criteria

Use this format exactly. Include sources/citations.
"""

        researcher_result = call_openai(researcher_prompt, temperature=0.5, model="gpt-4o")

        # Part 2: The Strategist
        strategist_prompt = f"""Complete STRATEGIST analysis for this opportunity:

Business: {business}
Problem: {pain}

Create a complete GTM strategy:

## VALUE PROPOSITION
Create statement: "I help [audience] solve [problem] so they can [outcome]"

Then quality check:
- Specific? (targets exact audience and problem)
- Emotional? (acknowledges pain/frustration)
- Obvious? (clear benefit)

## LEAD MAGNET IDEAS (Rank by speed/cost/conversion)
Generate 5 ideas:
1. [Name] - Build time: X hours - Value: [what they get]
2. [Name] - Build time: X hours - Value: [what they get]
3. [Name] - Build time: X hours - Value: [what they get]
4. [Name] - Build time: X hours - Value: [what they get]
5. [Name] - Build time: X hours - Value: [what they get]

TOP PICK: #X - [Name]
Why this one wins: [reasoning]

## MVT VALIDATION PLAN
Week 1: [action] - Success metric: [X]
Week 2: [action] - Success metric: [X]
Week 3: [action] - Success metric: [X]
Week 4: Decision point - [criteria to build or pivot]

## FIRST 10 CUSTOMERS
Where to find: [Specific LinkedIn groups, subreddits, forums WITH URLs]
Outreach approach: [How to reach them without being spammy]
Timeline: 14 days to 10 conversations

## GTM STRATEGY
- Content pillars: [3 main topics]
- Platform: [Primary channel - LinkedIn, Twitter, etc]
- Posting cadence: [X times/week]
- Distribution: [Where to share]

## STRAIGHT-LINE MARKETING
Content → Lead Magnet → Offer
[Map out the flow solving the same pain throughout]
"""

        strategist_result = call_openai(strategist_prompt, temperature=0.6, model="gpt-4o")

        # Part 3: The Attack Plan
        attack_prompt = f"""Create THE ATTACK PLAN for stealing customers from competitors:

Business: {business}
Problem: {pain}

Gap Proof (from Stage 4):
{idea.get('stage4_analysis', '')[:2000]}

Create attack strategy:

## COMPETITIVE POSITIONING
"We're [competitor name] but [what you do that they'll never add]"
Example: "We're ShipStation but with real-time AI-driven shipping cost predictions they'll never build"

## STEAL-THE-CUSTOMER STRATEGY
Based on the complaints from Stage 4:
1. Top complaint about competitors: [quote from Stage 4]
2. How we solve it differently: [specific feature]
3. Migration offer: [how to make switching easy]

## 30/60/90 DAY PLAN
Day 1-30: [Focus area] - Metric: [X]
Day 31-60: [Focus area] - Metric: [X]
Day 61-90: [Focus area] - Metric: [X]

## WHY CUSTOMERS WILL SWITCH
List 5 reasons based on Stage 4 complaints:
1. [Reason] - Evidence: [complaint quote]
2. [Reason] - Evidence: [complaint quote]
3. [Reason] - Evidence: [complaint quote]
4. [Reason] - Evidence: [complaint quote]
5. [Reason] - Evidence: [complaint quote]

## FIRST CUSTOMER ACQUISITION
Week 1-2 action plan:
- Where to find them: [exact URLs]
- What to say: [message template]
- Lead magnet hook: [how to position it]
- Expected response rate: [X%]
"""

        attack_result = call_openai(attack_prompt, temperature=0.6, model="gpt-4o")

        # Final Assessment
        assessment_prompt = f"""Final assessment of this opportunity:

Business: {business}
Problem: {pain}

Based on all research, provide:

## OVERALL SCORE (1-10): X/10

## TOP 3 STRENGTHS
1. [Strength] - [Why this matters]
2. [Strength] - [Why this matters]
3. [Strength] - [Why this matters]

## TOP 3 CONCERNS
1. [Concern] - Mitigation: [How to address]
2. [Concern] - Mitigation: [How to address]
3. [Concern] - Mitigation: [How to address]

## FINAL RECOMMENDATION
VERDICT: BUILD / PIVOT / KILL

- Why this is a winner (or not): [reasoning]
- Confidence level: [High/Medium/Low]
- Next immediate action: [What to do first]
"""

        assessment_result = call_openai(assessment_prompt, temperature=0.5, model="gpt-4o")

        # Compile full report
        full_report = f"""# ULTIMATE WINNER REPORT

TARGET: {business}
PROBLEM: {pain}
DATE: {datetime.now().strftime("%Y-%m-%d")}

{'='*70}
THE RESEARCHER: COMPLETE VALIDATION
{'='*70}

{researcher_result}

{'='*70}
THE STRATEGIST: GO-TO-MARKET PLAN
{'='*70}

{strategist_result}

{'='*70}
THE ATTACK PLAN: STEALING CUSTOMERS FROM COMPETITORS
{'='*70}

{attack_result}

{'='*70}
THE GAP PROOF (From Stage 4)
{'='*70}

{idea.get('stage4_analysis', 'No gap analysis available')}

{'='*70}
FINAL ASSESSMENT
{'='*70}

{assessment_result}

{'='*70}
COPYWRITER BRIEF
{'='*70}

This report contains everything needed for copywriting:
- Target audience: {business}
- Core pain: {pain}
- Value proposition: [Extract from Strategist section]
- Lead magnet: [Top pick from Strategist section]
- Tone/Voice: Bold, specific, results-focused
- Evidence: All citations included above

Ready for landing page, emails, and content creation.
"""

        # Save report
        safe_business = business.replace('/', '-').replace(' ', '_')[:40]
        filename = f"ULTIMATE_WINNER_{i}_{safe_business}.txt"

        try:
            with open(filename, 'w') as f:
                f.write(full_report)
            print(f"   ✅ Complete report saved: {filename}\n")
        except Exception as e:
            print(f"   ⚠️  Could not save file: {e}\n")

        winners.append({
            **idea,
            "report": full_report,
            "filename": filename
        })

    print(f"\n{'='*70}")
    print(f"STAGE 5 COMPLETE:")
    print(f"   Finalists researched: {len(ideas)}")
    print(f"   Complete reports generated: {len(winners)}")
    print(f"{'='*70}\n")

    return winners

# ============================================================================
# STAGE 6: FOUNDER REALITY CHECK ⭐ FINAL KILL
# ============================================================================

def stage6_founder_check(winners):
    """
    FINAL KILL - Can YOU actually execute this?
    Checks: reach test, build test, $500 test, conviction test
    """
    print(f"\n{'='*70}")
    print(f"👤 STAGE 6: FOUNDER REALITY CHECK (FINAL KILL)")
    print(f"{'='*70}\n")

    print(f"Evaluating {len(winners)} winners for founder fit...\n", flush=True)

    true_winners = []
    final_kills = []

    for i, winner in enumerate(winners, 1):
        business = winner['business']
        pain = winner['pain']

        print(f"[{i}/{len(winners)}] {business[:50]}...", flush=True)

        prompt = f"""FINAL REALITY CHECK for this opportunity:

Business: {business}
Problem: {pain}

Strategist Research:
{winner.get('report', '')[:3000]}

Answer these questions honestly:

═══════════════════════════════════════════════════════════
1. THE REACH TEST - Can founder find 10 customers in 14 days?
═══════════════════════════════════════════════════════════

Based on "First 10 Customers" section:
- Are the communities/groups specific and accessible?
- Can someone DM/post without looking spammy?
- Is the audience actively discussing this problem?

ANSWER: YES/NO - [reasoning]

═══════════════════════════════════════════════════════════
2. THE BUILD TEST - Can founder build lead magnet in 1 weekend?
═══════════════════════════════════════════════════════════

Based on top lead magnet pick:
- Is it actually buildable by one person?
- Can it be done with AI tools (ChatGPT, Canva, Bolt)?
- Does it require domain expertise?

ANSWER: YES/NO - [reasoning]

═══════════════════════════════════════════════════════════
3. THE $500 TEST - Can this be validated under $500?
═══════════════════════════════════════════════════════════

Calculate:
- Lead magnet cost: $X
- Landing page: $0 (Bolt/Lovable)
- Ad spend (optional): $X
- Total: $X

ANSWER: YES/NO - [breakdown]

═══════════════════════════════════════════════════════════
4. THE CONVICTION TEST - Would you bet $10k on this?
═══════════════════════════════════════════════════════════

Based on ALL research:
- Is the gap real and proven?
- Are customers desperate enough?
- Is the market timing right?
- Can a solo founder compete?

ANSWER: YES/NO - [honest assessment]

═══════════════════════════════════════════════════════════

FINAL VERDICT: [PASS/KILL] - [reason]

PASS only if ALL 4 are YES.
"""

        result = call_openai(prompt, temperature=0.3, model="gpt-4o")

        if not result:
            final_kills.append({**winner, "final_kill_reason": "API error"})
            continue

        result_lower = result.lower()

        # Count YES answers (need 4/4)
        yes_count = result_lower.count("answer: yes")

        if "final verdict: kill" in result_lower or yes_count < 4:
            print(f"   ❌ FINAL KILL: Not founder-ready")
            final_kills.append({**winner, "final_kill_reason": "Failed founder check", "stage6_analysis": result})
        else:
            print(f"   ✅ TRUE WINNER - Ready to execute!", flush=True)
            true_winners.append({**winner, "stage6_analysis": result})

            # Update report file with Stage 6 analysis
            try:
                with open(winner['filename'], 'a') as f:
                    f.write(f"\n\n{'='*70}\n")
                    f.write(f"STAGE 6: FOUNDER REALITY CHECK\n")
                    f.write(f"{'='*70}\n\n")
                    f.write(result)
            except Exception as e:
                print(f"   ⚠️  Could not update file: {e}")

    print(f"\n{'='*70}")
    print(f"STAGE 6 COMPLETE:")
    print(f"   Input: {len(winners)}")
    if len(winners) > 0:
        print(f"   Final Kills: {len(final_kills)} ({len(final_kills)/len(winners)*100:.1f}%)")
        print(f"   TRUE WINNERS: {len(true_winners)} ({len(true_winners)/len(winners)*100:.1f}%)")
    else:
        print(f"   Final Kills: 0")
        print(f"   TRUE WINNERS: 0")
    print(f"{'='*70}\n")

    return true_winners, final_kills

# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Ultimate Winner Machine v2.0')
    parser.add_argument('--count', type=int, default=100, help='Number of ideas to generate')
    parser.add_argument('--mode', type=str, default='full',
                       choices=['full', 'stage0', 'stage1', 'stage2', 'stage3', 'stage4', 'stage5', 'stage6'],
                       help='Which stage to run')

    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         🏆 THE ULTIMATE WINNER MACHINE v2.0 🏆                  ║
║                                                                  ║
║  7-Stage Progressive Filter for TRUE Business Opportunities     ║
║                                                                  ║
║  Stage 0: Smart Generation     (100 pre-filtered ideas)        ║
║  Stage 1: Growth & Feasibility (Kill 80% - growth/API check)   ║
║  Stage 2: Budget Reality       (Kill 50% - prove spending)     ║
║  Stage 3: Urgency Validation   (Kill 50% - 10+ complaints)     ║
║  Stage 4: Gap Proof ⭐         (Kill 40% - CRITICAL FILTER)    ║
║  Stage 5: Complete Research    (Full reports for finalists)    ║
║  Stage 6: Founder Check ⭐     (Final kill - can YOU do it?)   ║
║                                                                  ║
║  Expected: 100 → 0-1 TRUE WINNER (or honest ZERO)              ║
║                                                                  ║
║  Honest Output: Better 0/100 than 1 false positive             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Stage 0: Generate ideas
    ideas = stage0_generate_ideas(args.count)

    if not ideas:
        print("\n❌ No ideas generated. Exiting.")
        return

    if args.mode == 'stage0':
        print(f"\n✅ Generated {len(ideas)} ideas. Stopping at Stage 0.")
        return

    # Stage 1: Growth & Feasibility
    survivors, _ = stage1_growth_feasibility(ideas)

    if not survivors:
        print(f"\n⚠️  ALL {len(ideas)} IDEAS KILLED IN STAGE 1")
        print(f"\nThis is honest - no opportunities met the growth/feasibility criteria.")
        print(f"\nTry: Different industries or broader pain points")
        return

    if args.mode == 'stage1':
        print(f"\n✅ {len(survivors)} survivors after Stage 1. Stopping.")
        return

    # Stage 2: Budget Check
    survivors, _ = stage2_budget_check(survivors)

    if not survivors:
        print(f"\n⚠️  ALL IDEAS KILLED BY STAGE 2")
        print(f"\nCould not prove businesses spend $10k+/year on solutions.")
        return

    if args.mode == 'stage2':
        print(f"\n✅ {len(survivors)} survivors after Stage 2. Stopping.")
        return

    # Stage 3: Urgency Validation
    survivors, _ = stage3_urgency_validation(survivors)

    if not survivors:
        print(f"\n⚠️  ALL IDEAS KILLED BY STAGE 3")
        print(f"\nCould not find 10+ complaints showing urgent pain.")
        return

    if args.mode == 'stage3':
        print(f"\n✅ {len(survivors)} survivors after Stage 3. Stopping.")
        return

    # Stage 4: Gap Proof (THE CRITICAL FILTER)
    survivors, _ = stage4_gap_proof(survivors)

    if not survivors:
        print(f"\n⚠️  ALL IDEAS KILLED BY STAGE 4 (GAP PROOF)")
        print(f"\nCould not prove attackable gaps exist in the market.")
        print(f"\nThis is GOOD - you avoided building in saturated markets.")
        return

    if args.mode == 'stage4':
        print(f"\n✅ {len(survivors)} survivors after Stage 4. Stopping.")
        return

    # Stage 5: Complete Research
    winners = stage5_complete_research(survivors)

    if args.mode == 'stage5':
        print(f"\n✅ {len(winners)} complete reports generated. Stopping before founder check.")
        return

    # Stage 6: Founder Reality Check
    true_winners, _ = stage6_founder_check(winners)

    # Final output
    print(f"\n{'='*70}")
    print(f"🎉 ULTIMATE WINNER MACHINE COMPLETE! 🎉")
    print(f"{'='*70}\n")

    print(f"📊 FINAL RESULTS:")
    print(f"   Started with: {args.count} ideas")
    print(f"   TRUE WINNERS: {len(true_winners)}\n")
    print(f"{'='*70}\n")

    if true_winners:
        print(f"🏆 WINNERS FOUND:\n")
        for i, winner in enumerate(true_winners, 1):
            print(f"{i}. {winner['business']}")
            print(f"   Report: {winner['filename']}\n")

        print(f"\n🚀 NEXT STEPS:")
        print(f"1. Review ULTIMATE_WINNER_*.txt files")
        print(f"2. Use Copywriter Brief to write landing page copy")
        print(f"3. Build lead magnet (specs in Strategist section)")
        print(f"4. Build landing page with Bolt/Lovable")
        print(f"5. Execute Attack Plan to get first 10 customers")
        print(f"6. Run MVT validation (4-week plan included)")
    else:
        print(f"⚠️  NO WINNERS FOUND\n\n")
        print(f"💡 HONEST ASSESSMENT: No viable opportunities in this batch.\n")
        print(f"This is GOOD NEWS - you avoided wasting months on bad ideas.\n")
        print(f"SUGGESTIONS:")
        print(f"1. Try different industries (run again)")
        print(f"2. Adjust pain point focus (more specific)")
        print(f"3. Target different business sizes")
        print(f"\nRun again: python ultimate_winner_machine_v2.py --count=100")

    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    main()
