#!/usr/bin/env python3
"""
THE ULTIMATE WINNER MACHINE v1.0
One unified system to find TRUE business opportunities

Usage:
  python winner_machine.py --mode=full      # Run all stages (default)
  python winner_machine.py --mode=generate  # Just generate ideas
  python winner_machine.py --mode=stage1    # Run Stage 1 only
  python winner_machine.py --mode=stage5    # Run Stage 5 only
  python winner_machine.py --resume         # Continue from last checkpoint
"""

import os
import sys
import time
import re
import argparse
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Pain Point Research")

if not OPENAI_API_KEY:
    print("❌ No OPENAI_API_KEY in .env")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = Credentials.from_service_account_file('google-credentials.json', scopes=SCOPES)
gc = gspread.authorize(creds)
sheet = gc.open(GOOGLE_SHEET_NAME)

# ============================================================================
# CONFIGURATION
# ============================================================================

EXCLUDED_INDUSTRIES = [
    "healthcare", "medical", "hospital", "clinic", "doctor", "physician", "nurse",
    "insurance", "health insurance", "life insurance",
    "banking", "finance", "financial services", "fintech", "payment processing",
    "legal", "law firm", "attorney", "lawyer",
    "real estate", "realty", "property sales", "realtor", "mls",
    "pharmacy", "pharmaceutical sales", "drug", "dental", "dentist",
    "childcare", "daycare", "preschool", "education", "school", "university", "k-12",
    "senior care", "nursing home", "assisted living", "home health",
    "counseling", "therapy", "mental health", "psychologist"
]

RATE_LIMIT_DELAY = 1.0  # seconds between API calls

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def call_openai(prompt, max_tokens=4000, temperature=0.3):
    """Call OpenAI with rate limiting"""
    time.sleep(RATE_LIMIT_DELAY)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a world-class business analyst. You provide data-driven insights with real evidence and sources."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"   ERROR: {e}", flush=True)
        return None

def parse_verdict(text):
    """Extract verdict from AI response"""
    if not text:
        return "KILL"

    text_upper = text.upper()

    if "VERDICT: KILL" in text_upper or "VERDICT:KILL" in text_upper:
        return "KILL"
    if "VERDICT: PASS" in text_upper or "VERDICT:PASS" in text_upper or "VERDICT: PROCEED" in text_upper:
        return "PASS"

    # Default to KILL (be brutal)
    return "KILL"

def check_excluded_industry(business_type):
    """Check if business is in excluded list"""
    business_lower = business_type.lower()
    for excluded in EXCLUDED_INDUSTRIES:
        if excluded in business_lower:
            return True, excluded
    return False, None

def log_to_sheet(sheet_name, row_data):
    """Log data to Google Sheet"""
    try:
        ws = sheet.worksheet(sheet_name)
        ws.append_row(row_data)
    except:
        pass  # Fail silently if sheet doesn't exist

# ============================================================================
# STAGE 0: INTELLIGENT IDEA GENERATION
# ============================================================================

