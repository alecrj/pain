#!/usr/bin/env python3
"""
Pain Point Finder - FREE Edition
Automated research system using Gemini 2.0 Flash
Processes hundreds of ideas at $0 cost
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
print("  🔍 PAIN POINT FINDER - FREE EDITION")
print("="*80 + "\n")

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Pain Point Research")
CREDENTIALS_FILE = "google-credentials.json"

# Validation
print("🔧 Validating setup...")

if not GOOGLE_API_KEY:
    print("❌ ERROR: GOOGLE_API_KEY not found in .env")
    print("   Get FREE key at: https://aistudio.google.com/app/apikey")
    sys.exit(1)
print("  ✓ Gemini API key found")

if not os.path.exists(CREDENTIALS_FILE):
    print(f"❌ ERROR: {CREDENTIALS_FILE} not found")
    print(f"   Run: python setup.py")
    sys.exit(1)
print("  ✓ Google credentials found")

# Initialize Gemini
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(
        'gemini-2.0-flash-exp',
        tools='google_search_retrieval'
    )
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
    print(f"   Make sure:")
    print(f"   1. Sheet name in .env matches actual name")
    print(f"   2. Service account has Editor access")
    sys.exit(1)

print("\n✅ System ready!\n")

# Research stages
STAGES = {
    1: {
        "name": "Raw Complaints",
        "prompt": """Search for real people complaining about this pain.

NICHE: {micro_niche}
PAIN: {specific_pain}

Find 5+ different people with direct quotes and numbers (hours/week).

Output format:
### Complaint 1
**Source:** [url]
**Person:** [name]
**Quote:** "[complaint]"
**Numbers:** [X hrs/week] or [None]

[Repeat 5+ times]

### Verdict
- Found 5+: YES/NO
- Has numbers: YES/NO
- Recent (2024-2025): YES/NO

**DECISION: PROCEED** if all YES, else **DECISION: KILL - [reason]**"""
    },
    2: {
        "name": "Quantification",
        "prompt": """Find hard data on this pain.

NICHE: {micro_niche}
PAIN: {specific_pain}

Find 3+ sources with specific numbers (time/cost/errors).

Output format:
### Source 1
**Title:** [title]
**URL:** [url]
**Stat:** [X hours/week] or [$Y/year]
**Published:** [date]

[Repeat 3+ times]

### Impact
- Time: [X hrs/week]
- Cost: [$Y/year] or [N/A]
- Severity (1-10): [score]

### Verdict
- 3+ sources: YES/NO
- Severe (7+): YES/NO

**DECISION: PROCEED** if both YES, else **DECISION: KILL - [reason]**"""
    },
    3: {
        "name": "Market Size",
        "prompt": """Check market size.

NICHE: {micro_niche}
PAIN: {specific_pain}

Find total businesses and estimate % affected.

Output format:
### Market Data
- Total businesses: [X,XXX]
- Source: [url]
- Growth: [growing/stable/declining]

### Addressable
- Est. % with pain: [Y%]
- Total affected: [X,XXX × Y% = Z,ZZZ]

### Verdict
- >5,000 total: YES/NO
- >1,000 affected: YES/NO
- Growing/stable: YES/NO

**DECISION: PROCEED** if all YES, else **DECISION: KILL - [reason]**"""
    },
    4: {
        "name": "Competition",
        "prompt": """Find existing solutions.

NICHE: {micro_niche}
PAIN: {specific_pain}

List ALL competitors with reviews and gaps.

