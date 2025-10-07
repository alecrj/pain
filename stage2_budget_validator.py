#!/usr/bin/env python3
"""
STAGE 2: Budget Validator
Proves businesses WILL PAY and identifies buying authority
Only processes ideas that passed Stage 1
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

def call_openai(prompt, max_tokens=4000):
    """Call OpenAI API"""
    time.sleep(1)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a budget analyst. You find PROOF that businesses spend money on solutions. You identify decision makers and validate willingness to pay."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"   ERROR: {e}", flush=True)
        return None

def parse_verdict(text):
    """Extract verdict"""
    if not text:
        return "KILL"

    text_upper = text.upper()

    if "VERDICT: KILL" in text_upper or "VERDICT:KILL" in text_upper:
        return "KILL"
    if "VERDICT: PASS" in text_upper or "VERDICT:PASS" in text_upper or "VERDICT: PROCEED" in text_upper:
        return "PASS"

    return "KILL"

def budget_validator(row_num, niche, pain):
    """Stage 2: Budget & Buying Authority Validation"""
    print(f"\n{'='*70}", flush=True)
    print(f"💰 BUDGET VALIDATOR #{row_num}: {niche}", flush=True)
    print(f"{'='*70}", flush=True)

    full_analysis = f"TARGET: {niche}\nPROBLEM: {pain}\n\n"

    # Check 1: Existing Software Spending
    print(f"\n💳 Check 1: Existing Software Spending...", flush=True)

    spending_prompt = f"""Research ACTUAL software spending for this market:

TARGET MARKET: {niche}
PROBLEM: {pain}

Find PROOF that these businesses ALREADY SPEND MONEY on software:

1. **G2/Capterra Analysis**
   - Search for tools used by {niche}
   - What are they paying? (look for pricing pages, reviews mentioning "$X/month")
   - Categories they spend in (project management, scheduling, etc.)

2. **Similar Tool Pricing**
   - Find 3-5 tools targeting {niche} or solving similar problems
   - Extract pricing: Basic, Pro, Enterprise tiers
   - Note: Companies CURRENTLY paying = proven budget exists

3. **Review Analysis - Willingness to Pay**
   - Search G2/Capterra for phrases: "expensive but worth it", "ROI", "saves us $X"
   - Are customers saying price is justified?
   - What features justify the cost?

4. **Services Spending (Alternative Signal)**
   - Are there consultants/agencies serving {niche}?
   - What do they charge? (day rates, project fees)
   - High service spending = willingness to pay for software alternative

FORMAT YOUR RESPONSE:

## EXISTING SOFTWARE SPENDING
| Tool Name | Category | Pricing | # of {niche} Users |
|-----------|----------|---------|-------------------|
| [Tool 1] | [Category] | $X-Y/mo | [Est. from reviews] |
| [Tool 2] | [Category] | $X-Y/mo | [Est. from reviews] |

## WILLINGNESS TO PAY SIGNALS
1. [Quote from review showing ROI/value] - [Source]
2. [Quote showing price acceptance] - [Source]
3. [Quote showing budget availability] - [Source]

## SERVICES MARKET (if applicable)
- Consultant/Agency: [Name/Type]
- Day Rate: $X - $Y
- Evidence of {niche} using these services: [Source]

## VERDICT: [KILL or PASS]
- KILL if: No evidence of software spending, all free tools, no budget signals
- PASS if: Clear evidence of $X,000+/year software spending with 3+ tools/sources

Require PROOF of existing budgets."""

    spend_result = call_openai(spending_prompt)
    spend_verdict = parse_verdict(spend_result)
    full_analysis += f"\n{'='*70}\nCHECK 1: SPENDING ANALYSIS\n{'='*70}\n{spend_result}\n"

    print(f"   {spend_verdict}", flush=True)

    if spend_verdict == "KILL":
        return "KILL: No Budget Evidence", full_analysis

    # Check 2: Buying Authority & Decision Makers
    print(f"\n👔 Check 2: Buying Authority Analysis...", flush=True)

    authority_prompt = f"""Identify WHO controls the budget and HOW they buy:

TARGET MARKET: {niche}
PROBLEM: {pain}

Research WHO makes software purchasing decisions:

1. **Job Titles with Budget Authority**
   - Search LinkedIn for {niche} job postings mentioning "budget", "P&L", "purchasing authority"
   - Common decision-maker titles: VP Ops, Director of X, Owner, GM?
   - Do they have procurement teams or is it owner-direct?

2. **Buying Process**
   - How do {niche} typically buy software? (credit card, RFP, procurement?)
   - Average sales cycle for similar tools (30 days? 6 months?)
   - POC/trial expectations?

3. **Influencers vs Decision Makers**
   - Who uses the tool? (end users, managers)
   - Who approves the purchase? (may be different!)
   - Who champions it internally?

4. **Budget Cycle**
   - Annual budgets or ad-hoc spending?
   - Best time to sell? (fiscal year start, end?)

FORMAT YOUR RESPONSE:

