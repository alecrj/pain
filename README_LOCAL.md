# Pain Point Finder - FREE Edition

Automated system to find verified business pain points using Google Gemini 2.0 Flash (FREE tier).

## 🚀 Quick Start

### 1. Get API Keys (10 min)

**Google AI API Key (FREE):**
1. Go to: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)

**Google Sheets API:**
1. Run: `python setup.py`
2. Follow the interactive prompts
3. Copy the service account email shown at the end

### 2. Create Google Sheet (5 min)

1. Go to: https://sheets.google.com/
2. Create new spreadsheet named: **Pain Point Research**
3. Create 3 sheets (tabs):
   - **Ideas Queue**
   - **Verified Pains**
   - **Winners**

4. Add headers:

**Ideas Queue sheet (Row 1):**
```
A1: Idea #
B1: Micro-Niche
C1: Specific Task/Pain
D1: Status
E1: Date Added
```

**Verified Pains sheet (Row 1):**
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

**Winners sheet (Row 1):**
```
A1: Idea #
B1: Micro-Niche
C1: Specific Pain
D1: Research Link
E1: Next Phase
F1: Date Found
```

5. **Share with service account:**
   - Click "Share" (top right)
   - Paste service account email (from `.service-account-email.txt`)
   - Change to "Editor"
   - Uncheck "Notify people"
   - Click "Share"

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your keys
nano .env
```

Put in your actual keys:
```
GOOGLE_API_KEY=AIza-your-actual-key-here
GOOGLE_SHEET_NAME=Pain Point Research
```

### 4. Generate Ideas

```bash
# Activate virtual environment
source venv/bin/activate

# Generate 30 ideas (run multiple times)
python generate_ideas.py
python generate_ideas.py
python generate_ideas.py

# Now you have 90+ ideas in queue
```

### 5. Start Research

```bash
# Run in foreground (see live updates)
python pain_finder.py

# OR run in background
nohup python pain_finder.py > research.log 2>&1 &

# Watch logs
tail -f research.log
```

## 📊 How It Works

### 5-Stage Validation Process

1. **Raw Complaints** - Find 5+ people complaining with numbers
2. **Quantification** - Get 3+ sources with hard data
3. **Market Size** - Verify 5,000+ businesses affected
4. **Competition** - Check for weak/no competitors
5. **Documentation** - Create detailed pain profile

Ideas must pass ALL 5 stages to be verified.

### What Gets Logged

- **Ideas Queue**: All ideas with status (Pending/In Progress/Killed/Verified)
- **Verified Pains**: Detailed research for each idea tested
- **Winners**: Only 5/5 verified pain points (ready for validation)

## 💰 Cost

- **FREE tier**: 1,500 requests/day
- Each idea ≈ 15 requests
- **~100 ideas/day for $0**
- After free tier: ~$0.01/idea

## 📈 Expected Results

| Ideas Processed | Verified Pains (5-15%) | True Winners (1-2%) |
|----------------|----------------------|-------------------|
| 100            | 5-15                 | 1-2               |
| 300            | 15-45                | 3-6               |
| 500            | 25-75                | 5-10              |

## 🎯 What to Do With Winners

1. Check "Winners" sheet for 5/5 scored ideas
2. Read full research in "Verified Pains" sheet
3. **Manually validate:**
   - Find 20 people in that niche (LinkedIn)
   - Message: "Do you spend [X hours] on [Y task]?"
   - If 50%+ say YES → Build it!

## 🛠️ Commands

```bash
# Activate environment
source venv/bin/activate

# Generate ideas
python generate_ideas.py

# Start research
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

## ⚠️ Troubleshooting

**"Module not found"**
```bash
source venv/bin/activate
pip install google-generativeai gspread google-auth python-dotenv
```

**"Can't connect to Google Sheets"**
- Check sheet name in .env matches exactly
- Verify service account has Editor access
- Check `.service-account-email.txt` for email

**"API key invalid"**
- Get new key: https://aistudio.google.com/app/apikey
- Update .env file

## 📝 Files

- `setup.py` - Interactive Google Sheets setup
- `generate_ideas.py` - Creates 30 pain points
- `pain_finder.py` - Main research bot (5-stage validation)
- `.env` - Your API keys
- `google-credentials.json` - Google Sheets credentials

## 🚀 Quick Start (TL;DR)

```bash
# 1. Setup
python setup.py

# 2. Create & share Google Sheet (see above)

# 3. Configure
cp .env.example .env
nano .env  # Add your keys

# 4. Generate ideas
source venv/bin/activate
python generate_ideas.py
python generate_ideas.py
python generate_ideas.py

# 5. Start research
python pain_finder.py
```

Your system will now automatically find verified pain points! Check the "Winners" sheet for opportunities worth pursuing.