def generate_ideas(count=100):
    """Generate pre-filtered business ideas"""
    print(f"\n{'='*70}")
    print(f"🧠 STAGE 0: INTELLIGENT IDEA GENERATION")
    print(f"{'='*70}\n")
    print(f"Generating {count} pre-filtered ideas...", flush=True)

    prompt = f"""Generate {count} ultra-specific pain points for GROWING businesses with MONEY to spend.

STRICT REQUIREMENTS:

✅ ALLOWED INDUSTRIES ONLY:
- Construction/General Contractors
- Manufacturing (discrete & process)
- Retail (physical stores, NOT e-commerce platforms)
- Hospitality (restaurants, hotels, catering, bars)
- Logistics/Transportation/Freight
- Property Maintenance/Facilities Management
- Wholesale Distribution
- Agriculture/Farming/Agribusiness
- Marketing/Advertising Agencies
- Event Planning/Event Venues
- Professional Services (consulting, training, recruiting)
- Landscaping/Grounds Maintenance
- Commercial Cleaning/Janitorial
- Equipment Rental
- Print/Signage/Graphics
- Warehousing/Fulfillment/3PL
- HVAC/Plumbing/Electrical Contractors
- Food Service/Catering
- Auto Repair/Body Shops
- Fitness/Gyms (NOT personal training/coaching)

❌ ABSOLUTELY EXCLUDED:
- Healthcare/Medical/Dental/Veterinary
- Insurance/Financial Services
- Legal/Law Firms
- Real Estate Sales/Brokerage
- Pharmacy/Pharmaceutical
- Education/Schools/Childcare
- Senior Care/Home Health
- Counseling/Therapy

🎯 FOCUS ON:
- Industries growing >10% YoY
- Operational/workflow pain (NOT vanity problems)
- Businesses already spending $5k+/year on software
- Clear decision makers (VP, Director, Owner titles)
- Urgent pain (revenue loss, compliance risk, scaling blocker)

💡 PROBLEM TYPES:
- Manual data entry/reconciliation (spreadsheet hell)
- Communication chaos (phone tag, email overload)
- Scheduling/coordination nightmares
- Compliance/documentation burdens
- Financial tracking pain (invoicing, billing, payments)

EXAMPLES (don't repeat):
HVAC contractors,Coordinating emergency service calls with 15+ technicians in the field via phone tag and text messages
Food distributors,Reconciling delivery manifests with invoices across 200+ restaurant clients using Excel
Equipment rental companies,Tracking maintenance schedules for 500+ rental units using paper logbooks
Event venues,Managing vendor contracts and payment schedules across 50+ annual events through email

Generate {count} NEW ideas. Be specific about the business type and the exact pain.

Format EXACTLY as CSV (no headers, no extra text):
Business Type,Specific Pain Point"""

    result = call_openai(prompt, max_tokens=8000, temperature=0.9)

    if not result:
        print("❌ Failed to generate ideas")
        return []

    ideas = []
    for line in result.strip().split('\n'):
        if ',' in line and len(line) > 20:
            parts = [p.strip() for p in line.split(',', 1)]
            if len(parts) == 2 and len(parts[0]) > 0:
                ideas.append({"business": parts[0], "pain": parts[1]})

    print(f"✓ Generated {len(ideas)} ideas", flush=True)

    # Save to Google Sheet
    try:
        queue = sheet.worksheet("Ideas Queue")
        current_max = len(queue.get_all_values())

        for i, idea in enumerate(ideas):
            queue.append_row([
                current_max + i,
                idea["business"],
                idea["pain"],
                "Pending",
                datetime.now().strftime("%Y-%m-%d"),
                ""
            ])
        print(f"✓ Saved to Google Sheet (Ideas Queue)", flush=True)
    except Exception as e:
        print(f"⚠️  Warning: Could not save to sheet: {e}", flush=True)

    return ideas

# ============================================================================
# STAGE 1: INSTANT KILL FILTERS
# ============================================================================

def stage1_instant_kills(ideas):
    """Fast, cheap filters - kill 70-80%"""
    print(f"\n{'='*70}")
    print(f"⚡ STAGE 1: INSTANT KILL FILTERS")
    print(f"{'='*70}\n")
    print(f"Processing {len(ideas)} ideas with brutal filters...", flush=True)

    survivors = []
    killed = []

    for i, idea in enumerate(ideas):
        print(f"\n[{i+1}/{len(ideas)}] {idea['business'][:50]}...", flush=True)

        # Check 1: Excluded Industry
        is_excluded, keyword = check_excluded_industry(idea['business'])
        if is_excluded:
            reason = f"KILL: Excluded industry ({keyword})"
            print(f"   ❌ {reason}", flush=True)
            killed.append({**idea, "kill_reason": reason, "stage": 1})
            log_to_sheet("Ideas Queue", [idea.get('id', ''), idea['business'], idea['pain'], reason, datetime.now().strftime("%Y-%m-%d")])
            continue

        # Check 2: Growth Rate (quick check)
        growth_prompt = f"""Quick growth check for: {idea['business']}

Is this industry growing >10% annually? Answer with PASS or KILL and brief reason.

Response format:
VERDICT: [PASS or KILL]
REASON: [One sentence why]"""

        growth_result = call_openai(growth_prompt, max_tokens=200, temperature=0.1)
        growth_verdict = parse_verdict(growth_result)

        if growth_verdict == "KILL":
            reason = f"KILL: Low growth (<10% YoY)"
            print(f"   ❌ {reason}", flush=True)
            killed.append({**idea, "kill_reason": reason, "stage": 1})
            continue

        # Check 3: API Feasibility (quick check)
        api_prompt = f"""For solving: {idea['pain']} in {idea['business']}

Can this be built with PUBLIC APIs only (Google Maps, weather, etc.) OR web scraping OR no external data?

Would it require enterprise-only APIs (Salesforce, SAP, medical records, MLS, insurance databases)?

VERDICT: [PASS if public APIs sufficient, KILL if enterprise APIs required]
REASON: [One sentence]"""

        api_result = call_openai(api_prompt, max_tokens=200, temperature=0.1)
        api_verdict = parse_verdict(api_result)

        if api_verdict == "KILL":
            reason = f"KILL: Requires enterprise APIs"
            print(f"   ❌ {reason}", flush=True)
            killed.append({**idea, "kill_reason": reason, "stage": 1})
            continue

        # PASSED STAGE 1
        print(f"   ✅ PASS Stage 1", flush=True)
        survivors.append({**idea, "stage1_analysis": growth_result + "\n\n" + api_result})

    print(f"\n{'='*70}")
    print(f"STAGE 1 COMPLETE:")
    print(f"   Input: {len(ideas)}")
    print(f"   Killed: {len(killed)} ({len(killed)/len(ideas)*100:.1f}%)")
    print(f"   Survivors: {len(survivors)} ({len(survivors)/len(ideas)*100:.1f}%)")
    print(f"{'='*70}\n")

    return survivors, killed

