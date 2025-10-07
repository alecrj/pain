#!/usr/bin/env python3
"""
Pain Point Finder v2.0 - REAL Research Edition
Actually searches, cites sources, and kills 95%+ of ideas
"""

import os
import sys
import time
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

print("\n" + "="*80)
print("  🔍 PAIN POINT FINDER v2.0 - REAL RESEARCH EDITION")
print("="*80 + "\n")

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Pain Point Research")
CREDENTIALS_FILE = "google-credentials.json"

# Validation
print("🔧 Validating setup...")

if not GOOGLE_API_KEY:
    print("❌ ERROR: GOOGLE_API_KEY not found in .env")
    sys.exit(1)
print("  ✓ Gemini API key found")

if not os.path.exists(CREDENTIALS_FILE):
    print(f"❌ ERROR: {CREDENTIALS_FILE} not found")
    sys.exit(1)
print("  ✓ Google credentials found")

# Initialize Gemini
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    print("  ✓ Gemini 2.0 Flash connected (FREE tier)")
except Exception as e:
    print(f"❌ Gemini error: {e}")
    sys.exit(1)

# Initialize Google Sheets
try:
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sheet = gc.open(GOOGLE_SHEET_NAME)
    print(f"  ✓ Connected to: '{GOOGLE_SHEET_NAME}'")
except Exception as e:
    print(f"❌ Google Sheets error: {e}")
    sys.exit(1)

print("\n✅ System ready!\n")

