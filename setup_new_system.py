#!/usr/bin/env python3
"""
Setup Script for 3-Stage Winner System
Creates all necessary Google Sheet tabs
"""

import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Pain Point Research")

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

creds = Credentials.from_service_account_file('google-credentials.json', scopes=SCOPES)
gc = gspread.authorize(creds)
sheet = gc.open(GOOGLE_SHEET_NAME)

print("\n🔧 Setting up 3-Stage Winner System...")
print("="*70)

# Create/update Ideas Queue
try:
    queue = sheet.worksheet("Ideas Queue")
    print("✓ Ideas Queue exists")
except:
    queue = sheet.add_worksheet(title="Ideas Queue", rows=1000, cols=6)
    queue.append_row(["ID", "Business Type", "Pain Point", "Status", "Date Added", "Notes"])
    print("✓ Created Ideas Queue")

# Create Stage 1: Growth Pass
try:
    stage1 = sheet.worksheet("Stage 1: Growth Pass")
    print("✓ Stage 1: Growth Pass exists")
except:
    stage1 = sheet.add_worksheet(title="Stage 1: Growth Pass", rows=500, cols=6)
    stage1.append_row(["ID", "Business Type", "Pain Point", "Status", "Analysis Summary", "Date"])
    print("✓ Created Stage 1: Growth Pass")

# Create Stage 2: Budget Pass
try:
    stage2 = sheet.worksheet("Stage 2: Budget Pass")
    print("✓ Stage 2: Budget Pass exists")
except:
    stage2 = sheet.add_worksheet(title="Stage 2: Budget Pass", rows=200, cols=6)
    stage2.append_row(["ID", "Business Type", "Pain Point", "Status", "Budget Analysis", "Date"])
    print("✓ Created Stage 2: Budget Pass")

# Create TRUE WINNERS
try:
    winners = sheet.worksheet("TRUE WINNERS")
    print("✓ TRUE WINNERS exists")
except:
    winners = sheet.add_worksheet(title="TRUE WINNERS", rows=100, cols=6)
    winners.append_row(["ID", "Business Type", "Pain Point", "Final Status", "Report Summary", "Date"])
    print("✓ Created TRUE WINNERS")

print("\n" + "="*70)
print("✅ Setup complete!")
print("\n📋 Sheet Structure:")
print("   1. Ideas Queue       → All generated ideas (starting point)")
print("   2. Stage 1: Growth Pass   → Passed growth filter (~20%)")
print("   3. Stage 2: Budget Pass   → Passed budget filter (~10%)")
print("   4. TRUE WINNERS      → Final winners (~1-2%)")
print("\n🚀 Ready to run:")
print("   python generate_winners.py")
print("   python run_winner_pipeline.py")
print("="*70 + "\n")
