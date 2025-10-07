#!/usr/bin/env python3
"""
The Researcher v1.0 - Complete Stage 1 Framework
Implements the full "Researcher" role from your startup framework
Outputs COMPLETE research reports ready for "The Strategist" (Stage 2)
"""

import os
import sys
import time
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

RATE_LIMIT_DELAY = 1.0

def call_openai(prompt, max_tokens=4000):
    """Call OpenAI with retry logic"""
    time.sleep(RATE_LIMIT_DELAY)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Using full GPT-4 for deep research
            messages=[
                {"role": "system", "content": "You are a rigorous market researcher. You find REAL evidence from real sources. You cite URLs. You are thorough and detailed. You KILL ideas unless you find strong evidence."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"   ERROR: {e}", flush=True)
        return None

def parse_verdict(text):
    """Extract VERDICT from response"""
    if not text:
        return "KILL"

    text_upper = text.upper()

    if "VERDICT: KILL" in text_upper or "VERDICT:KILL" in text_upper:
        return "KILL"
    if "VERDICT: PROCEED" in text_upper or "VERDICT:PROCEED" in text_upper:
        return "PROCEED"

    kill_signals = ["NOT ENOUGH", "INSUFFICIENT", "TOO VAGUE", "CANNOT VERIFY", "FAILED TO FIND"]
    for signal in kill_signals:
        if signal in text_upper:
            return "KILL"

    if "PROCEED" in text_upper:
        return "PROCEED"

    return "KILL"

def stage1_find_problem(niche, pain):
    """Stage 1: Find & Validate the Problem (with citations)"""
    print(f"\n🔍 STAGE 1: Finding & Validating Problem...", flush=True)

    prompt = f"""You are researching a potential business idea:
TARGET CUSTOMER: {niche}
PROBLEM: {pain}

YOUR TASK: Find REAL evidence that this is an urgent and painful problem.

SEARCH FOR:
1. Reddit threads where {niche} complain about {pain}
2. Amazon reviews mentioning this frustration
3. Facebook/LinkedIn posts discussing this issue
4. Forum discussions about workarounds people are using
5. Industry reports quantifying this pain

REQUIREMENTS:
- Find 5+ SPECIFIC complaints from DIFFERENT sources
- Each must include EXACT QUOTES and SOURCE URLS
- Must show URGENCY (people say "I need this now" or "wasting X hours/week")
- Must show PAIN (frustration, money lost, time wasted)

FORMAT YOUR RESPONSE:

## COMPLAINTS FOUND

1. **Source:** [URL]
   **Quote:** "[exact quote]"
   **Pain Level:** [hours wasted OR money lost OR frequency]

2. **Source:** [URL]
   **Quote:** "[exact quote]"
   **Pain Level:** [quantify the pain]

[Continue for all 5+ complaints]

## PATTERN ANALYSIS
What is the CORE problem? What makes it so painful?

## VERDICT: [KILL or PROCEED]
- KILL if: <5 complaints, vague pain, no urgency, no real sources
- PROCEED if: 5+ real complaints with URLs showing urgent pain

Only PROCEED if this is clearly a painful problem people want solved NOW."""

    result = call_openai(prompt)
    verdict = parse_verdict(result)
    print(f"   {verdict}", flush=True)
    return verdict, result

def stage2_market_research(niche, pain, stage1_data):
    """Stage 2: Deep Market Research (size, growth, demand)"""
    print(f"\n📊 STAGE 2: Market Size & Growth Analysis...", flush=True)

    prompt = f"""This problem passed Stage 1:
TARGET: {niche}
PROBLEM: {pain}

STAGE 1 EVIDENCE:
{stage1_data[:2000]}

YOUR TASK: Assess market size, growth trends, and consumer demand.

RESEARCH:
1. **Market Size:** How many {niche} exist? (Use IBISWorld, Statista, Census data, LinkedIn)
2. **Growth Trends:** Is this industry growing or shrinking? By how much per year?
3. **Consumer Demand:** Search volumes, Google Trends, survey data showing need

FORMAT YOUR RESPONSE:

## MARKET SIZE
- Total {niche} in target market: [NUMBER with citation]
- Estimated TAM (businesses willing to pay): [NUMBER with citation]
- Market concentration: [geographic/demographic insights]

## GROWTH TRENDS
- Industry growth rate: [%/year with citation]
- Key drivers: [what's fueling growth?]
- Trajectory: [expanding, stable, declining?]

## CONSUMER DEMAND EVIDENCE
- Search volume for related terms: [data from Google Trends, SEMrush, etc.]
- Survey/study results: [% of target facing this problem]
- Market signals: [new competitors entering? Funding rounds? M&A activity?]

## VERDICT: [KILL or PROCEED]
- KILL if: <5,000 TAM, declining industry, no demand evidence
- PROCEED if: 5,000+ TAM, growing/stable industry, clear demand signals

Only PROCEED if this is a real market opportunity."""

    result = call_openai(prompt, max_tokens=5000)
    verdict = parse_verdict(result)
    print(f"   {verdict}", flush=True)
    return verdict, result

def stage3_competitive_landscape(niche, pain):
    """Stage 3: Competitive Landscape & Differentiation"""
    print(f"\n⚔️  STAGE 3: Competitive Analysis...", flush=True)

    prompt = f"""Analyze competitors for this opportunity:
TARGET: {niche}
PROBLEM: {pain}

YOUR TASK: Find existing solutions and identify differentiation opportunities.

RESEARCH:
1. Search G2, Capterra, Software Advice for relevant tools
2. Google search for "[niche] [pain] software"
3. Check ProductHunt, Reddit for what people currently use
4. Identify DIY solutions/workarounds

CLASSIFY COMPETITORS:
- **STRONG:** Purpose-built for this niche, good reviews (4+★), active development
- **WEAK:** Generic tool, poor reviews (<3★), outdated, clunky UI

FORMAT YOUR RESPONSE:

## COMPETITORS

### Strong Competitors (if any)
1. **[Name]** - [URL]
   - Strengths: [what they do well]
   - Weaknesses: [gaps, complaints, pricing issues]
   - Market position: [# customers, reviews, funding]

### Weak Competitors (if any)
[Same format]

### DIY Solutions
What are people hacking together now? (Excel + email, etc.)

## DIFFERENTIATION OPPORTUNITIES
Based on competitor weaknesses and user complaints:
1. [Opportunity #1 with evidence]
2. [Opportunity #2 with evidence]
3. [Opportunity #3 with evidence]

## COMPETITIVE ADVANTAGE SUSTAINABILITY
How defensible is this differentiation long-term?

## VERDICT: [KILL or PROCEED]
- KILL if: 3+ strong competitors with no clear gaps
- PROCEED if: 0-2 weak competitors OR clear differentiation opportunities

Only PROCEED if there's a real competitive opening."""

    result = call_openai(prompt, max_tokens=5000)
    verdict = parse_verdict(result)
    print(f"   {verdict}", flush=True)
    return verdict, result

def stage4_pricing_monetization(niche, pain, market_data):
    """Stage 4: Pricing, Margins & Monetization Strategy"""
    print(f"\n💰 STAGE 4: Pricing & Monetization...", flush=True)

    prompt = f"""Develop pricing strategy for this opportunity:
TARGET: {niche}
PROBLEM: {pain}

MARKET CONTEXT:
{market_data[:1500]}

YOUR TASK: Recommend pricing model and revenue strategy.

RESEARCH:
1. What do competitors charge? (check their pricing pages)
2. What do similar SaaS tools charge for {niche}?
3. What's the typical budget for {niche} for software tools?
4. Industry benchmarks for SaaS pricing in this vertical

FORMAT YOUR RESPONSE:

## PRICING BENCHMARKS
- Competitor pricing range: $X - $Y/month
- Industry standard for similar tools: $Z/month
- Customer willingness to pay: [evidence from reviews, surveys]

## RECOMMENDED PRICING STRATEGY
- **Model:** [Freemium / Free Trial / Paid Only]
- **Pricing Tiers:**
  - Starter: $X/month - [features]
  - Professional: $Y/month - [features]
  - Enterprise: $Z/month - [features]
- **Rationale:** [why this structure works for this market]

## PROFIT MARGINS
- Estimated costs: [hosting, support, development]
- Projected gross margin: [%]
- Break-even point: [# customers]

## REVENUE EXPANSION OPPORTUNITIES
- Upsells: [premium features, add-ons]
- Cross-sells: [complementary products]
- Recurring revenue potential: [MRR projections]

## CUSTOMER ECONOMICS
- Est. CAC (Customer Acquisition Cost): $X
- Est. LTV (Lifetime Value): $Y
- LTV:CAC ratio: [ratio] - [healthy is 3:1+]

## VERDICT: [KILL or PROCEED]
- KILL if: Pricing too low to be profitable, LTV:CAC <2:1, no expansion potential
- PROCEED if: Healthy margins, clear monetization path, sustainable economics

Only PROCEED if this can be a real business."""

    result = call_openai(prompt, max_tokens=5000)
    verdict = parse_verdict(result)
    print(f"   {verdict}", flush=True)
    return verdict, result

def stage5_operations_scalability(niche, pain):
    """Stage 5: Operations, Scalability & Feasibility"""
    print(f"\n🏗️  STAGE 5: Operations & Scalability...", flush=True)

    prompt = f"""Assess operational feasibility for:
TARGET: {niche}
PROBLEM: {pain}

YOUR TASK: Evaluate what it takes to build and scale this business.

FORMAT YOUR RESPONSE:

## RESOURCES NEEDED TO LAUNCH
- **Technology:** [required stack, integrations, APIs]
- **Team:** [key hires: developer, designer, support?]
- **Capital:** [estimated initial investment]
- **Partnerships:** [critical vendors, data providers, etc.]

## OPERATIONAL CHALLENGES
- Unique complexities for this niche
- Technical difficulty (1-10 scale)
- Regulatory/compliance requirements
- Customer support demands

## SCALABILITY ASSESSMENT
- Can this grow 10x without linear cost increase?
- Automation potential: [high/medium/low]
- Unit economics at scale: [do margins improve?]
- Quality maintenance: [can we scale without degrading UX?]

## VERDICT: [KILL or PROCEED]
- KILL if: Requires massive capital, non-scalable, too complex
- PROCEED if: Feasible to launch, clear path to scale efficiently

Only PROCEED if this is operationally viable."""

    result = call_openai(prompt, max_tokens=4000)
    verdict = parse_verdict(result)
    print(f"   {verdict}", flush=True)
    return verdict, result

def stage6_risks_validation(niche, pain, all_data):
    """Stage 6: Risks, Red Flags & Validation Plan"""
    print(f"\n⚠️  STAGE 6: Risk Assessment & Validation...", flush=True)

    prompt = f"""Risk analysis for:
TARGET: {niche}
PROBLEM: {pain}

PREVIOUS RESEARCH:
{all_data[:3000]}

YOUR TASK: Identify risks and create validation plan.

FORMAT YOUR RESPONSE:

## MAJOR RISKS
1. **Market Risk:** [What if demand isn't real?]
2. **Competitive Risk:** [What if incumbent responds?]
3. **Operational Risk:** [What could go wrong in execution?]
4. **Regulatory Risk:** [Compliance, legal, IP issues?]
5. **Technical Risk:** [What if we can't build it?]

## BARRIERS TO ENTRY
- Licenses/certifications needed: [list]
- Technical complexity: [challenges]
- Capital requirements: [minimums]
- Network effects: [do incumbents have lock-in?]

## RED FLAGS / WARNING SIGNS
Early indicators this might not work:
- [Red flag #1]
- [Red flag #2]
- [Red flag #3]

## WHY THIS COULD FAIL
Be brutally honest: [top 3 reasons this could fail]

## VALIDATION EXPERIMENTS
Cheap, fast tests to validate assumptions:

1. **Test #1:** [what to test]
   - **Method:** [how to test it]
   - **Success criteria:** [what proves it works]
   - **Cost/Time:** [$X, Y days]

2. **Test #2:** [what to test]
   [same format]

3. **Test #3:** [what to test]
   [same format]

## VERDICT: [KILL or PROCEED]
- KILL if: Massive risks with no mitigation, fundamental flaws
- PROCEED if: Risks are manageable, clear validation path

Only PROCEED if we can test this cheaply before fully committing."""

    result = call_openai(prompt, max_tokens=5000)
    verdict = parse_verdict(result)
    print(f"   {verdict}", flush=True)
    return verdict, result

def stage7_customer_acquisition(niche, pain):
    """Stage 7: Customer Acquisition Strategy"""
    print(f"\n🎯 STAGE 7: Customer Acquisition Plan...", flush=True)

    prompt = f"""Build customer acquisition strategy for:
TARGET: {niche}
PROBLEM: {pain}

YOUR TASK: Map out how to reach and acquire these customers.

FORMAT YOUR RESPONSE:

## BRAND STORY & POSITIONING
**Elevator Pitch (15 seconds):**
[Concise pitch]

**Value Statement:**
"I help [audience] solve [problem] so they can [outcome]."

## WHERE TARGET CUSTOMERS HANG OUT
- Online communities: [Reddit subs, FB groups, LinkedIn groups, forums]
- Industry publications: [blogs, newsletters, podcasts]
- Events/conferences: [where they gather]
- Influencers: [who do they follow?]

## CONTENT ENGINE
**Content Pillars:**
1. [Topic #1 that resonates with pain]
2. [Topic #2 that demonstrates expertise]
3. [Topic #3 that builds trust]

**Platform Strategy:**
- Primary: [platform where target is most active]
- Secondary: [supporting platforms]
- Posting cadence: [frequency per week]

## ACQUISITION CHANNELS (RANKED)
### Free Channels
1. [Channel] - [why it works for this audience]
2. [Channel] - [tactics]
3. [Channel] - [tactics]

### Paid Channels (if needed later)
1. [Channel] - [Est. CAC]
2. [Channel] - [Est. CAC]

## INITIAL OUTREACH
Where to find first 10 customers:
- [Specific subreddit / forum / group]
- [Direct outreach strategy]
- [Partnership opportunities]

## VERDICT: [KILL or PROCEED]
- KILL if: Can't identify where customers are, no clear acquisition path
- PROCEED if: Clear channel strategy, reachable audience

Only PROCEED if we can actually reach these customers."""

    result = call_openai(prompt, max_tokens=5000)
    verdict = parse_verdict(result)
    print(f"   {verdict}", flush=True)
    return verdict, result

def stage8_final_synthesis(niche, pain, all_research):
    """Stage 8: Final Synthesis & Recommendation"""
    print(f"\n✅ STAGE 8: Final Synthesis...", flush=True)

    prompt = f"""Final assessment for:
TARGET: {niche}
PROBLEM: {pain}

ALL RESEARCH COMPLETED:
{all_research[:4000]}

YOUR TASK: Synthesize everything and make final recommendation.

FORMAT YOUR RESPONSE:

## EXECUTIVE SUMMARY
[2-3 paragraph summary of the opportunity]

## VALUE STATEMENT (Make it punchy!)
"I help [audience] solve [painful problem] so they can [outcome]."

**Quality Check:**
- ✅ Is it specific? (not vague)
- ✅ Is it emotional? (makes them feel the pain)
- ✅ Is it obvious? (they immediately get it)

If weak/vague → this idea isn't ready.
If punchy/emotional/obvious → you're in business.

## OPPORTUNITY SCORE (1-10)
- **Market Size:** [X/10]
- **Pain Intensity:** [X/10]
- **Competition:** [X/10]
- **Monetization:** [X/10]
- **Feasibility:** [X/10]
- **Overall:** [X/10]

## STRENGTHS
1. [Key strength #1]
2. [Key strength #2]
3. [Key strength #3]

## WEAKNESSES / CONCERNS
1. [Main concern #1]
2. [Main concern #2]
3. [Main concern #3]

## NEXT STEPS IF VIABLE
Concrete actions to move forward:
1. [Action #1 with timeline]
2. [Action #2 with timeline]
3. [Action #3 with timeline]

## PIVOTS TO CONSIDER (if challenges emerged)
Alternative angles or adjacent opportunities:
1. [Alternative #1]
2. [Alternative #2]

## FINAL VERDICT: [KILL or PROCEED TO STRATEGIST]
- KILL if: Overall score <6/10, fatal flaws, vague value statement
- PROCEED TO STRATEGIST if: Score 7+/10, clear value prop, viable path forward

BE RUTHLESS. Only PROCEED if this is a legitimate business opportunity."""

    result = call_openai(prompt, max_tokens=6000)
    verdict = parse_verdict(result)
    print(f"   {verdict}", flush=True)
    return verdict, result

def research_complete_opportunity(row_num, niche, pain):
    """Run COMPLETE Researcher framework (all 8 stages)"""
    print(f"\n{'='*70}", flush=True)
    print(f"🎯 DEEP RESEARCH #{row_num}: {niche}", flush=True)
    print(f"   Pain: {pain[:60]}...", flush=True)
    print(f"{'='*70}", flush=True)

    full_research = f"TARGET: {niche}\nPROBLEM: {pain}\n\n"

    # Stage 1: Find & Validate Problem
    v1, d1 = stage1_find_problem(niche, pain)
    full_research += f"\n{'='*70}\nSTAGE 1: PROBLEM VALIDATION\n{'='*70}\n{d1}\n"
    if v1 == "KILL":
        return "KILLED: Stage 1 (No proven problem)", full_research

    # Stage 2: Market Research
    v2, d2 = stage2_market_research(niche, pain, d1)
    full_research += f"\n{'='*70}\nSTAGE 2: MARKET RESEARCH\n{'='*70}\n{d2}\n"
    if v2 == "KILL":
        return "KILLED: Stage 2 (Market too small/declining)", full_research

    # Stage 3: Competitive Landscape
    v3, d3 = stage3_competitive_landscape(niche, pain)
    full_research += f"\n{'='*70}\nSTAGE 3: COMPETITIVE LANDSCAPE\n{'='*70}\n{d3}\n"
    if v3 == "KILL":
        return "KILLED: Stage 3 (Too competitive)", full_research

    # Stage 4: Pricing & Monetization
    v4, d4 = stage4_pricing_monetization(niche, pain, d2)
    full_research += f"\n{'='*70}\nSTAGE 4: PRICING & MONETIZATION\n{'='*70}\n{d4}\n"
    if v4 == "KILL":
        return "KILLED: Stage 4 (Can't monetize profitably)", full_research

    # Stage 5: Operations & Scalability
    v5, d5 = stage5_operations_scalability(niche, pain)
    full_research += f"\n{'='*70}\nSTAGE 5: OPERATIONS & SCALABILITY\n{'='*70}\n{d5}\n"
    if v5 == "KILL":
        return "KILLED: Stage 5 (Not feasible to build/scale)", full_research

    # Stage 6: Risks & Validation
    v6, d6 = stage6_risks_validation(niche, pain, full_research)
    full_research += f"\n{'='*70}\nSTAGE 6: RISK ASSESSMENT\n{'='*70}\n{d6}\n"
    if v6 == "KILL":
        return "KILLED: Stage 6 (Risks too high)", full_research

    # Stage 7: Customer Acquisition
    v7, d7 = stage7_customer_acquisition(niche, pain)
    full_research += f"\n{'='*70}\nSTAGE 7: CUSTOMER ACQUISITION\n{'='*70}\n{d7}\n"
    if v7 == "KILL":
        return "KILLED: Stage 7 (Can't reach customers)", full_research

    # Stage 8: Final Synthesis
    v8, d8 = stage8_final_synthesis(niche, pain, full_research)
    full_research += f"\n{'='*70}\nSTAGE 8: FINAL SYNTHESIS\n{'='*70}\n{d8}\n"
    if v8 == "KILL":
        return "KILLED: Stage 8 (Final verdict: Not viable)", full_research

    return "✅ VERIFIED - READY FOR STRATEGIST!", full_research

def main():
    """Process pending ideas with COMPLETE Researcher framework"""
    print("\n🚀 THE RESEARCHER v1.0 - Complete Framework", flush=True)
    print("="*70, flush=True)
    print("📋 8-Stage Deep Research Process", flush=True)
    print("🎯 Output: Complete reports ready for 'The Strategist'", flush=True)
    print("💀 Expected kill rate: 95%+ (only the best pass)", flush=True)
    print("="*70, flush=True)

    queue = sheet.worksheet("Ideas Queue")
    verified = sheet.worksheet("Verified Pains")
    winners = sheet.worksheet("Winners")

    all_rows = queue.get_all_values()

    if len(all_rows) <= 1:
        print("\n❌ No ideas in queue. Run: python generate_ideas_v4.py", flush=True)
        return

    processed = 0
    killed = 0
    winners_count = 0

    for i, row in enumerate(all_rows[1:], start=2):
        if len(row) < 4:
            continue

        status = row[3] if len(row) > 3 else ""
        if status != "Pending":
            continue

        row_num = row[0]
        niche = row[1]
        pain = row[2]

        result_status, full_report = research_complete_opportunity(row_num, niche, pain)

        processed += 1

        # Update Ideas Queue
        queue.update_cell(i, 4, result_status)

        if "KILLED" in result_status:
            killed += 1
            print(f"\n💀 {result_status}", flush=True)

            # Save partial research to Verified Pains for learning
            verified.append_row([
                row_num,
                niche,
                pain,
                result_status,
                full_report[:500],
                datetime.now().strftime("%Y-%m-%d")
            ])

        elif "READY FOR STRATEGIST" in result_status:
            # This is a WINNER - save complete report
            winners.append_row([
                row_num,
                niche,
                pain,
                "VERIFIED - Ready for Stage 2: The Strategist",
                full_report[:1500],  # Save more detail for winners
                datetime.now().strftime("%Y-%m-%d")
            ])
            winners_count += 1
            print(f"\n🏆 WINNER! Ready for The Strategist!", flush=True)

            # Also save full report to a file
            safe_niche = niche.replace(' ', '_').replace('/', '-')[:30]
            filename = f"research_report_{row_num}_{safe_niche}.txt"
            with open(filename, 'w') as f:
                f.write(full_report)
            print(f"   📄 Full report saved: {filename}", flush=True)

        print(f"\n📊 Progress: {processed} processed | {killed} killed | {winners_count} winners", flush=True)
        print(f"   Kill rate: {(killed/processed*100):.1f}%", flush=True)

    print(f"\n{'='*70}", flush=True)
    print(f"✅ Research complete!", flush=True)
    print(f"   Processed: {processed}", flush=True)
    print(f"   Killed: {killed} ({(killed/processed*100):.1f}%)", flush=True)
    print(f"   WINNERS (Ready for Strategist): {winners_count}", flush=True)
    print(f"{'='*70}\n", flush=True)

if __name__ == "__main__":
    main()