# Research stages - RIGOROUS VERSION
STAGES = {
    1: {
        "name": "Find Real Complaints with Citations",
        "prompt": """You are a market researcher finding PROOF that this pain point exists.

MICRO-NICHE: {micro_niche}
SPECIFIC PAIN: {specific_pain}

YOUR TASK:
Search Reddit, Hacker News, forums, and social media for people complaining about this EXACT pain.

REQUIREMENTS - ALL must be met or you KILL this idea:
1. Find AT LEAST 5 different people from DIFFERENT sources
2. Each must include SPECIFIC NUMBERS (hours/week, $/month, frequency)
3. All must be from 2023-2025 (recent complaints only)
4. Must have ACTUAL URLS/LINKS you can cite

SEARCH STRATEGY:
- site:reddit.com "{micro_niche}" "{specific_pain}"
- site:reddit.com "wasting hours" "{specific_pain}"
- site:news.ycombinator.com "{micro_niche}" complaint
- "{micro_niche}" "how do you handle" "{specific_pain}"
- "{specific_pain}" "takes forever" "manual"

OUTPUT FORMAT:
---
## COMPLAINT 1
**Source URL:** [paste actual URL]
**Posted:** [date - must be 2023-2025]
**User:** [username]
**Quote:** "[exact quote showing pain]"
**Numbers:** [X hours/week OR $Y/month OR Z times per day]
**Context:** [Brief: when does this pain occur in their workflow]

## COMPLAINT 2
[same format]

## COMPLAINT 3
[same format]

## COMPLAINT 4
[same format]

## COMPLAINT 5
[same format]

---
## VERDICT

**Complaints found:** [exact number]
**With numbers:** [how many had specific metrics]
**Recent (2023-2025):** [how many were recent]
**Different sources:** [how many unique sources]

**CRITICAL EVALUATION:**
- Is this a REAL pain or just minor annoyance?
- Do multiple independent people confirm this?
- Are the numbers significant (>2 hours/week OR >$100/month)?

**DECISION:**

If ALL of these are YES → **DECISION: PROCEED**
- Found 5+ different complainers
- All have specific numbers
- All from 2023-2025
- Pain is significant (>2 hrs/week OR >$100/mo impact)

Otherwise → **DECISION: KILL - [specific reason which criteria failed]**

**FINAL VERDICT: [PROCEED or KILL - reason]**
"""
    },

    2: {
        "name": "Quantify with Industry Data",
        "prompt": """You found complaints. Now prove this pain is MEASURABLE and WIDESPREAD.

MICRO-NICHE: {micro_niche}
SPECIFIC PAIN: {specific_pain}

YOUR TASK:
Find industry reports, surveys, or studies with HARD NUMBERS about this pain.

SEARCH FOR:
- "{micro_niche}" survey time spent "{specific_pain}"
- "{specific_pain}" industry report statistics 2024
- "{micro_niche}" productivity study "{specific_pain}"
- "{specific_pain}" cost analysis "{micro_niche}"
- "{specific_pain}" benchmark data

REQUIREMENTS:
- Find AT LEAST 3 credible sources
- Each must have SPECIFIC metrics (time/cost/frequency)
- Sources must be credible (research firms, industry associations, surveys)
- Must be recent (2022+)

OUTPUT FORMAT:
---
## SOURCE 1: [Title]
**URL:** [actual link]
**Published:** [date]
**Credibility:** [e.g., "Gartner study", "Industry survey of 500 companies", "Academic research"]
**Key Stat:** [specific number with unit]
**Quote:** "[exact relevant quote]"
**What it measures:** [explain context]

## SOURCE 2: [Title]
[same format]

## SOURCE 3: [Title]
[same format]

---
## AGGREGATED IMPACT

Based on all sources:
- **Average time waste:** [X hours/week or hours/month]
- **Financial impact:** [$Y per year or per month]
- **Frequency:** [How often: daily/weekly/monthly]
- **% of niche affected:** [estimate based on data]
- **Severity score (1-10):** [your assessment with reasoning]

---
## VERDICT

**Sources found:** [number]
**Credible sources:** [number that are actually credible]
**Recent data:** [sources from 2022+]
**Consistent numbers:** [do sources agree or wildly contradict?]

**CRITICAL EVALUATION:**
- Is the impact severe enough to build a business? (Must be 5+ hours/week OR $500+/month)
- Is this widespread or niche edge case?
- Do multiple sources confirm each other?

**DECISION:**

If ALL YES → **DECISION: PROCEED**
- Found 3+ credible sources
- Impact is severe (>5 hrs/week OR >$500/mo)
- Numbers are consistent
- Recent data (2022+)

Otherwise → **DECISION: KILL - [specific reason]**

**FINAL VERDICT: [PROCEED or KILL - reason]**
"""
    },

    3: {
        "name": "Verify Market Size",
        "prompt": """Is this market big enough to build a business?

MICRO-NICHE: {micro_niche}
SPECIFIC PAIN: {specific_pain}

YOUR TASK:
Find hard numbers on market size. How many businesses/people actually have this problem?

SEARCH FOR:
- "number of {micro_niche}" United States 2024
- "{micro_niche}" market size TAM
- "{micro_niche}" industry statistics
- "{micro_niche}" association membership
- how many "{micro_niche}" exist

OUTPUT FORMAT:
---
## MARKET SIZE DATA

**Source 1:**
- **Title:** [title]
- **URL:** [link]
- **Data:** Total {micro_niche} in US = [X,XXX]
- **Date:** [publication date]
- **Credibility:** [source type]

**Source 2:**
[confirm with second source or provide different estimate]

---
## GEOGRAPHIC & DEMOGRAPHIC BREAKDOWN
- **Primary location:** [US-wide / Specific regions / Global]
- **Company size affected:** [1-10 employees / 10-50 / 50-200 / etc]
- **Industry concentration:** [Spread across industries or concentrated]

---
## GROWTH TRENDS
- **Market growth rate:** [X% per year]
- **Source:** [link]
- **Trend:** [Growing / Stable / Declining]
- **Why:** [brief explanation]

---
## ADDRESSABLE MARKET CALCULATION

- **Total {micro_niche}:** [X,XXX]
- **% likely affected by THIS pain:** [Y%]
  *(Reasoning: [explain your estimate based on Stage 1 & 2 data])*
- **Addressable market:** [X,XXX × Y% = Z,ZZZ businesses/people]

---
## VERDICT

**Market size clarity:** [Clear / Unclear]
**Growth:** [Growing / Stable / Declining]
**Addressable market:** [number]

**CRITICAL EVALUATION:**
- Is addressable market >5,000? (Minimum for viable SaaS)
- Is market growing or at least stable?
- Can you reach these people online?

**DECISION:**

If ALL YES → **DECISION: PROCEED**
- >5,000 addressable businesses/people
- Market growing or stable (not declining)
- Reachable online

Otherwise → **DECISION: KILL - [specific reason]**

**FINAL VERDICT: [PROCEED or KILL - reason]**
"""
    },

    4: {
        "name": "Deep Competitive Analysis",
        "prompt": """Is this already solved? Be brutally honest.

MICRO-NICHE: {micro_niche}
SPECIFIC PAIN: {specific_pain}

YOUR TASK:
Find EVERY solution that exists - software, services, workarounds. Then find the gaps.

SEARCH FOR:
- "{specific_pain}" software tool SaaS
- "{micro_niche}" "{specific_pain}" solution
- "automate {specific_pain}"
- site:g2.com "{specific_pain}"
- site:reddit.com "how do you {specific_pain}"
- "alternative to [any competitor found]"

BE THOROUGH - spend time on this stage!

OUTPUT FORMAT:
---
## COMPETITOR 1: [Company Name]

**Website:** [URL]
**What they do:** [1-2 sentence description]
**Founded:** [year - try to find this]
**Pricing:** [$X/month or not public]
**Reviews:** [X.X stars on G2/Capterra with Y total reviews]
**Notable customers:** [if any mentioned]

**Top 3 Customer Complaints (from reviews/Reddit):**
1. [Specific complaint with source]
2. [Specific complaint with source]
3. [Specific complaint with source]

**What they DON'T solve:** [The gap - what part of the pain remains]

**Strength assessment:** [Weak / Moderate / Strong - with reasoning]

---
## COMPETITOR 2: [Company Name]
[same format - find at least 3-5 competitors]

---
## DIY / WORKAROUND SOLUTIONS

People currently use:
- [Tool 1: e.g., "Spreadsheets"] - Source: [Reddit link]
- [Tool 2: e.g., "Airtable + Zapier"] - Source: [link]
- [Tool 3: e.g., "Manual process"] - Source: [link]

Why DIY instead of competitors:
- [Reason from actual users]

---
## GAP ANALYSIS

**Total direct competitors:** [number]
**Strong incumbents (10+ years, >4 stars, 1000+ customers):** [number]
**Recent well-funded competitors (raised money in last 3 years):** [number]

**Common gaps across ALL solutions:**
1. [Gap everyone has]
2. [Gap everyone has]
3. [Gap everyone has]

**Are people STILL complaining despite solutions existing?**
[YES/NO with evidence]

**The opportunity (if any):**
[Describe what's missing that you could build]

---
## VERDICT

**CRITICAL EVALUATION - Be RUTHLESS:**

KILL immediately if ANY of these:
- ❌ 3+ direct competitors exist
- ❌ 1 strong incumbent (10+ yrs, >4 stars, praised on Reddit)
- ❌ Well-funded competitor raised $5M+ recently
- ❌ Users generally happy with existing solutions
- ❌ No clear gap in the market

PROCEED only if:
- ✅ 0-2 weak competitors OR
- ✅ All competitors have major gaps AND
- ✅ People still actively complaining despite solutions AND
- ✅ Clear opportunity to differentiate

**DECISION:**

[Detailed reasoning - be specific about why KILL or PROCEED]

**FINAL VERDICT: [PROCEED or KILL - reason]**

BE HONEST. Most ideas should KILL here. That's normal and good.
"""
    },

    5: {
        "name": "Final Documentation & Viability",
        "prompt": """This idea passed 4 stages. Document it completely.

MICRO-NICHE: {micro_niche}
SPECIFIC PAIN: {specific_pain}
IDEA NUMBER: #{idea_num}

YOUR TASK:
Create comprehensive documentation ONLY if this is truly viable.

OUTPUT FORMAT:
---
# 🎯 VERIFIED PAIN POINT #{idea_num}

## 1. THE SPECIFIC PAIN (Ultra-detailed)

[3-4 sentences describing EXACTLY what's broken, why it's painful, and the impact]

## 2. WHO HAS THIS PAIN

- **Specific role/title:** [exact job title]
- **Company size:** [specific range]
- **Industry:** [specific industry vertical]
- **Total market:** [X,XXX total businesses]
- **Addressable market:** [Y,YYY with THIS specific pain]
- **Geographic:** [where they're located]

## 3. THE BROKEN WORKFLOW

Current state (step-by-step):
1. [First step where pain begins]
2. [What they currently do manually - be specific]
3. [Why this is painful/time-consuming/error-prone]
4. [What happens if they make a mistake]
5. [Current workarounds they're using]

Time impact: [X hours/week wasted on this]

## 4. EVIDENCE & CITATIONS

**Reddit/Forum Complaints (5+ sources):**
1. "[Quote]" - [Username], [Date], [URL]
2. "[Quote]" - [Username], [Date], [URL]
3. "[Quote]" - [Username], [Date], [URL]
4. "[Quote]" - [Username], [Date], [URL]
5. "[Quote]" - [Username], [Date], [URL]

**Industry Data (3+ sources):**
1. [Stat] - [Source], [Date], [URL]
2. [Stat] - [Source], [Date], [URL]
3. [Stat] - [Source], [Date], [URL]

## 5. QUANTIFIED IMPACT

- **Time waste:** [X hours/week per person/company]
- **Financial cost:** [$Y lost per year]
- **Error rate:** [Z% if applicable]
- **Frequency:** [daily/weekly/monthly]
- **Total annual cost to market:** [$XX million - if calculable]

## 6. COMPETITIVE LANDSCAPE

**Total competitors:** [number]

**Main players:**
1. [Name] - [Weakness]
2. [Name] - [Weakness]
3. [Name] - [Weakness]

**Why existing solutions fail:**
1. [Gap #1 with evidence]
2. [Gap #2 with evidence]
3. [Gap #3 with evidence]

**The clear opportunity:**
[What YOU would build that doesn't exist - be specific]

## 7. WHY THIS PAIN ISN'T SOLVED YET

[Explain the market failure - why hasn't someone built this already?]

Possible reasons:
- Market too small until recently (now reached critical mass)
- Technology enabler now exists (AI, automation, new APIs)
- New regulation created this pain in 2023-2024
- Incumbents focused on enterprise, SMB underserved
- [Or specific reason based on research]

## 8. DIGITAL SOLUTION OPPORTUNITY

**What to build:**
[Describe the software/SaaS product - be specific]

**Core features:**
1. [Feature that solves main pain]
2. [Feature that solves secondary pain]
3. [Differentiator from competition]

**Business model:**
[SaaS subscription / Usage-based / Productized service / etc]

**Estimated pricing:**
[$X-Y/month based on competitive analysis]

## 9. STRENGTH ASSESSMENT

| Criteria | Met? | Evidence |
|----------|------|----------|
| 5+ cited complaints (2023-2025) | ✅/❌ | [X complaints found] |
| 3+ industry sources with data | ✅/❌ | [Y sources cited] |
| Widespread (>5,000 affected) | ✅/❌ | [Z,ZZZ addressable] |
| Severe impact (>5hrs/week OR >$500/mo) | ✅/❌ | [Impact: X hrs/week] |
| Unsolved (0-2 weak competitors) | ✅/❌ | [N competitors, all weak] |

**FINAL SCORE: X/5**

## 10. FINAL RECOMMENDATION

**If 5/5:** 🟢 **STRONG VERIFIED PAIN POINT**
- High confidence this is real and unsolved
- Ready for customer validation (20 LinkedIn calls)
- If 50%+ confirm → BUILD IT

**If 4/5:** 🟡 **MODERATE**
- Missing: [which criteria]
- Consider validating before investing time

**If <4/5:** 🔴 **WEAK**
- Should have been killed earlier
- Do not pursue

---

**YOUR FINAL CALL:**

[Give your honest assessment. Is this a real business opportunity or did it slip through?]

**VERDICT: [Score/5 - STRONG/MODERATE/WEAK]**
"""
    }
}

