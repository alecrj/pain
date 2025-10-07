#!/usr/bin/env python3
"""
Idea Generator for 3-Stage Winner System
Generates ideas ONLY for allowed industries (no licensing/API restrictions)
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

PROMPT = """Generate 50 ultra-specific pain points for GROWING businesses with MONEY to pay.

CRITICAL CONSTRAINTS:

✅ **ALLOWED INDUSTRIES (No Licensing/Regulation):**
- Construction/General Contractors
- Manufacturing (discrete/process)
- Retail (physical stores, NOT e-commerce platforms)
- Hospitality (restaurants, hotels, catering)
- Logistics/Transportation
- Property Maintenance/Facilities Management
- Wholesale Distribution
- Agriculture/Farming
- Marketing/Advertising Agencies
- Event Planning
- Professional Services (consulting, training, recruiting)
- Landscaping/Grounds Maintenance
- Commercial Cleaning
- Equipment Rental
- Print/Signage
- Warehousing/Fulfillment

❌ **EXCLUDED (Licensing/Regulatory Hell):**
- Healthcare/Medical/Dental
- Insurance
- Finance/Banking
- Legal/Law Firms
- Real Estate Sales
- Pharmacy
- Childcare/Education
- Senior Care/Home Health
- Counseling/Therapy
- Alcohol/Cannabis

🎯 **TARGET: Businesses That:**
- Are growing >10% YoY (hiring, expanding)
- Already spend on software/tools
- Have clear decision makers (VP, Director, Owner)
- Face urgent, revenue-impacting problems
- Use manual processes costing time/money

💡 **SOLUTION REQUIREMENTS:**
- Must be solvable with software (SaaS, web app, mobile app)
- NO enterprise API dependencies (Salesforce, SAP integrations required)
- Can use PUBLIC APIs only (Google Maps, weather, etc.) or no APIs
- NO physical products, NO services requiring licensing

📊 **FOCUS ON:**
- Operations/workflow pain (scheduling, tracking, coordination)
- Data/reporting pain (manual spreadsheets, reconciliation)
- Communication pain (phone tag, email chaos)
- Compliance/documentation pain (paperwork, audits)
- Financial pain (invoicing, billing, payment tracking)

EXAMPLES (don't repeat):
Commercial HVAC contractors,Tracking equipment maintenance schedules across 50+ client sites using paper logbooks
Manufacturing plants,Reconciling inventory counts between warehouse floor and ERP system using spreadsheets
Restaurant groups,Managing food cost tracking and recipe costing across 12 locations manually
Distribution companies,Coordinating delivery routes and driver schedules via text messages and phone calls
Event venues,Managing vendor contracts and payment schedules through email and Excel
Marketing agencies,Tracking billable hours across 30+ client projects using manual timesheets

Generate 50 NEW pain points NOW - focus on GROWING industries with PROVEN budgets:

Format as CSV:
Business Type (specific industry),Specific Operational/Financial Pain Point
"""

print("\n💡 Generating 50 high-potential business opportunities...\n")

try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a business opportunity analyst. You identify high-growth industries with real budgets and urgent problems."},
            {"role": "user", "content": PROMPT}
        ],
        temperature=0.9,
        max_tokens=6000
    )
    ideas = response.choices[0].message.content
    print("✓ Generated!\n")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("📝 Adding to Google Sheet (Ideas Queue)...\n")

queue = sheet.worksheet("Ideas Queue")
current = len(queue.get_all_values())
next_num = current
added = 0

for line in ideas.strip().split('\n'):
    if not line.strip() or 'Business Type' in line or 'CSV' in line or 'Format' in line:
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
            print(f"  ✓ {parts[0][:60]}...")
            next_num += 1
            added += 1

print(f"\n✅ Added {added} high-potential opportunities!")
print(f"\n🚀 Next steps:")
print(f"   1. python stage1_growth_filter.py")
print(f"   2. python stage2_budget_validator.py")
print(f"   3. python stage3_deep_research.py")
print(f"\nOr run all at once: python run_winner_pipeline.py\n")
