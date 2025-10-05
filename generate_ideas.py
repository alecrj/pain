#!/usr/bin/env python3
"""
Idea Generator - Creates 30 pain points at a time
FREE using Gemini 2.0 Flash
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

PROMPT = """Generate 30 ultra-specific micro-niche business pain points.

HYPER-SPECIFIC niches only (not "contractors" → "residential HVAC contractors in CA")
Focus on MANUAL tasks (data entry, forms, reconciliation, tracking)

Format as CSV:
Micro-Niche,Specific Task/Pain

Examples (don't repeat):
Residential HVAC contractors in California,Title 24 compliance form filling
Property managers 10-50 units,Maintenance request tracking across properties
Personal injury attorneys,Medical record organization from multiple providers

Generate 30 NEW ones:"""

print("\n💡 Generating 30 ideas with Gemini (FREE)...\n")

try:
    response = model.generate_content(PROMPT, generation_config={'temperature': 0.9})
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
    if not line.strip() or 'Micro-Niche' in line:
        continue

    if ',' in line:
        parts = [p.strip() for p in line.split(',', 1)]
        if len(parts) >= 2:
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

print(f"\n✅ Added {added} ideas!")
print(f"   Run: python pain_finder.py\n")