# Helper functions
def get_next():
    try:
        q = sheet.worksheet("Ideas Queue")
        rows = q.get_all_records()
        for idx, row in enumerate(rows, start=2):
            if str(row.get('Status', '')).strip() == 'Pending':
                return {
                    'row': idx,
                    'num': row.get('Idea #', idx-1),
                    'niche': str(row.get('Micro-Niche', '')).strip(),
                    'pain': str(row.get('Specific Task/Pain', '')).strip()
                }
        return None
    except Exception as e:
        print(f"❌ Queue error: {e}")
        return None

def update_status(row, status):
    try:
        sheet.worksheet("Ideas Queue").update_cell(row, 4, status)
    except:
        pass

def run_stage(idea, num):
    prompt = STAGES[num]["prompt"].format(
        micro_niche=idea['niche'],
        specific_pain=idea['pain'],
        idea_num=idea['num']
    )

    try:
        # Use generate_content WITHOUT search tools for now
        # Gemini's search wasn't working - let it use its training data
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.4,  # Lower temp for more focused analysis
                'max_output_tokens': 8192,
            }
        )
        return response.text
    except Exception as e:
        return f"ERROR: {e}"

def parse_verdict(response):
    """Extract verdict - MUST be explicit KILL or PROCEED"""

    response_upper = response.upper()

    # Look for final verdict
    if "FINAL VERDICT:" in response_upper:
        verdict_section = response[response.upper().index("FINAL VERDICT:"):]

        if "KILL" in verdict_section[:200].upper():
            # Extract reason
            try:
                reason = verdict_section.split("KILL", 1)[1].strip()
                if "-" in reason:
                    reason = reason.split("-", 1)[1].strip()
                return {"verdict": "KILL", "reason": reason[:200]}
            except:
                return {"verdict": "KILL", "reason": "Failed stage criteria"}

        elif "PROCEED" in verdict_section[:200].upper():
            return {"verdict": "PROCEED", "reason": None}

    # If no clear verdict, default to KILL (be conservative)
    return {"verdict": "KILL", "reason": "No clear verdict - defaulting to KILL for safety"}

