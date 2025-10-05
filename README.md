# Pain Point Finder 🔍

> Automated system to discover verified business pain points using AI research. Find your next business idea by processing hundreds of micro-niche opportunities.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Cost: FREE](https://img.shields.io/badge/cost-FREE-green.svg)](https://aistudio.google.com/app/apikey)

## 🎯 What This Does

Automatically finds verified business pain points by:
- 💡 Generating hundreds of micro-niche business ideas
- 🔬 Researching each through 5 validation stages
- ❌ Killing 85-90% that don't meet strict criteria
- ✅ Surfacing 5-15% that are **verified pain points**
- 📊 Logging everything to Google Sheets

**Goal:** Find 1-2 verified pain points worth building a business around.

## 💰 Cost

- **FREE tier:** ~100 ideas/day at $0
- **After free tier:** ~$0.01 per idea
- **500 ideas total:** ~$2-5

Uses **Google Gemini 2.0 Flash** (FREE tier)

*vs Claude Sonnet 4: $130 for 500 ideas ❌*

## 📊 Expected Results

| Ideas Processed | Verified Pains (5-15%) | Worth Building (1-2%) |
|----------------|----------------------|-------------------|
| 100            | 5-15                 | 1-2               |
| 300            | 15-45                | 3-6               |
| 500            | 25-75                | 5-10              |

## 🔬 How It Works

### 5-Stage Validation Process

Each idea must pass ALL 5 stages to be verified:

1. **Raw Complaints** → Find 5+ people complaining with numbers (hours/week)
2. **Quantification** → Get 3+ sources with hard data (time/cost/errors)
3. **Market Size** → Verify 5,000+ businesses affected
4. **Competition** → Check for 0-2 weak competitors only
5. **Documentation** → Create detailed pain profile

**Kill rate:** ~85-90% of ideas don't make it through

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google account
- ~20 minutes for setup

### 1. Clone & Setup

```bash
git clone https://github.com/alecrj/pain.git
cd pain
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Get API Keys

**A. Google AI API Key (FREE)**
1. Go to: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)

**B. Google Sheets API**
```bash
python setup.py
```
Follow the interactive prompts. Save the service account email shown!

### 3. Create Google Sheet

1. Go to: https://sheets.google.com/
2. Create new spreadsheet named: **Pain Point Research**
3. Create 3 sheets (tabs):
   - `Ideas Queue`
   - `Verified Pains`
   - `Winners`

4. **Add headers** (see [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for details)

5. **Share the sheet:**
   - Click "Share"
   - Paste service account email (from step 2)
   - Change to "Editor"
   - Uncheck "Notify people"
   - Click "Share"

### 4. Configure Environment

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Add your keys:
```
GOOGLE_API_KEY=AIza-your-actual-key-here
GOOGLE_SHEET_NAME=Pain Point Research
```

### 5. Test It

```bash
source venv/bin/activate
python generate_ideas.py
```

Should see: `✅ Added 30 ideas!`

Check your Google Sheet → "Ideas Queue" should have 30 rows!

### 6. Run Research

```bash
python pain_finder.py
```

Watch it process ideas through 5 stages automatically!

## 📈 Scale It Up

Once test works, generate hundreds of ideas:

```bash
# Generate lots of ideas
python generate_ideas.py  # Run 5-10 times

# Run research in background
nohup python pain_finder.py > research.log 2>&1 &

# Watch live logs
tail -f research.log
```

## 🏆 What To Do With Winners

Check "Winners" sheet for ideas with 5/5 score:

1. Read full research in "Verified Pains" sheet
2. **Manually validate:**
   - Find 20 people in that niche on LinkedIn
   - Message: *"Quick question: do you spend [X hours/week] on [Y task]?"*
   - Track responses
3. **If 50%+ say YES → Build it!** 🚀

## 📁 Project Structure

```
pain-finder-system/
├── pain_finder.py          # Main research bot (5-stage validation)
├── generate_ideas.py       # Creates 30 pain point ideas
├── setup.py                # Interactive Google Sheets setup
├── .env.example            # Template for API keys
├── requirements.txt        # Python dependencies
├── START_HERE.md          # Quick start guide
├── CHECKLIST.md           # Step-by-step checklist
├── SETUP_INSTRUCTIONS.md  # Detailed setup guide
└── README.md              # This file
```

## 🛠️ Commands

```bash
# Navigate to project
cd pain-finder-system

# Activate environment
source venv/bin/activate

# Generate ideas
python generate_ideas.py

# Run research (foreground)
python pain_finder.py

# Run research (background)
nohup python pain_finder.py > research.log 2>&1 &

# Watch logs
tail -f research.log

# Check status
ps aux | grep pain_finder

# Stop
pkill -f pain_finder.py
```

## 🐛 Troubleshooting

### "Module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Can't connect to Google Sheets"
- Check `.env` sheet name matches exactly
- Verify service account has "Editor" access
- Check email: `cat .service-account-email.txt`

### "API key invalid"
- Get new key: https://aistudio.google.com/app/apikey
- Update `.env` file

## 🔐 Security Notes

⚠️ **NEVER commit these files:**
- `.env` (contains API keys)
- `google-credentials.json` (service account credentials)
- `.service-account-email.txt`

They're already in `.gitignore` but be careful!

## 📖 Documentation

- [START_HERE.md](START_HERE.md) - Quick start guide
- [CHECKLIST.md](CHECKLIST.md) - Step-by-step checklist
- [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) - Detailed setup guide

## 🤝 Contributing

This is a personal project for finding business ideas, but feel free to fork and customize for your own use!

## 📄 License

MIT License - feel free to use this for your own pain point research!

## 🙏 Acknowledgments

- Uses [Google Gemini 2.0 Flash](https://ai.google.dev/) for FREE AI research
- Inspired by systematic startup validation methodologies

## ⭐ Star This Repo

If this helps you find your next business idea, give it a star! ⭐

---

**Ready to find your next business opportunity?** 💎

Start with [START_HERE.md](START_HERE.md) for the complete setup guide.
