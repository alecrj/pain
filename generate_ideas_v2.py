#!/usr/bin/env python3
"""
Idea Generator v2.0 - Digital/SaaS Pain Points ONLY
Generates specific software/automation opportunities
"""

import os
import sys
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Pain Point Research")

if not GOOGLE_API_KEY:
    print("❌ No API key in .env")
    sys.exit(1)

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = Credentials.from_service_account_file('google-credentials.json', scopes=SCOPES)
gc = gspread.authorize(creds)
sheet = gc.open(GOOGLE_SHEET_NAME)

PROMPT = """Generate 30 ultra-specific DIGITAL/SOFTWARE pain points ONLY.

CRITICAL RULES:
- ONLY software, automation, or digital service opportunities
- NO physical products (no manufacturing, inventory, shipping)
- NO brick-and-mortar businesses (no restaurants, retail stores, etc.)
- Focus on ONLINE/REMOTE problems that can be solved with software/SaaS

MUST be solvable with:
✅ Software/SaaS subscription
✅ Automation tool/platform
✅ Digital service/productized service
✅ Online marketplace/platform
✅ API/integration service
✅ Data/analytics product

TARGET: B2B pain points in knowledge work, professional services, online businesses

EXAMPLES (don't repeat):
B2B SaaS contractors (online businesses),Tracking subcontractor invoices across 10+ projects using spreadsheets
E-commerce store owners (Shopify/WooCommerce),Reconciling inventory between online store and warehouse management system
Digital marketing agencies,Reporting client campaign ROI across 5+ platforms manually
Remote accounting firms,Onboarding new clients with 20+ document requests via email
Online course creators,Managing student support tickets across email/Slack/social DMs
SaaS companies (B2B),Tracking feature requests from Intercom/email/calls in spreadsheets

Generate 30 NEW digital/software pain points now:

Format as CSV:
Micro-Niche (online/digital business type),Specific Software/Data/Automation Pain
"""

print("\n💡 Generating 30 DIGITAL pain point ideas...\n")

try:
    response = model.generate_content(
        PROMPT,
        generation_config={
            'temperature': 0.9,
            'max_output_tokens': 4000,
        }
    )
    ideas = response.text
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
    if not line.strip() or 'Micro-Niche' in line or 'CSV' in line:
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

print(f"\n✅ Added {added} DIGITAL pain point ideas!")
print(f"   These are software/SaaS opportunities only.")
print(f"   Run: python pain_finder_v2.py\n")