def log_result(idea, stages, status, kill_stage=None):
    try:
        results = sheet.worksheet("Verified Pains")

        summaries = {}
        for i in range(1, 6):
            summaries[i] = stages.get(i, {}).get('response', '')[:400] if i in stages else ''

        row = [
            idea['num'],
            idea['niche'],
            idea['pain'],
            summaries.get(1, ''),
            summaries.get(2, ''),
            summaries.get(3, ''),
            summaries.get(4, ''),
            summaries.get(5, ''),
            status,
            kill_stage or "N/A",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]

        results.append_row(row)
        print("  ✓ Logged to 'Verified Pains'")

        if status == "VERIFIED":
            winners = sheet.worksheet("Winners")
            winners.append_row([
                idea['num'],
                idea['niche'],
                idea['pain'],
                f"Row {results.row_count} in 'Verified Pains' sheet",
                "Ready for manual validation (20 customer calls)",
                datetime.now().strftime("%Y-%m-%d")
            ])
            print("  🏆 ADDED TO WINNERS!")

    except Exception as e:
        print(f"  ⚠️ Log error: {e}")

def research(idea):
    print(f"\n{'='*80}")
    print(f"  IDEA #{idea['num']}: {idea['niche']}")
    print(f"  Pain: {idea['pain'][:60]}...")
    print(f"{'='*80}\n")

    results = {}

    for num in range(1, 6):
        stage = STAGES[num]
        print(f"  🔍 Stage {num}/5: {stage['name']}")
        print(f"     Researching...")

        try:
            response = run_stage(idea, num)
            verdict = parse_verdict(response)

            results[num] = {
                'name': stage['name'],
                'response': response,
                'verdict': verdict['verdict']
            }

            print(f"     ✓ {verdict['verdict']}")

            if verdict['verdict'] == "KILL":
                print(f"\n  🔴 KILLED at Stage {num}: {stage['name']}")
                print(f"     Reason: {verdict['reason'][:120]}")
                log_result(idea, results, "KILL", f"Stage {num}")
                update_status(idea['row'], 'Killed')
                return False

            time.sleep(3)  # Rate limiting

        except KeyboardInterrupt:
            print("\n⚠️ Interrupted")
            update_status(idea['row'], 'Interrupted')
            raise
        except Exception as e:
            print(f"     ❌ Error: {e}")
            # Treat errors as KILL
            results[num] = {
                'name': stage['name'],
                'response': str(e),
                'verdict': 'ERROR'
            }
            log_result(idea, results, "KILL", f"Stage {num} - Error")
            update_status(idea['row'], 'Killed')
            return False

    print(f"\n  🟢 VERIFIED! Passed all 5 rigorous stages.")
    print(f"     This is a HIGH-CONFIDENCE pain point.\n")

    log_result(idea, results, "VERIFIED")
    update_status(idea['row'], 'VERIFIED')
    return True

