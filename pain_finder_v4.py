#!/usr/bin/env python3
"""
Pain Point Finder v4.0 - OpenAI Edition
Rigorous 5-stage validation with better research
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

# Rate limiting: 1 second between API calls
RATE_LIMIT_DELAY = 1.0

def wait_for_rate_limit():
    """Wait to avoid hitting rate limits"""
    time.sleep(RATE_LIMIT_DELAY)

def call_openai(prompt, max_retries=3):
    """Call OpenAI API with retry logic"""
    for attempt in range(max_retries):
        try:
            wait_for_rate_limit()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a rigorous market researcher. You KILL ideas unless you find strong evidence. Default to KILL, not PROCEED."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10
                    print(f"   ⏱️  Rate limit hit, waiting {wait_time}s...", flush=True)
                    time.sleep(wait_time)
                    continue
            raise e
    raise Exception("Max retries exceeded")

def parse_verdict(text):
    """Extract VERDICT from response"""
    text_upper = text.upper()

    # Look for explicit verdict
    if "VERDICT: KILL" in text_upper or "VERDICT:KILL" in text_upper:
        return "KILL"
    if "VERDICT: PROCEED" in text_upper or "VERDICT:PROCEED" in text_upper:
        return "PROCEED"

    # Check for kill signals
    kill_signals = [
        "NOT ENOUGH EVIDENCE",
        "INSUFFICIENT COMPLAINTS",
        "TOO VAGUE",
        "NO CLEAR PATTERN",
        "CANNOT VERIFY",
        "FAILED TO FIND",
        "DOES NOT MEET"
    ]

    for signal in kill_signals:
        if signal in text_upper:
            return "KILL"

    # Default to KILL unless explicitly says proceed
    if "PROCEED" in text_upper:
        return "PROCEED"

    return "KILL"

def stage1_find_complaints(niche, pain):
    """Stage 1: Find 5+ specific complaints with citations"""
    print(f"\n🔍 STAGE 1: Finding complaints...", flush=True)

    prompt = f"""Research this business pain point:
NICHE: {niche}
PAIN: {pain}

Find 5+ SPECIFIC complaints from real business owners experiencing this exact problem.

CRITICAL REQUIREMENTS:
- Must be from REAL business owners (not consultants or vendors)
- Must describe the SAME core problem
- Must include frustration/impact statements
- Must provide CITED SOURCES (Reddit URLs, forum links, LinkedIn posts, industry reports)

Search for:
- "{niche} {pain}" discussions
- Industry forums, Reddit communities, LinkedIn groups
- Trade association reports
- Review sites (G2, Capterra) mentioning this problem

FORMAT YOUR RESPONSE:

COMPLAINTS FOUND:
1. [Quote from business owner] - [Source URL]
2. [Quote from business owner] - [Source URL]
...