# ============================================================================
# STAGE 2: BUDGET REALITY CHECK
# ============================================================================

def stage2_budget_check(ideas):
    """Validate budget and buying power - kill 50%"""
    print(f"\n{'='*70}")
    print(f"💰 STAGE 2: BUDGET REALITY CHECK")
    print(f"{'='*70}\n")
    print(f"Processing {len(ideas)} ideas for budget validation...", flush=True)

    survivors = []
    killed = []

    for i, idea in enumerate(ideas):
        print(f"\n[{i+1}/{len(ideas)}] {idea['business'][:50]}...", flush=True)

        budget_prompt = f"""Budget validation for: {idea['business']} - {idea['pain'][:100]}

Research and answer:

1. SOFTWARE SPENDING: Do {idea['business']} already spend on software?
   - Search G2/Capterra for tools used by this industry
   - Find pricing evidence ($X/month)
   - Minimum: Prove $5,000+/year software spending

2. DECISION MAKERS: Who controls the budget?
   - Specific job titles (VP Operations, Director, Owner?)
   - Are they reachable? (LinkedIn, forums, conferences?)

3. DEAL SIZE: What would they pay for this solution?
   - Based on competitive pricing
   - Minimum ACV: $1,200/year ($100/month)

FORMAT:
## SOFTWARE SPENDING
[Evidence of existing spending with $amounts]

## DECISION MAKERS
[Specific titles + where to reach them]

## DEAL SIZE
ACV: $[X]/year (realistic estimate)

VERDICT: [PASS if all 3 criteria met, KILL if any missing]
- PASS criteria: $5k+ existing spend, clear decision makers, $1,200+ ACV
- KILL otherwise

Be honest. Default to KILL if evidence is weak."""

        result = call_openai(budget_prompt, max_tokens=2000)
        verdict = parse_verdict(result)

        if verdict == "KILL":
            reason = "KILL: Failed budget validation (Stage 2)"
            print(f"   ❌ {reason}", flush=True)
            killed.append({**idea, "kill_reason": reason, "stage": 2})
            continue

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
# STAGE 3: URGENCY & PAIN DEPTH
# ============================================================================

def stage3_urgency_validation(ideas):
    """Validate urgency and pain intensity - kill 50%"""
    print(f"\n{'='*70}")
    print(f"🔥 STAGE 3: URGENCY & PAIN VALIDATION")
    print(f"{'='*70}\n")
    print(f"Processing {len(ideas)} ideas for urgency...", flush=True)

    survivors = []
    killed = []

    for i, idea in enumerate(ideas):
        print(f"\n[{i+1}/{len(ideas)}] {idea['business'][:50]}...", flush=True)

        urgency_prompt = f"""Urgency validation for: {idea['business']} - {idea['pain'][:100]}

REQUIREMENTS:

1. FIND 5+ COMPLAINTS (2024-2025 ONLY):
   - Real quotes from business owners
   - Must include URLs/sources
   - Must show frustration/impact

2. URGENCY DRIVERS:
   - Regulatory deadline forcing change?
   - Revenue loss if not solved?
   - Competitive threat?
   - Scaling blocker?

3. PAIN INTENSITY SCORE (1-10):
   - 1-3: Nice to have
   - 4-6: Moderate pain
   - 7-8: Urgent, actively seeking
   - 9-10: Hair on fire, buying NOW

   MINIMUM REQUIRED: 7/10

FORMAT:
## COMPLAINTS (with URLs)
1. "[Quote]" - [URL] - [Date]
2. "[Quote]" - [URL] - [Date]
[... 5 total]

## URGENCY DRIVERS
[List forcing functions]

## PAIN SCORE: [X]/10
[Justification]

VERDICT: [PASS if 5+ complaints + 7+ score, KILL otherwise]"""

        result = call_openai(urgency_prompt, max_tokens=3000)
        verdict = parse_verdict(result)

        # Also check for pain score
        score_match = re.search(r'PAIN SCORE:\s*(\d+)', result)
        if score_match:
            score = int(score_match.group(1))
            if score < 7:
                verdict = "KILL"

        if verdict == "KILL":
            reason = "KILL: Low urgency or insufficient pain (Stage 3)"
            print(f"   ❌ {reason}", flush=True)
            killed.append({**idea, "kill_reason": reason, "stage": 3})
            continue

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
# STAGE 4: COMPETITIVE MOAT
# ============================================================================

