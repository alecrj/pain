# 🚀 SETUP INSTRUCTIONS - START HERE

## Step 1: Get Google AI API Key (2 minutes)

1. Open: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)
4. Save it - you'll need it in Step 4

## Step 2: Setup Google Sheets API (5 minutes)

Run the setup helper:

```bash
cd /Users/alec/desktop/pain-finder-system
source venv/bin/activate
python setup.py
```

Follow the interactive prompts. At the end, it will show your service account email - **copy this email!**

## Step 3: Create Google Sheet (3 minutes)

1. Go to: https://sheets.google.com/
2. Create new spreadsheet
3. Name it: **Pain Point Research**

### Create 3 sheets (tabs at bottom):
- Ideas Queue
- Verified Pains
- Winners

### Add headers to each sheet:

**Ideas Queue (Row 1):**
```
A1: Idea #
B1: Micro-Niche
C1: Specific Task/Pain
D1: Status
E1: Date Added
```

**Verified Pains (Row 1):**
```
A1: Idea #
B1: Micro-Niche
C1: Pain
D1: Raw Complaints
E1: Quantification
F1: Widespread
G1: Competition
H1: Documentation
I1: Status
J1: Kill Stage
K1: Timestamp
```

**Winners (Row 1):**
```
A1: Idea #
B1: Micro-Niche
C1: Specific Pain
D1: Research Link
E1: Next Phase
F1: Date Found
```

### Share the sheet:
1. Click "Share" (top right)
2. Paste your service account email (from step 2)
3. Change permission to **Editor**
4. **Uncheck** "Notify people"
5. Click "Share"

## Step 4: Configure API Keys

```bash
# Copy example file
cp .env.example .env

# Edit it
nano .env
```

Replace with your actual keys:
```
GOOGLE_API_KEY=AIza-your-key-from-step-1
GOOGLE_SHEET_NAME=Pain Point Research
```

Save: Ctrl+O, Enter, Ctrl+X

## Step 5: Test It! (2 minutes)

```bash
# Make sure you're in the right folder and venv is active
cd /Users/alec/desktop/pain-finder-system
source venv/bin/activate

# Generate 30 test ideas
python generate_ideas.py
```

You should see:
```
💡 Generating 30 ideas with Gemini (FREE)...
✓ Generated!

📝 Adding to Google Sheet...
  ✓ Commercial refrigeration technicians...
  ✓ HOA property managers...
  [etc...]

✅ Added 30 ideas!
```

Check your Google Sheet - you should see 30 rows in "Ideas Queue"!

## Step 6: Start Research! (automatic)

```bash
# Run the research bot
python pain_finder.py
```

It will:
- Pick up the first pending idea
- Run through 5 stages of research
- Either kill it or verify it
- Log everything to the sheet
- Move to the next idea
- Repeat until queue is empty

Watch it work! Check your Google Sheet and see results populate in real-time.

## Step 7: Scale It Up

Once the test works, generate hundreds of ideas:

```bash
# Generate more ideas (run this 5-10 times)
python generate_ideas.py
python generate_ideas.py
python generate_ideas.py
python generate_ideas.py
python generate_ideas.py

# Now you have 150+ ideas queued

# Run research in background
nohup python pain_finder.py > research.log 2>&1 &

# Watch live logs
tail -f research.log
```

## 📊 Monitor Results

- **Google Sheet**: Watch rows populate in real-time
- **Winners tab**: Check for 5/5 verified pain points
- **Terminal**: See progress updates

## 🎯 Next Steps

When you find ideas in "Winners" sheet (5/5 score):
1. Read full research in "Verified Pains" sheet
2. Find 20 people in that niche on LinkedIn
3. Message them: "Do you spend [X hours] on [Y task]?"
4. If 50%+ say YES → You found your business!

## 💰 Cost

- **FREE**: First ~100 ideas per day
- After that: ~$0.01 per idea
- Much cheaper than Claude!

---

## Troubleshooting

**"Module not found"**
```bash
source venv/bin/activate
pip install google-generativeai gspread google-auth python-dotenv
```

**"Can't connect to Google Sheets"**
- Check sheet name in `.env` matches exactly
- Verify service account has Editor access
- Run `cat .service-account-email.txt` to get email

**"API key invalid"**
- Get new key at https://aistudio.google.com/app/apikey
- Update `.env` file

---

## Quick Reference

```bash
# Navigate to project
cd /Users/alec/desktop/pain-finder-system

# Activate environment
source venv/bin/activate

# Generate ideas
python generate_ideas.py

# Run research
python pain_finder.py

# Background mode
nohup python pain_finder.py > research.log 2>&1 &

# Watch logs
tail -f research.log

# Check status
ps aux | grep pain_finder

# Stop
pkill -f pain_finder.py
```

---

You're all set! 🚀

Your system will now automatically find verified business pain points. The goal is to process hundreds of ideas until you find 1-2 truly great opportunities (5/5 score) that you can manually validate and build into a business.
