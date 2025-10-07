#!/usr/bin/env python3
"""
STAGE 3: Deep Research (Final Winners)
Only runs on ideas that passed BOTH Growth & Budget filters
Comprehensive analysis ready for "The Strategist"
"""

import os
import sys
import time
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

def call_openai(prompt, max_tokens=5000):
    """Call OpenAI API"""
    time.sleep(1)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a world-class business researcher. You create comprehensive opportunity reports with real evidence, actionable insights, and clear next steps."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"   ERROR: {e}", flush=True)
        return None

def deep_research(row_num, niche, pain):
    """Stage 3: Comprehensive Deep Research"""
    print(f"\n{'='*70}", flush=True)
    print(f"🔬 DEEP RESEARCH #{row_num}: {niche}", flush=True)
    print(f"{'='*70}", flush=True)

    full_report = f"# OPPORTUNITY REPORT #{row_num}\n\nTARGET: {niche}\nPROBLEM: {pain}\n\n"

    # Research 1: Urgency & Pain Validation
    print(f"\n🔥 Research 1: Urgency & Pain Intensity...", flush=True)

    urgency_prompt = f"""Validate URGENCY of this problem:

TARGET: {niche}
PROBLEM: {pain}

Find evidence this is URGENT (not just annoying):

1. **Forcing Functions**
   - Regulatory deadlines forcing change?
   - Competitive threats (competitors solving this)?
   - Economic pressure (recession forcing efficiency)?
   - Technology shifts (old systems breaking)?

2. **Pain Severity Signals**
   - Search: "{niche} {pain} costing us" → revenue/profit impact
   - Search: "{niche} can't scale because" → growth blocker
   - Search: "{niche} {pain} compliance" → legal risk
   - Recent complaints (2024-2025) showing rising urgency

3. **Timing Signals**
   - Google Trends: Is search volume increasing?
   - Job postings: Hiring for roles to solve this?
   - Conference/event topics: Industry discussing this?

FORMAT:

## URGENCY DRIVERS
1. [Driver with evidence & source]
2. [Driver with evidence & source]
3. [Driver with evidence & source]

## PAIN QUOTES (2024-2025)
1. "[Quote]" - [Source URL] - [Date]
2. "[Quote]" - [Source URL] - [Date]
3. "[Quote]" - [Source URL] - [Date]

## URGENCY SCORE: [1-10]
- 1-3: Nice to have, low urgency
- 4-6: Moderate pain, eventual purchase
- 7-8: Urgent, actively seeking solutions
- 9-10: Hair on fire, buying NOW

Score: [X]/10 - [Justification]"""

    urgency_result = call_openai(urgency_prompt)
    full_report += f"\n{'='*70}\nURGENCY & PAIN VALIDATION\n{'='*70}\n{urgency_result}\n"
    print(f"   ✓ Complete", flush=True)

    # Research 2: Competitive Moat Analysis
    print(f"\n🏰 Research 2: Competitive Moat & Defensibility...", flush=True)

    moat_prompt = f"""Analyze competitive positioning and defensibility:

TARGET: {niche}
PROBLEM: {pain}

1. **Current Competitive Landscape**
   - G2/Capterra: Who are the players?
   - Filter reviews by 2024-2025 + low ratings
   - What are customers complaining about?

2. **Market Gaps (Your Opportunity)**
   - What do ALL competitors miss?
   - Underserved segments? (SMB vs Enterprise)
   - Geographic gaps? (regions not served well)
   - Feature gaps? (wish list items in reviews)

3. **Defensibility (Can You Build a Moat?)**
   - Network effects: Does value increase with more users?
   - Data advantage: Can you build proprietary data/insights?
   - Integration moat: Hard to rip out once embedded?
   - Brand/expertise: Can you become THE {niche} solution?

4. **Why Incumbents Haven't Fixed This**
   - Technical debt/legacy architecture?
   - Business model conflict (cannibalizes revenue)?
   - Market too small for them?
   - Different target customer?

FORMAT:

## COMPETITIVE GAPS
1. [Gap with evidence from reviews]
2. [Gap with evidence]
3. [Gap with evidence]

## MOAT OPPORTUNITIES
- Network Effects: [High/Medium/Low + how]
- Data Moat: [What data can you uniquely collect?]
- Switching Costs: [How sticky can this be?]
- Vertical Expertise: [How deep can you go?]

## DEFENSIBILITY SCORE: [1-10]
Score: [X]/10 - [Justification]"""

    moat_result = call_openai(moat_prompt)
    full_report += f"\n{'='*70}\nCOMPETITIVE MOAT ANALYSIS\n{'='*70}\n{moat_result}\n"
    print(f"   ✓ Complete", flush=True)

    # Research 3: Go-to-Market Strategy
    print(f"\n🎯 Research 3: Go-to-Market & Acquisition...", flush=True)

    gtm_prompt = f"""Design initial go-to-market strategy:

TARGET: {niche}
PROBLEM: {pain}

1. **Customer Discovery (First 10 Customers)**
   - Specific communities: [Subreddits, LinkedIn groups, Slack/Discord]
   - Direct outreach: Where to find decision makers?
   - Warm intros: Any connector communities?

2. **Lead Magnet Ideas (MVT - Minimum Viable Test)**
   - What free tool/resource would they download TODAY?
   - Must be: quick to build, valuable, related to problem
   - Examples: calculator, template, checklist, audit tool

3. **Validation Experiments (Before Building)**
   - Landing page test: Measure real interest
   - Concierge MVP: Manual service to prove willingness to pay
   - Direct outreach: 20 conversations to validate need

4. **Content Strategy**
   - Where does {niche} consume content?
   - What topics resonate? (based on popular posts/articles)
   - Influencers/champions in the space?

FORMAT:

## FIRST 10 CUSTOMERS
- **Where to find:** [Specific communities with URLs]
- **Outreach strategy:** [Exact approach]
- **Timeline:** [Days to get 10 conversations]

## LEAD MAGNET IDEAS (Rank by speed to build)
1. [Idea] - Can build in: [X hours] - Value: [what they get]
2. [Idea] - Can build in: [X hours] - Value: [what they get]
3. [Idea] - Can build in: [X hours] - Value: [what they get]

## VALIDATION PLAN ($0-500 budget)
1. **Week 1:** [Experiment + success metric]
2. **Week 2:** [Experiment + success metric]
3. **Week 3:** [Decision point - build or pivot]

## GTM SCORE: [1-10]
Score: [X]/10 - [Reachability + validation feasibility]"""

    gtm_result = call_openai(gtm_prompt)
    full_report += f"\n{'='*70}\nGO-TO-MARKET STRATEGY\n{'='*70}\n{gtm_result}\n"
    print(f"   ✓ Complete", flush=True)

    # Research 4: Final Synthesis & Recommendation
    print(f"\n✅ Research 4: Final Synthesis...", flush=True)

    final_prompt = f"""Create final recommendation:

All previous research for: {niche} - {pain}

URGENCY ANALYSIS:
{urgency_result[:1000]}

COMPETITIVE MOAT:
{moat_result[:1000]}

GTM STRATEGY:
{gtm_result[:1000]}

Synthesize everything into a final recommendation:

FORMAT:

## EXECUTIVE SUMMARY
[2-3 paragraphs: The opportunity, why now, why you can win]

## VALUE PROPOSITION (Nail this!)
"I help [specific {niche}] solve [specific painful problem] so they can [specific outcome]."

**Quality Check:**
- ✅ Specific? (not generic)
- ✅ Emotional? (feels the pain)
- ✅ Obvious? (immediate clarity)

## OPPORTUNITY SCORES
- **Growth Potential:** [X]/10
- **Budget/Willingness to Pay:** [X]/10
- **Urgency:** [X]/10
- **Competitive Moat:** [X]/10
- **GTM Feasibility:** [X]/10
- **OVERALL:** [X]/10

## TOP 3 STRENGTHS
1. [Strength]
2. [Strength]
3. [Strength]

## TOP 3 RISKS
1. [Risk + mitigation]
2. [Risk + mitigation]
3. [Risk + mitigation]

## RECOMMENDED NEXT STEPS (30 days)
**Week 1-2:**
1. [Specific action]
2. [Specific action]

**Week 3-4:**
1. [Specific action]
2. [Specific action]

## FINAL VERDICT
**PROCEED TO STRATEGIST?** [YES/NO + reasoning]

If YES: This is ready for Stage 2 (The Strategist) - lead magnet creation
If NO: [What's missing or what pivot to consider]"""

    final_result = call_openai(final_prompt, max_tokens=6000)
    full_report += f"\n{'='*70}\nFINAL SYNTHESIS & RECOMMENDATION\n{'='*70}\n{final_result}\n"
    print(f"   ✓ Complete", flush=True)

    # Check if it's a TRUE WINNER
    if "PROCEED TO STRATEGIST? YES" in final_result.upper() or "FINAL VERDICT: YES" in final_result.upper():
        return "🏆 TRUE WINNER - Ready for Strategist", full_report
    else:
        return "⚠️ MARGINAL - Needs refinement", full_report