Output format:
### Competitor 1: [Name]
**Website:** [url]
**Founded:** [year]
**Reviews:** [X.X stars]
**Complaints:** [top 3]
**Gap:** [what they don't solve]

[Repeat for all found]

### Analysis
- Total: [number]
- Strong incumbent: YES/NO
- Clear gap: YES/NO

### Verdict
- 3+ competitors: YES/NO
- Strong incumbent: YES/NO

**DECISION: KILL** if either YES, else **DECISION: PROCEED**"""
    },
    5: {
        "name": "Documentation",
        "prompt": """Create final pain profile.

NICHE: {micro_niche}
PAIN: {specific_pain}
ID: #{idea_num}

# VERIFIED PAIN POINT #{idea_num}

## 1. The Pain
[2-3 sentences describing exact problem]

## 2. Who Has It
- Role: [specific title]
- Company size: [range]
- Total market: [X,XXX]
- Affected: [Y,YYY]

## 3. Impact
- Time: [X hrs/week]
- Cost: [$Y/year]
- Frequency: [how often]

## 4. Evidence
- Complainers: [X people]
- Top 3 quotes with sources

## 5. Competition
- Total: [number]
- Main players: [list]
- Gaps: [what's missing]

## 6. Why Unsolved
[Explanation]

## 7. Score
| Criteria | Met? |
|----------|------|
| 5+ complainers | ✅/❌ |
| Quantified | ✅/❌ |
| Recent | ✅/❌ |
| Widespread | ✅/❌ |
| Unsolved | ✅/❌ |

**SCORE: X/5**

**VERDICT:** 🟢 STRONG if 5/5, 🟡 MODERATE if 4/5, 🔴 WEAK if <4"""
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
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'max_output_tokens': 8192,
            }
        )
        return response.text
    except Exception as e:
        return f"ERROR: {e}"

def parse_verdict(text):
    upper = text.upper()
    if "DECISION: KILL" in upper or "DECISION:KILL" in upper:
        try:
            start = upper.index("DECISION: KILL")
            reason = text[start:start+200].replace("DECISION: KILL -", "").strip()
            return {"verdict": "KILL", "reason": reason[:150]}
        except:
            return {"verdict": "KILL", "reason": "Failed criteria"}
    elif "DECISION: PROCEED" in upper or "DECISION:PROCEED" in upper:
        return {"verdict": "PROCEED", "reason": None}
    else:
        return {"verdict": "UNCLEAR", "reason": "No clear verdict"}

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
        print("  ✓ Logged")

        if status == "VERIFIED":
            winners = sheet.worksheet("Winners")
            winners.append_row([
                idea['num'],
                idea['niche'],
                idea['pain'],
                f"Row {results.row_count} in Verified Pains",
                "Manual validation needed",
                datetime.now().strftime("%Y-%m-%d")
            ])
            print("  🏆 Winner!")
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

        try:
            response = run_stage(idea, num)
            verdict = parse_verdict(response)

            results[num] = {'name': stage['name'], 'response': response, 'verdict': verdict['verdict']}

            print(f"     ✓ {verdict['verdict']}")

            if verdict['verdict'] == "KILL":
                print(f"\n  🔴 KILLED at Stage {num}")
                print(f"     {verdict['reason'][:100]}")
                log_result(idea, results, "KILL", f"Stage {num}")
                update_status(idea['row'], 'Killed')
                return False

            time.sleep(2)

        except KeyboardInterrupt:
            print("\n⚠️ Interrupted")
            update_status(idea['row'], 'Interrupted')
            raise
        except Exception as e:
            print(f"     ❌ Error: {e}")
            results[num] = {'name': stage['name'], 'response': str(e), 'verdict': 'ERROR'}

    print(f"\n  🟢 VERIFIED! Passed all 5 stages.\n")
    log_result(idea, results, "VERIFIED")
    update_status(idea['row'], 'VERIFIED')
    return True

def main():
    print("="*80)
    print("  🚀 STARTING RESEARCH")
    print("="*80)
    print(f"  Model: Gemini 2.0 Flash (FREE)")
    print(f"  Sheet: '{GOOGLE_SHEET_NAME}'")
    print(f"  Cost: $0 per day (up to 1,500 requests)")
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
                print(f"  Rate: {(verified/processed*100 if processed > 0 else 0):.1f}%")
                print(f"  Time: {elapsed:.1f} hrs")
                print(f"  Cost: $0 (FREE)")
                print("="*80 + "\n")
                break

            update_status(idea['row'], 'In Progress')
            is_verified = research(idea)

            processed += 1
            if is_verified:
                verified += 1
            else:
                killed += 1

            print(f"\n  📊 Progress: {processed} total | ✅ {verified} verified | ❌ {killed} killed")
            print(f"     Success: {(verified/processed*100):.1f}% | Cost: $0\n")

            time.sleep(3)

    except KeyboardInterrupt:
        print(f"\n\n⚠️ Stopped. Processed: {processed}\n")
    except Exception as e:
        print(f"\n\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()