PATTERN ANALYSIS:
[What's the common thread? What makes this painful?]

VERDICT: [KILL or PROCEED]
- KILL if: <5 complaints, vague problems, no clear pattern
- PROCEED if: 5+ specific complaints from real business owners with citations

Only PROCEED if you found 5+ complaints with real citations."""

    try:
        result = call_openai(prompt)
        verdict = parse_verdict(result)

        print(f"   {verdict}", flush=True)
        return verdict, result
    except Exception as e:
        print(f"   ERROR: {e}", flush=True)
        return "KILL", f"Error: {e}"

def stage2_quantify(niche, pain, stage1_data):
    """Stage 2: Quantify the problem with industry data"""
    print(f"\n📊 STAGE 2: Quantifying problem...", flush=True)

    prompt = f"""This pain point passed Stage 1:
NICHE: {niche}
PAIN: {pain}

STAGE 1 FINDINGS:
{stage1_data[:1500]}

Find quantitative data proving this is a significant problem:

REQUIRED DATA:
1. Industry statistics on time/money wasted
2. Survey data showing % of businesses affected
3. Market research on this specific workflow problem
4. Cost estimates for manual processes

Search for:
- Industry reports (McKinsey, Gartner, IBISWorld)
- Trade association surveys
- Academic studies
- Government data (BLS, Census)

FORMAT YOUR RESPONSE:

QUANTITATIVE DATA:
1. [Stat with citation]
2. [Stat with citation]
...

IMPACT ANALYSIS:
[How much time/money/productivity is lost?]

VERDICT: [KILL or PROCEED]
- KILL if: No hard data, vague estimates, cannot quantify
- PROCEED if: 3+ industry sources with specific numbers/percentages

Only PROCEED if you found hard data with citations."""

    try:
        result = call_openai(prompt)
        verdict = parse_verdict(result)

        print(f"   {verdict}", flush=True)
        return verdict, result
    except Exception as e:
        print(f"   ERROR: {e}", flush=True)
        return "KILL", f"Error: {e}"

def stage3_market_size(niche, pain):
    """Stage 3: Verify market size >5,000 businesses"""
    print(f"\n🎯 STAGE 3: Market sizing...", flush=True)

    prompt = f"""Estimate the addressable market for:
NICHE: {niche}
PAIN: {pain}

Calculate total # of businesses that:
1. Fit this niche description
2. Experience this specific problem
3. Could afford a software solution ($50-500/month)

RESEARCH:
- Industry databases (IBISWorld, Statista)
- Trade associations (member counts)
- Government data (BLS, Census Bureau)
- LinkedIn company counts by industry

FORMAT YOUR RESPONSE:

MARKET SIZE CALCULATION:
[Show your work - total businesses in niche, % affected, etc.]

TAM (Total Addressable Market): [NUMBER] businesses

SOURCES:
1. [Citation]
2. [Citation]

VERDICT: [KILL or PROCEED]
- KILL if: <5,000 businesses, cannot verify size
- PROCEED if: 5,000+ businesses with cited sources

Only PROCEED if TAM >5,000 with citations."""

    try:
        result = call_openai(prompt)
        verdict = parse_verdict(result)

        print(f"   {verdict}", flush=True)
        return verdict, result
    except Exception as e:
        print(f"   ERROR: {e}", flush=True)
        return "KILL", f"Error: {e}"

def stage4_competition(niche, pain):
    """Stage 4: Competitive analysis (0-2 weak competitors)"""
    print(f"\n⚔️  STAGE 4: Competitive analysis...", flush=True)

    prompt = f"""Find existing solutions for:
NICHE: {niche}
PAIN: {pain}

Research:
1. Software products specifically targeting this niche + pain
2. General tools being adapted for this use case
3. Review sites (G2, Capterra, Software Advice)
4. Competitor websites and marketing

CRITICAL: Distinguish between:
- STRONG competitor: Built specifically for this niche, good reviews, active marketing
- WEAK competitor: Generic tool, poor reviews, outdated, not niche-specific

FORMAT YOUR RESPONSE:

COMPETITORS FOUND:
1. [Name] - [URL] - [Strong/Weak and why]
2. [Name] - [URL] - [Strong/Weak and why]

MARKET GAP ANALYSIS:
[What are they missing? Why is this still a pain point?]

VERDICT: [KILL or PROCEED]
- KILL if: 3+ strong competitors already solving this
- PROCEED if: 0-2 weak competitors OR clear market gap

Only PROCEED if there's a real opportunity."""

    try:
        result = call_openai(prompt)
        verdict = parse_verdict(result)

        print(f"   {verdict}", flush=True)
        return verdict, result
    except Exception as e:
        print(f"   ERROR: {e}", flush=True)
        return "KILL", f"Error: {e}"

def stage5_final_verdict(niche, pain, all_data):
    """Stage 5: Final documentation and verdict"""
    print(f"\n✅ STAGE 5: Final verdict...", flush=True)

    prompt = f"""Final assessment for:
NICHE: {niche}
PAIN: {pain}

ALL RESEARCH:
{all_data[:2000]}

Summarize the complete opportunity:

FORMAT YOUR RESPONSE:

VERIFIED PAIN POINT:
[One sentence description]

EVIDENCE SUMMARY:
- Complaints: [X sources cited]
- Market data: [Key stats]
- Market size: [X businesses]
- Competition: [X weak competitors]

BUSINESS OPPORTUNITY:
[Why this is a real, solvable problem]

NEXT STEPS:
[What to validate next]

VERDICT: [KILL or PROCEED]
- KILL if: Any critical gaps in evidence
- PROCEED if: All 4 stages passed with strong evidence

Be RUTHLESS - only PROCEED if this is clearly a winner."""

    try:
        result = call_openai(prompt)
        verdict = parse_verdict(result)

        print(f"   {verdict}", flush=True)
        return verdict, result
    except Exception as e:
        print(f"   ERROR: {e}", flush=True)
        return "KILL", f"Error: {e}"

def research_pain_point(row_num, niche, pain):
    """Run full 5-stage research on one pain point"""
    print(f"\n{'='*60}", flush=True)
    print(f"🎯 Researching #{row_num}: {niche}", flush=True)
    print(f"   Pain: {pain[:60]}...", flush=True)
    print(f"{'='*60}", flush=True)

    all_data = ""

    # Stage 1: Find complaints
    verdict1, data1 = stage1_find_complaints(niche, pain)
    all_data += f"\n\nSTAGE 1:\n{data1}"
    if verdict1 == "KILL":
        return "KILLED: Stage 1 (complaints)", all_data

    # Stage 2: Quantify
    verdict2, data2 = stage2_quantify(niche, pain, data1)
    all_data += f"\n\nSTAGE 2:\n{data2}"
    if verdict2 == "KILL":
        return "KILLED: Stage 2 (quantify)", all_data

    # Stage 3: Market size
    verdict3, data3 = stage3_market_size(niche, pain)
    all_data += f"\n\nSTAGE 3:\n{data3}"
    if verdict3 == "KILL":
        return "KILLED: Stage 3 (market size)", all_data

    # Stage 4: Competition
    verdict4, data4 = stage4_competition(niche, pain)
    all_data += f"\n\nSTAGE 4:\n{data4}"
    if verdict4 == "KILL":
        return "KILLED: Stage 4 (competition)", all_data

    # Stage 5: Final verdict
    verdict5, data5 = stage5_final_verdict(niche, pain, all_data)
    all_data += f"\n\nSTAGE 5:\n{data5}"
    if verdict5 == "KILL":
        return "KILLED: Stage 5 (final)", all_data

    return "✅ VERIFIED WINNER!", all_data

def main():
    """Process pending pain points from Ideas Queue"""
    print("\n🚀 Pain Point Finder v4.0 (OpenAI Edition)", flush=True)
    print("="*60, flush=True)
    print("⏱️  Rate limited: 1s between API calls", flush=True)
    print("🎯 Targeting: REAL businesses (any industry)", flush=True)
    print("💀 Expected kill rate: 95%+", flush=True)
    print("="*60, flush=True)

    queue = sheet.worksheet("Ideas Queue")
    verified = sheet.worksheet("Verified Pains")
    winners = sheet.worksheet("Winners")

    all_rows = queue.get_all_values()

    if len(all_rows) <= 1:
        print("\n❌ No ideas in queue. Run: python generate_ideas_v4.py", flush=True)
        return

    processed = 0
    killed = 0
    verified_count = 0
    winners_count = 0

    for i, row in enumerate(all_rows[1:], start=2):
        if len(row) < 4:
            continue

        status = row[3] if len(row) > 3 else ""
        if status != "Pending":
            continue

        row_num = row[0]
        niche = row[1]
        pain = row[2]

        result_status, research_data = research_pain_point(row_num, niche, pain)

        processed += 1

        # Update Ideas Queue status
        queue.update_cell(i, 4, result_status)

        if "KILLED" in result_status:
            killed += 1
            print(f"\n💀 KILLED: {result_status}", flush=True)

        elif "VERIFIED" in result_status:
            # Add to Verified Pains
            verified.append_row([
                row_num,
                niche,
                pain,
                research_data[:500],
                datetime.now().strftime("%Y-%m-%d")
            ])
            verified_count += 1
            print(f"\n✅ VERIFIED!", flush=True)

            # Check if it's a winner (passed all 5 stages)
            if "Stage 5" in research_data and "PROCEED" in research_data:
                winners.append_row([
                    row_num,
                    niche,
                    pain,
                    research_data[:1000],
                    datetime.now().strftime("%Y-%m-%d")
                ])
                winners_count += 1
                print(f"\n🏆 WINNER FOUND!", flush=True)

        print(f"\n📊 Progress: {processed} processed | {killed} killed | {verified_count} verified | {winners_count} winners", flush=True)
        print(f"   Kill rate: {(killed/processed*100):.1f}%", flush=True)

    print(f"\n{'='*60}", flush=True)
    print(f"✅ Research complete!", flush=True)
    print(f"   Processed: {processed}", flush=True)
    print(f"   Killed: {killed} ({(killed/processed*100):.1f}%)", flush=True)
    print(f"   Verified: {verified_count}", flush=True)
    print(f"   Winners: {winners_count}", flush=True)
    print(f"{'='*60}\n", flush=True)

if __name__ == "__main__":
    main()
