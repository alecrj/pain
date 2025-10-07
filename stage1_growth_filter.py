#!/usr/bin/env python3
"""
STAGE 1: Growth Filter
Identifies HIGH-GROWTH industries with NO licensing/API restrictions
Filters out 80% of ideas immediately
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

# Industries EXCLUDED due to licensing/regulatory barriers
EXCLUDED_INDUSTRIES = [
    "healthcare", "medical", "hospital", "clinic", "doctor", "physician",
    "insurance", "health insurance", "life insurance",
    "banking", "finance", "financial services", "fintech", "payment processing",
    "legal", "law firm", "attorney", "lawyer",
    "real estate", "realty", "property sales", "realtor",
    "pharmacy", "pharmaceutical sales", "drug", "dental",
    "childcare", "daycare", "preschool", "education", "school", "university",
    "senior care", "nursing home", "assisted living",
    "counseling", "therapy", "mental health"
]

def check_industry_excluded(niche):
    """Check if industry is in excluded list"""
    niche_lower = niche.lower()
    for excluded in EXCLUDED_INDUSTRIES:
        if excluded in niche_lower:
            return True
    return False

def call_openai(prompt, max_tokens=3000):
    """Call OpenAI API"""
    time.sleep(1)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a business analyst specializing in high-growth industries. You find data-driven evidence of growth, funding, and market dynamics."},
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
    """Extract verdict from response"""
    if not text:
        return "KILL"

    text_upper = text.upper()

    if "VERDICT: KILL" in text_upper or "VERDICT:KILL" in text_upper:
        return "KILL"
    if "VERDICT: PASS" in text_upper or "VERDICT:PASS" in text_upper or "VERDICT: PROCEED" in text_upper:
        return "PASS"

    # Default to KILL
    return "KILL"

def growth_filter(row_num, niche, pain):
    """Stage 1: Growth & Viability Filter"""
    print(f"\n{'='*70}", flush=True)
    print(f"🔍 GROWTH FILTER #{row_num}: {niche}", flush=True)
    print(f"{'='*70}", flush=True)

    # Check 1: Industry Exclusions (licensing/regulatory)
    print(f"\n📋 Check 1: Industry Restrictions...", flush=True)
    if check_industry_excluded(niche):
        print(f"   ❌ KILL - Excluded industry (licensing/regulatory barriers)", flush=True)
        return "KILL: Excluded Industry", f"Industry '{niche}' requires licensing or has heavy regulatory barriers."
    print(f"   ✅ PASS - No licensing restrictions", flush=True)

    # Check 2: Growth Rate Analysis
    print(f"\n📈 Check 2: Growth Rate Analysis...", flush=True)

    growth_prompt = f"""Analyze the growth potential of this business segment:

TARGET MARKET: {niche}
PROBLEM CONTEXT: {pain}

RESEARCH REQUIREMENTS:
1. **Industry Growth Rate (Last 3 years)**
   - Use IBISWorld, Statista, industry reports
   - Must be >10% YoY growth
   - Cite specific sources with data

2. **Market Expansion Signals**
   - New companies entering the market?
   - Technology adoption increasing?
   - Industry consolidation or M&A activity?

3. **Future Outlook (Next 3 years)**
   - Accelerating or decelerating?
   - Key growth drivers?
   - Any headwinds?

FORMAT YOUR RESPONSE:

## GROWTH METRICS
- **Industry Growth Rate:** [X%] YoY (2021-2024) - [Source]
- **Market Size:** $[X]B → $[Y]B (2024-2027 projection) - [Source]
- **Trend:** [Accelerating/Stable/Declining]

## EXPANSION SIGNALS
1. [Signal with evidence]
2. [Signal with evidence]
3. [Signal with evidence]

## FUNDING/M&A ACTIVITY
- Recent notable deals: [List if any]
- Startup funding: [VC investment trends]
- Strategic acquisitions: [Incumbents buying startups?]

## VERDICT: [KILL or PASS]
- KILL if: <10% growth, declining, or no expansion signals
- PASS if: >10% growth + clear expansion signals + healthy outlook

Only PASS if this is a HIGH-GROWTH opportunity."""

    result = call_openai(growth_prompt, max_tokens=2000)
    verdict = parse_verdict(result)

    print(f"   {verdict}", flush=True)

    if verdict == "KILL":
        return "KILL: Low Growth", result

    # Check 3: API/Technical Feasibility
    print(f"\n🔧 Check 3: Technical Feasibility (API Requirements)...", flush=True)

    api_prompt = f"""Assess technical feasibility for building a solution:

