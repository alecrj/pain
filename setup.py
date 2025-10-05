#!/usr/bin/env python3
"""
Interactive setup helper
Guides you through getting Google Sheets API credentials
"""

import os
import sys

print("\n" + "="*70)
print("  🔧 GOOGLE SHEETS API SETUP HELPER")
print("="*70 + "\n")

print("We need to set up Google Sheets API access.")
print("This is FREE and takes ~5 minutes.\n")

print("STEP 1: Create Google Cloud Project")
print("-" * 70)
print("1. Open: https://console.cloud.google.com/")
print("2. Click the project dropdown (top left)")
print("3. Click 'New Project'")
print("4. Name it: pain-finder-free")
print("5. Click Create and wait 10 seconds")
input("\nPress ENTER when done...\n")

print("\nSTEP 2: Enable APIs")
print("-" * 70)
print("1. Make sure 'pain-finder-free' is selected (top left)")
print("2. Go to: https://console.cloud.google.com/apis/library")
print("3. Search 'Google Sheets API' → Click it → Enable")
print("4. Go back, search 'Google Drive API' → Click it → Enable")
input("\nPress ENTER when both APIs are enabled...\n")

print("\nSTEP 3: Create Service Account")
print("-" * 70)
print("1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts")
print("2. Click '+ CREATE SERVICE ACCOUNT'")
print("3. Name: pain-finder-bot")
print("4. Click 'Create and Continue'")
print("5. Skip role selection → Click 'Continue'")
print("6. Skip user access → Click 'Done'")
input("\nPress ENTER when service account is created...\n")

print("\nSTEP 4: Create JSON Key")
print("-" * 70)
print("1. Click on your service account email in the list")
print("2. Click 'KEYS' tab")
print("3. Click 'ADD KEY' → 'Create new key'")
print("4. Choose JSON")
print("5. Click 'Create'")
print("6. File downloads automatically")
input("\nPress ENTER when JSON file is downloaded...\n")

print("\nSTEP 5: Move JSON File")
print("-" * 70)
downloads = os.path.expanduser("~/Downloads")
json_files = [f for f in os.listdir(downloads) if f.endswith('.json') and 'pain-finder' in f.lower()]

if json_files:
    latest = max([os.path.join(downloads, f) for f in json_files], key=os.path.getctime)
    print(f"Found: {os.path.basename(latest)}")

    import shutil
    dest = os.path.join(os.getcwd(), 'google-credentials.json')
    shutil.copy(latest, dest)
    print(f"✓ Moved to: {dest}")

    # Extract service account email
    import json
    with open(dest, 'r') as f:
        data = json.load(f)
        email = data.get('client_email', '')

    print(f"\n✓ Service Account Email: {email}")
    print("\n⚠️  IMPORTANT: Copy this email! You'll need it to share your Google Sheet.")

    with open('.service-account-email.txt', 'w') as f:
        f.write(email)

    print("   (Also saved to: .service-account-email.txt)")

else:
    print("❌ Could not find JSON file in Downloads.")
    print("   Please manually move it:")
    print(f"   mv ~/Downloads/pain-finder-*.json ./google-credentials.json")

print("\n" + "="*70)
print("  ✅ GOOGLE SHEETS API SETUP COMPLETE!")
print("="*70 + "\n")

print("Next step: Configure API keys in .env file")
