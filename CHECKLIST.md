# ✅ Setup Checklist

Follow these steps in order. Check off each one as you complete it.

## 🔑 Step 1: Get Google AI API Key
- [ ] Go to: https://aistudio.google.com/app/apikey
- [ ] Click "Create API Key"
- [ ] Copy the key (starts with `AIza...`)
- [ ] Save it somewhere

## 🔧 Step 2: Setup Google Sheets API
```bash
cd /Users/alec/desktop/pain-finder-system
source venv/bin/activate
python setup.py
```
- [ ] Follow the interactive prompts
- [ ] Copy the service account email shown at the end
- [ ] Confirm file `google-credentials.json` exists
- [ ] Confirm file `.service-account-email.txt` exists

## 📊 Step 3: Create Google Sheet
- [ ] Go to: https://sheets.google.com/
- [ ] Create new spreadsheet named: **Pain Point Research**
- [ ] Create 3 sheets (tabs): **Ideas Queue**, **Verified Pains**, **Winners**
- [ ] Add headers to **Ideas Queue**: `Idea #`, `Micro-Niche`, `Specific Task/Pain`, `Status`, `Date Added`
- [ ] Add headers to **Verified Pains**: `Idea #`, `Micro-Niche`, `Pain`, `Raw Complaints`, `Quantification`, `Widespread`, `Competition`, `Documentation`, `Status`, `Kill Stage`, `Timestamp`
- [ ] Add headers to **Winners**: `Idea #`, `Micro-Niche`, `Specific Pain`, `Research Link`, `Next Phase`, `Date Found`
- [ ] Click "Share" → Paste service account email → Change to "Editor" → Uncheck "Notify" → Share

## ⚙️ Step 4: Configure .env File
```bash
cp .env.example .env
nano .env
```
- [ ] Add your Google AI API key (from Step 1)
- [ ] Confirm sheet name is `Pain Point Research`
- [ ] Save file (Ctrl+O, Enter, Ctrl+X)

## 🧪 Step 5: Test It
```bash
source venv/bin/activate
python generate_ideas.py
```
- [ ] See "✓ Generated!" message
- [ ] See "✅ Added 30 ideas!" message
- [ ] Check Google Sheet - see 30 rows in "Ideas Queue"

## 🚀 Step 6: Run First Research
```bash
python pain_finder.py
```
- [ ] See "✅ System ready!" message
- [ ] Watch it process first idea through 5 stages
- [ ] Check Google Sheet - see results in "Verified Pains"

## 📈 Step 7: Scale Up
```bash
# Generate lots of ideas
python generate_ideas.py
python generate_ideas.py
python generate_ideas.py

# Run in background
nohup python pain_finder.py > research.log 2>&1 &

# Watch logs
tail -f research.log
```
- [ ] Generated 100+ ideas
- [ ] Research bot running in background
- [ ] Can see progress in Google Sheet

## 🎯 Step 8: Find Winners
- [ ] Check "Winners" sheet for 5/5 verified pain points
- [ ] Read full research in "Verified Pains" sheet
- [ ] Start manual validation (LinkedIn outreach)

---

## ✅ You're Done!

Your automated pain point finder is now running!

**What it does:**
- Processes hundreds of business ideas automatically
- Runs 5-stage validation on each
- Kills 85-90% that don't meet criteria
- Surfaces the 5-15% that are verified pain points
- Logs everything to Google Sheet

**Cost:** FREE for first ~100 ideas/day

**Goal:** Find 1-2 verified pain points (5/5 score) worth manually validating with customers, then build the solution!