TARGET MARKET: {niche}
PROBLEM: {pain}

RESEARCH:
1. **What data/APIs would this solution need?**
   - List specific APIs or data sources required
   - Check if they're PUBLIC or enterprise-only

2. **API Accessibility**
   - Public/free APIs available? (✅)
   - Restricted/enterprise APIs required? (❌)
   - Web scraping of public data possible? (✅)
   - No external data needed? (✅)

3. **Examples of Similar Tools**
   - What do existing solutions use?
   - Are those APIs accessible to new entrants?

CRITICAL: Can this be built WITHOUT:
- Enterprise-only APIs (Salesforce API, enterprise CRMs, etc.)
- Restricted industry APIs (MLS, medical records, insurance databases)
- Licensed data sources

FORMAT YOUR RESPONSE:

## DATA/API REQUIREMENTS
1. [Required data/API] - [Public/Restricted]
2. [Required data/API] - [Public/Restricted]

## ACCESSIBILITY ANALYSIS
- **Public APIs Available:** [Yes/No + list]
- **Alternative Data Sources:** [Web scraping, manual input, etc.]
- **Gatekeepers/Restrictions:** [Any barriers?]

## VERDICT: [KILL or PASS]
- KILL if: Requires restricted APIs, enterprise-only data, or licensed sources
- PASS if: Can be built with public APIs, web scraping, or no external data

Only PASS if technically feasible without gatekeepers."""

    api_result = call_openai(api_prompt, max_tokens=2000)
    api_verdict = parse_verdict(api_result)

    print(f"   {api_verdict}", flush=True)

    if api_verdict == "KILL":
        return "KILL: API Restrictions", result + "\n\n" + api_result

    # All checks passed
    return "PASS: Growth Filter", result + "\n\n" + api_result

def main():
    """Process ideas through Growth Filter"""
    print("\n🚀 STAGE 1: GROWTH FILTER", flush=True)
    print("="*70, flush=True)
    print("🎯 Identifying HIGH-GROWTH opportunities", flush=True)
    print("🚫 Filtering out regulated/restricted industries", flush=True)
    print("💀 Expected pass rate: ~20%", flush=True)
    print("="*70, flush=True)

    queue = sheet.worksheet("Ideas Queue")
    growth_pass = sheet.worksheet("Stage 1: Growth Pass")

    all_rows = queue.get_all_values()

    if len(all_rows) <= 1:
        print("\n❌ No ideas in queue. Run: python generate_ideas_v4.py", flush=True)
        return

    processed = 0
    killed = 0
    passed = 0

    for i, row in enumerate(all_rows[1:], start=2):
        if len(row) < 4:
            continue

        status = row[3] if len(row) > 3 else ""
        if status != "Pending":
            continue

        row_num = row[0]
        niche = row[1]
        pain = row[2]

        result_status, analysis = growth_filter(row_num, niche, pain)

        processed += 1

        # Update Ideas Queue
        queue.update_cell(i, 4, result_status)

        if "KILL" in result_status:
            killed += 1
            print(f"\n💀 {result_status}", flush=True)
        else:
            # PASSED - Move to Stage 2
            growth_pass.append_row([
                row_num,
                niche,
                pain,
                "Ready for Budget Filter",
                analysis[:500],
                datetime.now().strftime("%Y-%m-%d")
            ])
            passed += 1
            print(f"\n✅ PASSED Growth Filter!", flush=True)

        print(f"\n📊 Progress: {processed} processed | {killed} killed | {passed} passed", flush=True)
        print(f"   Kill rate: {(killed/processed*100):.1f}% | Pass rate: {(passed/processed*100):.1f}%", flush=True)

    print(f"\n{'='*70}", flush=True)
    print(f"✅ Stage 1 Complete!", flush=True)
    print(f"   Processed: {processed}", flush=True)
    print(f"   Killed: {killed} ({(killed/processed*100):.1f}%)", flush=True)
    print(f"   Passed to Stage 2: {passed}", flush=True)
    print(f"\n➡️  Next: python stage2_budget_validator.py", flush=True)
    print(f"{'='*70}\n", flush=True)

if __name__ == "__main__":
    main()