def stage4_competitive_moat(ideas):
    """Analyze competitive positioning - kill 30%"""
    print(f"\n{'='*70}")
    print(f"🏰 STAGE 4: COMPETITIVE MOAT ANALYSIS")
    print(f"{'='*70}\n")
    print(f"Processing {len(ideas)} ideas for competitive gaps...", flush=True)

    survivors = []
    killed = []

    for i, idea in enumerate(ideas):
        print(f"\n[{i+1}/{len(ideas)}] {idea['business'][:50]}...", flush=True)

        moat_prompt = f"""Competitive analysis for: {idea['business']} - {idea['pain'][:100]}

RESEARCH:

1. CURRENT SOLUTIONS:
   - Search G2/Capterra for existing tools
   - Classify: STRONG (purpose-built, good reviews) or WEAK (generic, poor fit)
   - KILL CRITERIA: 3+ strong competitors

2. MARKET GAPS:
   - What do ALL competitors miss?
   - Filter reviews by 2024-2025, low ratings
   - Find the opportunity

3. DEFENSIBILITY (Moat potential):
   - Network effects possible?
   - Data advantage buildable?
   - High switching costs?
   - Vertical expertise deep enough?

4. WHY INCUMBENTS HAVEN'T FIXED IT:
   - Technical debt?
   - Business model conflict?
   - Market too small for them?

FORMAT:
## COMPETITIVE LANDSCAPE
Strong: [List]
Weak: [List]

## MARKET GAP
[What's missing that you can own]

## MOAT OPPORTUNITY
[How defensible this could be]

## VERDICT: [KILL if 3+ strong competitors, PASS if clear opening]"""

        result = call_openai(moat_prompt, max_tokens=3000)
        verdict = parse_verdict(result)

        if verdict == "KILL":
            reason = "KILL: Too competitive or no defensibility (Stage 4)"
            print(f"   ❌ {reason}", flush=True)
            killed.append({**idea, "kill_reason": reason, "stage": 4})
            continue

        print(f"   ✅ PASS Stage 4", flush=True)
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
# STAGE 5: COMPLETE RESEARCH + STRATEGIST
# ============================================================================