## DECISION MAKERS
- **Primary Title:** [VP Operations, Owner, Director of X]
- **Budget Range:** $X - $Y (estimated purchasing authority)
- **Reporting Structure:** [Who they report to]
- **LinkedIn Count:** [# of these roles in {niche} space]

## BUYING PROCESS
- **Typical Process:** [Credit card signup / RFP / Procurement / Direct owner decision]
- **Sales Cycle:** [30-90 days / 6+ months]
- **Key Requirements:** [Demo, trial, references, security review]

## REACHABILITY
- **Where they hang out:** [LinkedIn groups, industry forums, conferences]
- **Influencers they follow:** [Industry thought leaders]
- **Communities:** [Specific Slack/Discord/Facebook groups]

## VERDICT: [KILL or PASS]
- KILL if: Can't identify decision makers, unreachable, complex enterprise sales required
- PASS if: Clear decision makers, reachable, understood buying process

Require clear path to buyers."""

    authority_result = call_openai(authority_prompt)
    authority_verdict = parse_verdict(authority_result)
    full_analysis += f"\n{'='*70}\nCHECK 2: BUYING AUTHORITY\n{'='*70}\n{authority_result}\n"

    print(f"   {authority_verdict}", flush=True)

    if authority_verdict == "KILL":
        return "KILL: Unreachable Buyers", full_analysis

    # Check 3: Deal Size & LTV Analysis
    print(f"\n💵 Check 3: Deal Size Analysis...", flush=True)

    deal_prompt = f"""Calculate realistic deal size and LTV:

TARGET MARKET: {niche}
PROBLEM: {pain}

EXISTING SPENDING DATA:
{spend_result[:1000]}

Based on competitive pricing and customer segments, estimate:

1. **Annual Contract Value (ACV)**
   - What would {niche} pay for a solution to {pain}?
   - Base on: existing tool pricing, services costs, pain severity
   - Segment by company size (SMB vs Mid-market vs Enterprise)

2. **Lifetime Value (LTV)**
   - Estimated customer lifespan: [years]
   - Churn risk: [high/medium/low and why]
   - Expansion revenue potential: [upsells, cross-sells]

3. **Market TAM Calculation**
   - # of {niche} businesses: [from earlier research]
   - % likely to buy: [realistic %, not 100%]
   - Addressable market value: $[X]M

FORMAT YOUR RESPONSE:

## DEAL SIZE ESTIMATES
| Segment | # Businesses | ACV | LTV (3yr) |
|---------|-------------|-----|-----------|
| SMB | [X] | $X/yr | $X |
| Mid-Market | [X] | $X/yr | $X |
| Enterprise | [X] | $X/yr | $X |

## MARKET SIZE
- **Total TAM:** $[X]M annually
- **Serviceable TAM (realistic):** $[X]M (assuming X% adoption)
- **Year 1 Target:** $[X]K (realistic first year revenue)

## PROFITABILITY CHECK
- **Estimated CAC:** $[X] (based on similar SaaS)
- **LTV:CAC Ratio:** [X]:1
- **Healthy?** [Yes if >3:1, No if <3:1]

## VERDICT: [KILL or PASS]
- KILL if: ACV <$1,200/yr, TAM <$10M, LTV:CAC <2:1
- PASS if: Healthy deal sizes, large TAM, profitable unit economics

Require viable business model."""

    deal_result = call_openai(deal_prompt)
    deal_verdict = parse_verdict(deal_result)
    full_analysis += f"\n{'='*70}\nCHECK 3: DEAL SIZE ANALYSIS\n{'='*70}\n{deal_result}\n"

    print(f"   {deal_verdict}", flush=True)

    if deal_verdict == "KILL":
        return "KILL: Poor Unit Economics", full_analysis

    # All checks passed
    return "PASS: Budget Validated", full_analysis

def main():
    """Process ideas through Budget Validator"""
    print("\n🚀 STAGE 2: BUDGET VALIDATOR", flush=True)
    print("="*70, flush=True)
    print("💰 Proving businesses WILL PAY", flush=True)
    print("👔 Identifying decision makers", flush=True)
    print("💀 Expected pass rate: ~50% of Stage 1 survivors", flush=True)
    print("="*70, flush=True)

    growth_pass = sheet.worksheet("Stage 1: Growth Pass")
    budget_pass = sheet.worksheet("Stage 2: Budget Pass")

    all_rows = growth_pass.get_all_values()

    if len(all_rows) <= 1:
        print("\n❌ No ideas from Stage 1. Run: python stage1_growth_filter.py", flush=True)
        return

    processed = 0
    killed = 0
    passed = 0

    for i, row in enumerate(all_rows[1:], start=2):
        if len(row) < 3:
            continue

        row_num = row[0]
        niche = row[1]
        pain = row[2]

        result_status, analysis = budget_validator(row_num, niche, pain)

        processed += 1

        if "KILL" in result_status:
            killed += 1
            print(f"\n💀 {result_status}", flush=True)
            # Update status in growth_pass sheet
            growth_pass.update_cell(i, 4, result_status)
        else:
            # PASSED - Move to Stage 3
            budget_pass.append_row([
                row_num,
                niche,
                pain,
                "Ready for Deep Research",
                analysis[:500],
                datetime.now().strftime("%Y-%m-%d")
            ])
            passed += 1
            print(f"\n✅ PASSED Budget Validation!", flush=True)

            # Update status in growth_pass sheet
            growth_pass.update_cell(i, 4, "PASSED to Stage 3")

        print(f"\n📊 Progress: {processed} processed | {killed} killed | {passed} passed", flush=True)
        print(f"   Kill rate: {(killed/processed*100):.1f}% | Pass rate: {(passed/processed*100):.1f}%", flush=True)

    print(f"\n{'='*70}", flush=True)
    print(f"✅ Stage 2 Complete!", flush=True)
    print(f"   Processed: {processed}", flush=True)
    print(f"   Killed: {killed} ({(killed/processed*100):.1f}%)", flush=True)
    print(f"   Passed to Stage 3: {passed}", flush=True)
    print(f"\n➡️  Next: python stage3_deep_research.py", flush=True)
    print(f"{'='*70}\n", flush=True)

if __name__ == "__main__":
    main()