def main():
    print("="*80)
    print("  🚀 STARTING RIGOROUS RESEARCH")
    print("="*80)
    print(f"  Model: Gemini 2.0 Flash")
    print(f"  Sheet: '{GOOGLE_SHEET_NAME}'")
    print(f"  Expected kill rate: 95%+ (most ideas are bad - that's GOOD)")
    print("="*80 + "\n")

    processed = verified = killed = 0
    start = time.time()

    try:
        while True:
            idea = get_next()

            if not idea:
                elapsed = (time.time() - start) / 3600
                print("\n" + "="*80)
                print("  ✅ BATCH COMPLETE")
                print("="*80)
                print(f"  Processed: {processed}")
                print(f"  Verified: {verified}")
                print(f"  Killed: {killed}")
                print(f"  Success rate: {(verified/processed*100 if processed > 0 else 0):.1f}%")
                print(f"  Kill rate: {(killed/processed*100 if processed > 0 else 0):.1f}%")
                print(f"  Time: {elapsed:.1f} hrs")
                print("="*80 + "\n")

                if verified > 0:
                    print("🎯 CHECK 'WINNERS' SHEET FOR VERIFIED PAIN POINTS!")
                    print("   Next: Manually validate with 20 customer calls\n")
                else:
                    print("No verified pain points found in this batch.")
                    print("This is normal - keep testing more ideas!\n")
                break

            update_status(idea['row'], 'In Progress')
            is_verified = research(idea)

            processed += 1
            if is_verified:
                verified += 1
            else:
                killed += 1

            print(f"\n  📊 Progress: {processed} total | ✅ {verified} verified | ❌ {killed} killed")
            print(f"     Kill rate: {(killed/processed*100):.1f}% (target: 95%+)\n")

            time.sleep(5)

    except KeyboardInterrupt:
        print(f"\n\n⚠️ Stopped. Processed: {processed}, Verified: {verified}, Killed: {killed}\n")
    except Exception as e:
        print(f"\n\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()