def stage5_final_research(ideas):
    """Complete deep research + strategist output"""
    print(f"\n{'='*70}")
    print(f"🔬 STAGE 5: COMPLETE RESEARCH + STRATEGIST")
    print(f"{'='*70}\n")
    print(f"Deep research on {len(ideas)} finalists...", flush=True)

    winners = []

    for i, idea in enumerate(ideas):
        print(f"\n[{i+1}/{len(ideas)}] DEEP DIVE: {idea['business']}", flush=True)
        print(f"{'='*70}", flush=True)

        # Part 1: The Researcher (Complete Framework)
        research_prompt = f"""COMPLETE BUSINESS VALIDATION REPORT

TARGET: {idea['business']}
PROBLEM: {idea['pain']}

PREVIOUS VALIDATION:
- Stage 1: {idea.get('stage1_analysis', '')[:500]}
- Stage 2: {idea.get('stage2_analysis', '')[:500]}
- Stage 3: {idea.get('stage3_analysis', '')[:500]}
- Stage 4: {idea.get('stage4_analysis', '')[:500]}

YOUR TASK: Synthesize everything and provide final assessment.

PROVIDE:

## MARKET VALIDATION
- Market size (TAM): [specific number with source]
- Growth rate: [%/year with source]
- Demand evidence: [search volumes, surveys, industry data]

## COMPETITIVE POSITIONING
- Key competitors: [list with gaps]
- Differentiation opportunities: [specific features/positioning]
- Sustainable advantage: [how defensible]

## UNIT ECONOMICS
- Pricing strategy: [tiers with rationale]
- Est. CAC: $[X]
- Est. LTV: $[Y] (3-year)
- LTV:CAC ratio: [X]:1 (healthy if >3:1)
- Gross margin: [%]

## OPERATIONS & SCALABILITY
- Resources to launch: [team, tech, capital]
- Technical complexity: [1-10 score]
- Scalability assessment: [can it 10x without linear costs?]

## RISKS & RED FLAGS
- Top 3 risks: [list with mitigation]
- Regulatory barriers: [any compliance issues?]
- Why this could fail: [honest assessment]

## VALIDATION EXPERIMENTS
1. [Experiment] - $[cost] - [days] - [success criteria]
2. [Experiment] - $[cost] - [days] - [success criteria]
3. [Experiment] - $[cost] - [days] - [success criteria]"""

        research_result = call_openai(research_prompt, max_tokens=6000)

        # Part 2: The Strategist (Lead Magnet Strategy)
        strategist_prompt = f"""STRATEGIST OUTPUT

Based on this validated opportunity:
TARGET: {idea['business']}
PAIN: {idea['pain']}

PROVIDE:

## VALUE PROPOSITION
"I help [specific audience] solve [specific painful problem] so they can [specific outcome]."

Quality check:
- Specific? (not generic)
- Emotional? (feels the pain)
- Obvious? (immediate clarity)

## LEAD MAGNET IDEAS (Rank by speed/cost/conversion)
1. [Idea] - Build time: [X hours] - Value: [what they get]
2. [Idea] - Build time: [X hours] - Value: [what they get]
3. [Idea] - Build time: [X hours] - Value: [what they get]
4. [Idea] - Build time: [X hours] - Value: [what they get]
5. [Idea] - Build time: [X hours] - Value: [what they get]

TOP PICK: [#X] - [Why this one wins]

## MVT VALIDATION PLAN
Week 1: [Action + success metric]
Week 2: [Action + success metric]
Week 3: [Action + success metric]
Week 4: [Decision point - build or pivot]

## FIRST 10 CUSTOMERS
Where to find: [Specific communities with URLs]
Outreach approach: [Exact message strategy]
Timeline: [Days to 10 conversations]

## GTM STRATEGY
- Content pillars: [3 topics]
- Platform: [Primary channel + why]
- Posting cadence: [X/week]
- Distribution: [Where target audience is]

## STRAIGHT-LINE MARKETING
Content → Lead Magnet → Offer (all solving same pain, same way, same person)
[Describe the flow]"""

        strategist_result = call_openai(strategist_prompt, max_tokens=4000)

        # Part 3: Final Verdict
        final_prompt = f"""FINAL VERDICT

Review all research and strategy for:
{idea['business']} - {idea['pain']}

RESEARCH SUMMARY:
{research_result[:1000]}

STRATEGY SUMMARY:
{strategist_result[:1000]}

PROVIDE:

## OVERALL SCORE (1-10): [X]/10

## TOP 3 STRENGTHS
1. [Strength]
2. [Strength]
3. [Strength]

## TOP 3 CONCERNS
1. [Concern + mitigation]
2. [Concern + mitigation]
3. [Concern + mitigation]

## FINAL RECOMMENDATION
VERDICT: [BUILD or PIVOT]

If BUILD:
- Why this is a winner
- Confidence level: [High/Medium]
- Next immediate action

If PIVOT:
- What's missing
- Alternative angle to consider"""

        final_result = call_openai(final_prompt, max_tokens=2000)

        # Compile full report
        full_report = f"""# TRUE WINNER REPORT

TARGET: {idea['business']}
PROBLEM: {idea['pain']}
DATE: {datetime.now().strftime("%Y-%m-%d")}

{'='*70}
THE RESEARCHER: COMPLETE VALIDATION
{'='*70}

{research_result}

{'='*70}
THE STRATEGIST: GO-TO-MARKET PLAN
{'='*70}

{strategist_result}

{'='*70}
FINAL ASSESSMENT
{'='*70}

{final_result}

{'='*70}
COPYWRITER BRIEF
{'='*70}

This report contains everything needed for copywriting:
- Target audience: {idea['business']}
- Core pain: {idea['pain']}
- Value proposition: [Extract from Strategist section]
- Lead magnet: [Top pick from Strategist section]
- Tone/Voice: Bold, specific, results-focused
- Evidence: All citations included above

Ready for landing page, emails, and content creation.
"""

        # Save report
        safe_name = re.sub(r'[^\w\s-]', '', idea['business'])[:30].replace(' ', '_')
        filename = f"WINNER_{i+1}_{safe_name}.txt"

        with open(filename, 'w') as f:
            f.write(full_report)

        print(f"   ✅ Complete report saved: {filename}", flush=True)

        # Check if it's truly a winner
        if "BUILD" in final_result.upper():
            winners.append({**idea, "report": full_report, "filename": filename})

            # Save to TRUE WINNERS sheet
            try:
                winners_sheet = sheet.worksheet("TRUE WINNERS")
                winners_sheet.append_row([
                    len(winners),
                    idea['business'],
                    idea['pain'],
                    "TRUE WINNER ✅",
                    full_report[:500],
                    datetime.now().strftime("%Y-%m-%d")
                ])
            except:
                pass

    print(f"\n{'='*70}")
    print(f"STAGE 5 COMPLETE:")
    print(f"   Finalists researched: {len(ideas)}")
    print(f"   TRUE WINNERS: {len(winners)}")
    print(f"{'='*70}\n")

    return winners

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='The Ultimate Winner Machine')
    parser.add_argument('--mode', default='full', choices=['full', 'generate', 'stage1', 'stage2', 'stage3', 'stage4', 'stage5'],
                       help='Execution mode')
    parser.add_argument('--count', type=int, default=100, help='Number of ideas to generate')
    parser.add_argument('--resume', action='store_true', help='Resume from last checkpoint')

    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         🏆 THE ULTIMATE WINNER MACHINE v1.0 🏆                  ║