def main():
    """Process ideas through Deep Research"""
    print("\n🚀 STAGE 3: DEEP RESEARCH (Final Analysis)", flush=True)
    print("="*70, flush=True)
    print("🔬 Comprehensive research on filtered opportunities", flush=True)
    print("🎯 Output: Complete reports for TRUE WINNERS", flush=True)
    print("="*70, flush=True)

    budget_pass = sheet.worksheet("Stage 2: Budget Pass")
    winners = sheet.worksheet("TRUE WINNERS")

    all_rows = budget_pass.get_all_values()

    if len(all_rows) <= 1:
        print("\n❌ No ideas from Stage 2. Run: python stage2_budget_validator.py", flush=True)
        return

    processed = 0
    true_winners = 0
    marginal = 0

    for i, row in enumerate(all_rows[1:], start=2):
        if len(row) < 3:
            continue

        row_num = row[0]
        niche = row[1]
        pain = row[2]

        result_status, full_report = deep_research(row_num, niche, pain)

        processed += 1

        if "TRUE WINNER" in result_status:
            # Save complete report
            safe_niche = niche.replace(' ', '_').replace('/', '-')[:30]
            filename = f"WINNER_{row_num}_{safe_niche}.txt"
            with open(filename, 'w') as f:
                f.write(full_report)

            # Add to Winners sheet
            winners.append_row([
                row_num,
                niche,
                pain,
                result_status,
                full_report[:1500],
                datetime.now().strftime("%Y-%m-%d")
            ])
            true_winners += 1
            print(f"\n🏆 TRUE WINNER!", flush=True)
            print(f"   📄 Report saved: {filename}", flush=True)

            # Update budget_pass sheet
            budget_pass.update_cell(i, 4, "TRUE WINNER ✅")

        else:
            marginal += 1
            print(f"\n⚠️  Marginal opportunity (may need pivot)", flush=True)
            budget_pass.update_cell(i, 4, "Marginal - Review")

        print(f"\n📊 Progress: {processed} processed | {true_winners} TRUE WINNERS | {marginal} marginal", flush=True)

    print(f"\n{'='*70}", flush=True)
    print(f"✅ RESEARCH COMPLETE!", flush=True)
    print(f"   Processed: {processed}", flush=True)
    print(f"   TRUE WINNERS: {true_winners}", flush=True)
    print(f"   Marginal: {marginal}", flush=True)
    print(f"\n🎯 Next: Review WINNER_*.txt reports", flush=True)
    print(f"🚀 Ready for: Stage 2 - The Strategist (lead magnet creation)", flush=True)
    print(f"{'='*70}\n", flush=True)

if __name__ == "__main__":
    main()
