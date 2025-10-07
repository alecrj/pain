#!/usr/bin/env python3
"""
Idea Generator v4.0 - OpenAI Edition
Generates software/automation opportunities for ANY business type
"""

import os
import sys
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

PROMPT = """Generate 30 ultra-specific pain points for REAL BUSINESSES that can be solved with digital/software solutions.

CRITICAL RULES:
✅ TARGET: ANY type of REAL business (construction, healthcare, legal, manufacturing, retail, restaurants, dental, accounting, real estate, etc.)
✅ PAIN: Manual/tedious processes that currently use spreadsheets, paper, email, phone calls
✅ SOLUTION: Must be solvable with software/SaaS (NOT physical products, NOT services requiring physical presence)

DO NOT LIMIT TO:
❌ Online-only businesses
❌ Virtual businesses
❌ Digital nomads
❌ "Online coaches" or "virtual assistants"

FOCUS ON:
- Brick-and-mortar businesses with real locations
- Traditional industries with outdated processes
- B2B businesses managing complex workflows
- Service businesses coordinating teams/clients
- Any business doing manual data entry, reconciliation, tracking, scheduling

SOLUTION TYPES (digital only):
✅ Software/SaaS platform
✅ Automation tool
✅ Mobile app for field workers
✅ Integration/API service
✅ Workflow management system
✅ Data analytics dashboard

EXAMPLES (don't repeat):
General contractors,Tracking change orders across 15+ active job sites using text messages and paper forms
Dental practices,Managing patient recall appointments with manual spreadsheet tracking and phone calls
Law firms,Billing time across multiple cases/clients using separate timers and spreadsheets
HVAC companies,Scheduling emergency service calls while technicians are in the field via phone tag
Accounting firms,Collecting tax documents from 200+ clients via email with manual follow-ups
Medical equipment distributors,Tracking inventory across 10+ hospital accounts using Excel
Restaurant groups,Reconciling daily sales across 8 locations with different POS systems
Commercial property managers,Coordinating maintenance requests from 30+ tenants via email and calls
Auto body shops,Estimating repair costs and tracking insurance approvals across 20+ active claims

Generate 30 NEW pain points for REAL businesses across diverse industries:

Format as CSV:
Business Type (be specific about industry),Specific Manual/Software Pain Point
"""

print("\n💡 Generating 30 pain point ideas for REAL businesses...\n")

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a market research expert finding pain points in real businesses."},
            {"role": "user", "content": PROMPT}
        ],
        temperature=0.9,
        max_tokens=4000
    )
    ideas = response.choices[0].message.content
    print("✓ Generated!\n")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("📝 Adding to Google Sheet...\n")

queue = sheet.worksheet("Ideas Queue")
current = len(queue.get_all_values())
next_num = current
added = 0

for line in ideas.strip().split('\n'):
    if not line.strip() or 'Business Type' in line or 'CSV' in line:
        continue

    if ',' in line:
        parts = [p.strip() for p in line.split(',', 1)]
        if len(parts) >= 2 and len(parts[0]) > 0:
            queue.append_row([
                next_num,
                parts[0],
                parts[1],
                "Pending",
                datetime.now().strftime("%Y-%m-%d")
            ])
            print(f"  ✓ {parts[0][:50]}...")
            next_num += 1
            added += 1

print(f"\n✅ Added {added} pain point ideas for REAL businesses!")
print(f"   These target traditional/brick-and-mortar businesses.")
print(f"   Solutions are digital/software (no physical products).")
print(f"   Run: python pain_finder_v4.py\n")