║                                                                  ║
║  One Unified System to Find TRUE Business Opportunities         ║
║                                                                  ║
║  Stage 0: Smart Generation    (100 pre-filtered ideas)         ║
║  Stage 1: Instant Kills       (Kill 70-80%)                    ║
║  Stage 2: Budget Check        (Kill 50% more)                  ║
║  Stage 3: Urgency Validation  (Kill 50% more)                  ║
║  Stage 4: Competitive Moat    (Kill 30% more)                  ║
║  Stage 5: Final Research      (1-2 TRUE WINNERS or ZERO)       ║
║                                                                  ║
║  Honest Output: Better 0/100 than 1 false positive             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    if args.mode == 'full' or args.mode == 'generate':
        ideas = generate_ideas(args.count)
        if args.mode == 'generate':
            return
    else:
        # Load from sheet for partial runs
        ideas = []  # Would load from checkpoint

    if args.mode == 'full' or args.mode == 'stage1':
        survivors, _ = stage1_instant_kills(ideas)
        ideas = survivors

    if args.mode == 'full' or args.mode == 'stage2':
        survivors, _ = stage2_budget_check(ideas)
        ideas = survivors

    if args.mode == 'full' or args.mode == 'stage3':
        survivors, _ = stage3_urgency_validation(ideas)
        ideas = survivors

    if args.mode == 'full' or args.mode == 'stage4':
        survivors, _ = stage4_competitive_moat(ideas)
        ideas = survivors

    if args.mode == 'full' or args.mode == 'stage5':
        winners = stage5_final_research(ideas)

        print(f"""
{'='*70}
🎉 WINNER MACHINE COMPLETE! 🎉
{'='*70}

📊 FINAL RESULTS:
   Started with: {args.count} ideas
   TRUE WINNERS: {len(winners)}

{'='*70}

{'🏆 WINNERS FOUND:' if winners else '⚠️  NO WINNERS FOUND'}
""")

        if winners:
            for i, w in enumerate(winners):
                print(f"{i+1}. {w['business']}")
                print(f"   Report: {w['filename']}")
                print()

            print(f"""
🚀 NEXT STEPS:
1. Review WINNER_*.txt files
2. These are ready for The Copywriter
3. Build lead magnet from Strategist section
4. Launch MVT validation
""")
        else:
            print(f"""
💡 HONEST ASSESSMENT: No viable opportunities in this batch.

This is GOOD NEWS - you avoided wasting months on bad ideas.

SUGGESTIONS:
1. Try different industries (run again)
2. Adjust pain point focus (more specific)
3. Target different business sizes

Run again: python winner_machine.py --count=100
""")

    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
