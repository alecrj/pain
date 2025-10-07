# Google Custom Search Setup (Required for v3.1)

v3.1 requires a Google Custom Search Engine to get REAL, cited evidence with clickable URLs.

## Why Google Custom Search?

- **FREE**: 100 searches/day
- **REAL URLs**: No more fake evidence like "[Reddit] - [2024]"
- **Recent results**: Filters to 2024-2025 only
- **Verifiable**: Every claim has a clickable URL you can verify

---

## Setup Steps (5 minutes)

### Step 1: Create Custom Search Engine

1. Go to: https://programmablesearchengine.google.com/
2. Click **"Get started"** or **"Add"**
3. **Sites to search**: Enter `*` (searches entire web)
4. **Language**: English
5. **Name**: "Winner Machine Search" (or anything)
6. Click **"Create"**

### Step 2: Get your Search Engine ID

1. Click **"Customize"** on your new search engine
2. Find **"Search engine ID"** (looks like: `a1b2c3d4e5f6g7h8i`)
3. **Copy it**

### Step 3: Enable the API

1. Go to: https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Go to **APIs & Services > Library**
4. Search for **"Custom Search API"**
5. Click **"Enable"**

### Step 4: Create API Key

1. Go to **APIs & Services > Credentials**
2. Click **"Create Credentials" > "API Key"**
3. **Copy the API key** (looks like: `AIzaSy...`)
4. (Optional) Click **"Restrict Key"** and limit to "Custom Search API" only

### Step 5: Add to .env file

Open `.env` and replace the placeholder:

```bash
GOOGLE_CSE_ID=REPLACE_WITH_YOUR_CUSTOM_SEARCH_ENGINE_ID
```

With your actual ID:

```bash
GOOGLE_CSE_ID=a1b2c3d4e5f6g7h8i
```

Your `.env` should now have:
```bash
GOOGLE_API_KEY=AIzaSy...  # (you already have this)
GOOGLE_CSE_ID=a1b2c3d4e5f6g7h8i  # (your new search engine ID)
OPENAI_API_KEY=sk-proj-...  # (you already have this)
```

---

## Test It

Run with 1 idea to verify it works:

```bash
python ultimate_winner_machine_v3.1.py --count=1
```

You should see:
- **Stage 3 searches returning REAL URLs** (not "[Reddit]" placeholders)
- **Clickable links** like `https://reddit.com/r/...`
- **Real snippets** from 2024-2025

---

## Troubleshooting

### "No GOOGLE_CSE_ID found"
- Check `.env` has `GOOGLE_CSE_ID=...` (not the placeholder text)
- Search Engine ID should be alphanumeric (like `a1b2c3d4e5f6g7h8i`)

### "API key not valid" error
- Make sure you **enabled the Custom Search API** in Google Cloud Console
- Check your API key is correct in `.env`
- Wait 1-2 minutes after creating the key (can take time to activate)

### "No results found" for every search
- Check your Custom Search Engine searches the **entire web** (`*`)
- Not restricted to specific sites

### "Quota exceeded" error
- You've hit 100 searches/day limit
- Wait 24 hours or upgrade to paid plan ($5 per 1000 queries)
- 100 free = ~30 ideas/day (3 searches per idea)

---

## Cost

- **First 100 searches/day**: FREE
- **After 100/day**: $5 per 1,000 queries

For 100 ideas:
- 100 ideas × 3 searches = 300 searches
- 100 free + 200 paid = 200 × $0.005 = **$1**
- Plus OpenAI: ~$6 (o4-mini)
- **Total: ~$7 per 100 ideas**

---

## Why Not Perplexity?

v3.0 used Perplexity API which:
- Costs $0.01 per search (3× more expensive)
- Requires paid account
- No free tier

Google Custom Search is:
- FREE for 100/day
- Better for this use case (need many searches)
- Same quality results

---

## You're Ready!

Once you see real URLs in Stage 3 output, v3.1 is working correctly.

Run the full 100 ideas:

```bash
python ultimate_winner_machine_v3.1.py --count=100
```

(Will take 3-4 days if staying in free tier - 30 ideas/day)
