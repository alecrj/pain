"""
Stages 2-7 for Ultimate Winner Machine v5.0
Separated for code organization
"""

import time
import json
from typing import Dict, List

# Import from main file will provide these
# call_openai, call_perplexity, web_search, load_founder_profile

# ═══════════════════════════════════════════════════════════
# STAGE 2: MULTI-SIGNAL EVIDENCE + MARKET SIZE
# ═══════════════════════════════════════════════════════════

def stage2_evidence_engine(idea: Dict, call_perplexity_fn, web_search_fn) -> Dict:
    """
    7 evidence signals + market size estimation
    Returns score and decision
    """
    print(f"\n{'─'*60}")
    print(f"STAGE 2: MULTI-SIGNAL EVIDENCE - Idea #{idea['id']}")
    print(f"{'─'*60}")

    total_score = 0
    signals_triggered = 0
    evidence = {}

    # SIGNAL 1: Search Volume
    print(f"\n   📊 Signal 1: Search Volume Analysis")
    search_queries = [
        f"{idea['business']} {idea['pain']} software",
        f"{idea['business']} {idea['pain']} tool",
        f"how to manage {idea['pain']}"
    ]

    prompt_sv = f"""Search Google Trends and estimate monthly search volume for:
{chr(10).join(['- ' + q for q in search_queries])}

Return JSON:
{{
  "total_monthly_searches": 0-10000,
  "trend": "rising"/"stable"/"declining",
  "score": 0-5
}}

Scoring:
- 500+ searches: 5 points
- 100-500: 3 points
- 10-100: 1 point
- <10: 0 points
"""

    sv_response = call_perplexity_fn(prompt_sv)
    try:
        sv_data = json.loads(sv_response) if sv_response else {}
        sv_score = sv_data.get("score", 0)
        total_score += sv_score
        if sv_score > 0:
            signals_triggered += 1
        evidence["search_volume"] = sv_data
        print(f"      ✅ Score: {sv_score}/5 ({sv_data.get('total_monthly_searches', 0)} searches/mo)")
    except:
        print(f"      ⚠️  Could not parse search volume")
        evidence["search_volume"] = {"score": 0}

    # SIGNAL 2: DIY Solution Demand
    print(f"\n   📝 Signal 2: DIY Solution Demand")
    diy_queries = [
        f"{idea['pain']} spreadsheet template",
        f"{idea['pain']} excel template",
        f"how to track {idea['pain']} in spreadsheet"
    ]

    prompt_diy = f"""Search for DIY solution demand:
{chr(10).join(['- ' + q for q in diy_queries])}

If people are searching for spreadsheet templates, it means no good software exists.

Return JSON:
{{
  "monthly_diy_searches": 0-10000,
  "top_results": ["...", "..."],
  "score": 0-5
}}

Scoring:
- 200+ searches: 5 points (GOLD)
- 50-200: 3 points
- 10-50: 1 point
"""

    diy_response = call_perplexity_fn(prompt_diy)
    try:
        diy_data = json.loads(diy_response) if diy_response else {}
        diy_score = diy_data.get("score", 0)
        total_score += diy_score
        if diy_score > 0:
            signals_triggered += 1
        evidence["diy_demand"] = diy_data
        print(f"      ✅ Score: {diy_score}/5 ({diy_data.get('monthly_diy_searches', 0)} DIY searches/mo)")
    except:
        print(f"      ⚠️  Could not parse DIY demand")
        evidence["diy_demand"] = {"score": 0}

    # SIGNAL 3: Job Posting Analysis
    print(f"\n   💼 Signal 3: Job Posting Analysis")
    prompt_jobs = f"""Search Indeed and LinkedIn for recent job postings mentioning:
Business type: {idea['business']}
Pain point keywords: {idea['pain'][:100]}

How many job descriptions mention this pain?
If companies are hiring to solve this problem, it's expensive enough to need staff.

Return JSON:
{{
  "jobs_found": 0-100,
  "sample_titles": ["...", "..."],
  "pain_mentions": 0-50,
  "score": 0-5
}}

Scoring:
- 20+ mentions: 5 points
- 10-20: 3 points
- 3-10: 2 points
"""

    jobs_response = call_perplexity_fn(prompt_jobs)
    try:
        jobs_data = json.loads(jobs_response) if jobs_response else {}
        jobs_score = jobs_data.get("score", 0)
        total_score += jobs_score
        if jobs_score > 0:
            signals_triggered += 1
        evidence["job_postings"] = jobs_data
        print(f"      ✅ Score: {jobs_score}/5 ({jobs_data.get('pain_mentions', 0)} mentions in jobs)")
    except:
        print(f"      ⚠️  Could not parse job data")
        evidence["job_postings"] = {"score": 0}

    # SIGNAL 4: Competitor Gap Mining
    print(f"\n   ⭐ Signal 4: Competitor Gap Mining")
    prompt_gaps = f"""Search G2, Capterra, GetApp for software used by: {idea['business']}

Find 1-star and 2-star reviews. How many mention this gap: {idea['pain'][:100]}

If existing tools DON'T solve this, it's white space.

Return JSON:
{{
  "tools_found": ["Tool A", "Tool B"],
  "reviews_mentioning_gap": 0-50,
  "sample_complaints": ["...", "..."],
  "score": 0-5
}}

Scoring:
- 5+ tools with 10+ gap mentions: 5 points
- 3-5 tools: 3 points
- 1-2 tools: 1 point
"""

    gaps_response = call_perplexity_fn(prompt_gaps)
    try:
        gaps_data = json.loads(gaps_response) if gaps_response else {}
        gaps_score = gaps_data.get("score", 0)
        total_score += gaps_score
        if gaps_score > 0:
            signals_triggered += 1
        evidence["competitor_gaps"] = gaps_data
        print(f"      ✅ Score: {gaps_score}/5 ({gaps_data.get('reviews_mentioning_gap', 0)} gap mentions)")
    except:
        print(f"      ⚠️  Could not parse competitor gaps")
        evidence["competitor_gaps"] = {"score": 0}

    # SIGNAL 5: Industry Forums
    print(f"\n   💬 Signal 5: Industry Forum Evidence")
    forums = {
        "contractor": ["contractortalk.com", "hvac-talk.com", "plumbingzone.com"],
        "logistics": ["truckerspath.com", "truckingboards.com"],
        "manufacturing": ["manufacturing.net forums", "industryforum.com"]
    }

    prompt_forums = f"""Search industry forums for discussions about:
{idea['pain'][:100]}

Find threads from 2024-2025 where {idea['business']} discuss this problem.

Return JSON:
{{
  "threads_found": 0-20,
  "sample_threads": [{{"title": "...", "date": "2024-XX", "replies": 0}}],
  "score": 0-4
}}

Scoring:
- 5+ threads: 4 points
- 3-5: 2 points
- 1-2: 1 point
"""

    forums_response = call_perplexity_fn(prompt_forums)
    try:
        forums_data = json.loads(forums_response) if forums_response else {}
        forums_score = forums_data.get("score", 0)
        total_score += forums_score
        if forums_score > 0:
            signals_triggered += 1
        evidence["forums"] = forums_data
        print(f"      ✅ Score: {forums_score}/4 ({forums_data.get('threads_found', 0)} forum threads)")
    except:
        print(f"      ⚠️  Could not parse forum data")
        evidence["forums"] = {"score": 0}

    # SIGNAL 6: Web Evidence
    print(f"\n   🌐 Signal 6: General Web Evidence")
    prompt_web = f"""Search for:
- Blog posts about: {idea['pain'][:100]}
- Industry articles mentioning cost
- LinkedIn posts from {idea['business']} owners complaining
- YouTube videos discussing this problem

Return JSON:
{{
  "sources_found": 0-20,
  "sample_sources": [{{"type": "blog", "title": "...", "url": "..."}}],
  "score": 0-4
}}

Scoring:
- 10+ sources: 4 points
- 5-10: 2 points
- 2-5: 1 point
"""

    web_response = call_perplexity_fn(prompt_web)
    try:
        web_data = json.loads(web_response) if web_response else {}
        web_score = web_data.get("score", 0)
        total_score += web_score
        if web_score > 0:
            signals_triggered += 1
        evidence["web_evidence"] = web_data
        print(f"      ✅ Score: {web_score}/4 ({web_data.get('sources_found', 0)} web sources)")
    except:
        print(f"      ⚠️  Could not parse web evidence")
        evidence["web_evidence"] = {"score": 0}

    # SIGNAL 7: Cost/ROI Research
    print(f"\n   💰 Signal 7: Cost/ROI Research")
    prompt_cost = f"""Find industry research about cost of: {idea['pain'][:100]}

For: {idea['business']}

Search for:
- Industry reports quantifying this cost
- Case studies showing losses
- Regulatory fine data
- Time-waste statistics

Return JSON:
{{
  "cost_estimates": ["$X per year from source Y"],
  "sources": ["..."],
  "has_third_party_validation": true/false,
  "score": 0-5
}}

Scoring:
- Industry report with $10k+ cost: 5 points
- Multiple anecdotal mentions: 3 points
- Single mention: 1 point
"""

    cost_response = call_perplexity_fn(prompt_cost)
    try:
        cost_data = json.loads(cost_response) if cost_response else {}
        cost_score = cost_data.get("score", 0)
        total_score += cost_score
        if cost_score > 0:
            signals_triggered += 1
        evidence["cost_research"] = cost_data
        print(f"      ✅ Score: {cost_score}/5 (third-party cost validation)")
    except:
        print(f"      ⚠️  Could not parse cost research")
        evidence["cost_research"] = {"score": 0}

    # SIGNAL 8: Market Size (NEW)
    print(f"\n   📈 Signal 8: Market Size Estimation")
    prompt_market = f"""Estimate market size for: {idea['business']}

1. How many {idea['business']} exist in US?
2. What % would need this solution?
3. Calculate TAM (Total Addressable Market)

Check: BLS data, industry associations, IBISWorld

Return JSON:
{{
  "total_businesses": 0-1000000,
  "addressable_percent": 0-100,
  "addressable_market": 0-1000000,
  "tam_estimate": "$X M",
  "score": 0-5
}}

Scoring:
- TAM > $50M: 5 points (venture-scale)
- TAM $10-50M: 3 points (good bootstrap)
- TAM $1-10M: 1 point (lifestyle only)
- TAM < $1M: 0 points (too small)
"""

    market_response = call_perplexity_fn(prompt_market)
    try:
        market_data = json.loads(market_response) if market_response else {}
        market_score = market_data.get("score", 0)
        # Market size is pass/fail, not added to score
        evidence["market_size"] = market_data
        print(f"      ✅ TAM: {market_data.get('tam_estimate', 'Unknown')} (Score: {market_score}/5)")
    except:
        print(f"      ⚠️  Could not parse market size")
        evidence["market_size"] = {"score": 0}
        market_score = 0

    # FINAL DECISION
    print(f"\n   📊 EVIDENCE SUMMARY:")
    print(f"      Total Score: {total_score}/33")
    print(f"      Signals Triggered: {signals_triggered}/7")
    print(f"      Market Size Score: {market_score}/5")

    # Pass criteria: score >= 12 AND signals >= 3 AND market_size >= 3 ($10M+ TAM)
    if total_score >= 12 and signals_triggered >= 3 and market_score >= 3:
        print(f"\n✅ PASS - Strong multi-signal evidence + viable market size")
        return {"verdict": "PASS", "score": total_score, "signals": signals_triggered, "evidence": evidence}
    else:
        reasons = []
        if total_score < 12:
            reasons.append(f"score too low ({total_score}/33)")
        if signals_triggered < 3:
            reasons.append(f"too few signals ({signals_triggered}/7)")
        if market_score < 3:
            reasons.append(f"market too small")

        print(f"\n❌ KILL - {', '.join(reasons)}")
        return {"verdict": "KILL", "score": total_score, "signals": signals_triggered, "evidence": evidence}


# ═══════════════════════════════════════════════════════════
# STAGE 3: BUILD FEASIBILITY (DIGITAL-ONLY)
# ═══════════════════════════════════════════════════════════

def stage3_build_feasibility(idea: Dict, call_openai_fn) -> Dict:
    """Enhanced build check with digital-only filter"""
    print(f"\n{'─'*60}")
    print(f"STAGE 3: BUILD FEASIBILITY (DIGITAL-ONLY) - Idea #{idea['id']}")
    print(f"{'─'*60}")

    prompt = f"""Analyze build feasibility for:

Business: {idea['business']}
Pain: {idea['pain']}

CRITICAL REQUIREMENTS (must pass ALL):

✅ DIGITAL-ONLY CHECK:
Can this be 100% delivered as web/mobile software?

❌ AUTO-KILL IF REQUIRES:
- Custom hardware (sensors, readers, kiosks, devices)
- On-premise installation (can't be cloud SaaS)
- Physical presence (technician visits, on-site setup)
- Custom manufacturing (labels, tags, physical goods)
- Specialized equipment beyond standard office gear

✅ ALLOWED:
- Web app, mobile app
- Public API integrations (Stripe, Twilio, Google Maps)
- User uploads (photos, PDFs, CSVs)
- Standard office equipment (printer, phone camera)

✅ PUBLIC API CHECK:
All integrations must have:
- Self-service signup (no sales call)
- Public documentation
- No enterprise-only features blocking MVP

❌ AUTO-KILL IF REQUIRES:
- SAP/Oracle/Salesforce enterprise APIs
- Manufacturer-specific APIs
- Government/regulatory APIs with restricted access
- Banking APIs requiring certifications (PCI-DSS Level 1)
- Healthcare APIs requiring HIPAA + BAA

✅ SOLO-FOUNDER BUILDABLE:
Can ONE technical founder build MVP in 3 months?

❌ AUTO-KILL IF REQUIRES:
- ML models (beyond basic APIs)
- Real-time video processing
- Blockchain infrastructure
- PhD-level algorithms
- Multi-sided marketplace

✅ NO CERTIFICATION REQUIRED:
Can launch MVP without:
- Professional licenses
- Industry certifications (ISO, SOC 2, HIPAA) for MVP
- Special permits

Return JSON:
{{
  "digital_only": true/false,
  "digital_reasoning": "...",
  "public_api_feasible": true/false,
  "apis_needed": ["Stripe", "Twilio", "..."],
  "solo_buildable": true/false,
  "build_complexity": "simple"/"moderate"/"complex",
  "no_certifications": true/false,
  "certification_blockers": [],
  "decision": "PASS"/"KILL",
  "reasoning": "..."
}}
"""

    response = call_openai_fn(prompt, model="gpt-5-mini", response_format="json")
    if not response:
        return {"verdict": "KILL", "reason": "API Error"}

    try:
        data = json.loads(response)

        all_checks_pass = (
            data.get("digital_only") and
            data.get("public_api_feasible") and
            data.get("solo_buildable") and
            data.get("no_certifications")
        )

        if all_checks_pass and data.get("decision") == "PASS":
            print(f"\n✅ PASS - Digital-only, solo-buildable, no certs required")
            return {"verdict": "PASS", "analysis": data}
        else:
            failed = []
            if not data.get("digital_only"):
                failed.append("requires hardware/physical")
            if not data.get("public_api_feasible"):
                failed.append("needs enterprise APIs")
            if not data.get("solo_buildable"):
                failed.append("too complex for solo")
            if not data.get("no_certifications"):
                failed.append("requires certifications")

            print(f"\n❌ KILL - {', '.join(failed)}")
            return {"verdict": "KILL", "analysis": data}
    except json.JSONDecodeError:
        return {"verdict": "KILL", "reason": "Parse error"}


# Continuing in next message - file getting long...

# ═══════════════════════════════════════════════════════════
# STAGE 4: COST CALCULATOR
# ═══════════════════════════════════════════════════════════

def stage4_cost_calculator(idea: Dict, call_perplexity_fn, call_openai_fn) -> Dict:
    """Calculate problem cost with real sources"""
    print(f"\n{'─'*60}")
    print(f"STAGE 4: COST CALCULATOR - Idea #{idea['id']}")
    print(f"{'─'*60}")

    # Search for cost evidence
    prompt_search = f"""Find evidence of costs/losses from:
{idea['pain']}

For: {idea['business']}

Search for:
1. Direct losses (revenue lost, fines, churn)
2. Labor waste (hours spent, hourly rates)
3. Opportunity cost (what they could do instead)
4. Industry reports with dollar amounts

Return specific dollar amounts and sources.
"""

    print(f"\n   🔍 Searching for cost evidence...")
    cost_evidence = call_perplexity_fn(prompt_search)

    # Calculate costs
    prompt_calc = f"""Calculate annual cost of this problem:

Business: {idea['business']}
Pain: {idea['pain']}

COST EVIDENCE FOUND:
{cost_evidence}

Calculate:
A) DIRECT LOSSES:
   - Lost revenue
   - Compliance fines
   - Customer churn
   - Rework costs

B) INDIRECT COSTS:
   - Time wasted (hours/week × hourly rate × 52)
   
C) OPPORTUNITY COST:
   - What they could do with freed time

Return JSON:
{{
  "direct_losses": 0-1000000,
  "indirect_costs": 0-1000000,
  "opportunity_cost": 0-1000000,
  "total_annual_cost": 0-1000000,
  "current_spend_on_solutions": 0-100000,
  "pricing_opportunity": 0-10000,
  "customer_roi": 0-1000000,
  "sources": ["..."],
  "decision": "PASS"/"KILL",
  "reasoning": "..."
}}

PASS if: total_annual_cost >= $10,000 with citable sources
KILL if: total_annual_cost < $10,000 OR no evidence
"""

    response = call_openai_fn(prompt_calc, model="gpt-5-mini", response_format="json")
    if not response:
        return {"verdict": "KILL", "reason": "API Error"}

    try:
        data = json.loads(response)
        total_cost = data.get("total_annual_cost", 0)

        if data.get("decision") == "PASS" and total_cost >= 10000:
            print(f"\n✅ PASS - Problem costs ${total_cost:,}/year")
            return {"verdict": "PASS", "analysis": data}
        else:
            print(f"\n❌ KILL - Cost too low (${total_cost:,}/year) or insufficient evidence")
            return {"verdict": "KILL", "analysis": data}
    except json.JSONDecodeError:
        return {"verdict": "KILL", "reason": "Parse error"}


# ═══════════════════════════════════════════════════════════
# STAGE 5: GTM FIT (DISTRIBUTION CHANNELS)
# ═══════════════════════════════════════════════════════════

def stage5_gtm_fit(idea: Dict, call_openai_fn) -> Dict:
    """Check if customers can be acquired digitally"""
    print(f"\n{'─'*60}")
    print(f"STAGE 5: GTM FIT (DISTRIBUTION) - Idea #{idea['id']}")
    print(f"{'─'*60}")

    prompt = f"""Design digital customer acquisition strategy:

Business: {idea['business']}
Pain: {idea['pain']}

FOUNDER CONSTRAINTS:
- NO phone sales / cold calling
- NO in-person demos / site visits
- Must be 100% digital acquisition

ALLOWED CHANNELS:
1. Google/SEO
2. Facebook/LinkedIn ads
3. Industry forums/communities
4. Content marketing (blog, YouTube)
5. Partnerships/integrations
6. Productized signup flow

For EACH channel, assess:

1. SEARCH (Google/SEO):
   - Do they search for solutions?
   - Can rank in 6 months?

2. PAID ADS:
   - Are they on Facebook/LinkedIn?
   - Estimated CPC?

3. COMMUNITIES:
   - Active online forums exist?
   - Can engage without selling?

4. CONTENT:
   - Would they consume blog/video?

5. PARTNERSHIPS:
   - What tools do they use?
   - Integration opportunities?

Return JSON:
{{
  "viable_channels": ["SEO", "LinkedIn ads", "..."],
  "cac_estimate": 0-1000,
  "time_to_first_10_customers_days": 0-180,
  "channel_details": {{
    "SEO": {{"viable": true, "reasoning": "..."}},
    "paid_ads": {{"viable": true, "cpc": 5}}
  }},
  "decision": "PASS"/"KILL",
  "reasoning": "..."
}}

PASS if: 2+ viable channels AND CAC < $500 AND time < 90 days
"""

    response = call_openai_fn(prompt, model="gpt-5-mini", response_format="json")
    if not response:
        return {"verdict": "KILL", "reason": "API Error"}

    try:
        data = json.loads(response)
        viable_channels = len(data.get("viable_channels", []))
        cac = data.get("cac_estimate", 1000)
        time_days = data.get("time_to_first_10_customers_days", 180)

        if viable_channels >= 2 and cac < 500 and time_days < 90:
            print(f"\n✅ PASS - {viable_channels} channels, ${cac} CAC, {time_days} days")
            return {"verdict": "PASS", "analysis": data}
        else:
            reasons = []
            if viable_channels < 2:
                reasons.append(f"only {viable_channels} channel(s)")
            if cac >= 500:
                reasons.append(f"CAC too high (${cac})")
            if time_days >= 90:
                reasons.append(f"takes {time_days} days")

            print(f"\n❌ KILL - {', '.join(reasons)}")
            return {"verdict": "KILL", "analysis": data}
    except json.JSONDecodeError:
        return {"verdict": "KILL", "reason": "Parse error"}


# ═══════════════════════════════════════════════════════════
# STAGE 6: FOUNDER FIT (AUTHENTICITY)
# ═══════════════════════════════════════════════════════════

def stage6_founder_fit(idea: Dict, founder_profile: Dict, call_openai_fn) -> Dict:
    """Check founder-market fit and authenticity"""
    print(f"\n{'─'*60}")
    print(f"STAGE 6: FOUNDER FIT (AUTHENTICITY) - Idea #{idea['id']}")
    print(f"{'─'*60}")

    prompt = f"""Founder-market fit analysis:

IDEA:
Business: {idea['business']}
Pain: {idea['pain']}

FOUNDER PROFILE:
Background: {founder_profile.get('background', 'Unknown')}
Skills: {', '.join(founder_profile.get('skills', []))}
Interests: {', '.join(founder_profile.get('interests', []))}
Network: {', '.join(founder_profile.get('network', []))}
Motivation: {', '.join(founder_profile.get('motivation', []))}

HARD CONSTRAINTS (must pass):
{json.dumps(founder_profile.get('constraints', {}), indent=2)}

ASSESSMENT:

1. DOMAIN KNOWLEDGE:
   Does founder have ANY connection to this industry?
   - Direct experience?
   - Personal network?
   - Genuine curiosity?

   HIGH FIT: Direct experience or strong connection
   MEDIUM FIT: Adjacent experience or genuine interest
   LOW FIT: Zero connection

2. CONTENT AUTHENTICITY:
   Can founder authentically create content?
   - Blog posts about this pain?
   - Forum engagement?
   - LinkedIn content?

   Must be able to speak authentically (lived it or deeply curious)

3. STAYING POWER:
   Will founder stick with this 12-18 months?

   Red flags:
   - "Just chasing market opportunity"
   - "Seems profitable but boring"
   - "Don't care about customer's world"

   Green flags:
   - "Genuinely curious"
   - "Would use this myself"
   - "Find industry interesting"

Return JSON:
{{
  "domain_fit": "HIGH"/"MEDIUM"/"LOW",
  "domain_reasoning": "...",
  "content_authenticity": "CAN"/"CANNOT",
  "content_reasoning": "...",
  "staying_power": "HIGH"/"MEDIUM"/"LOW",
  "staying_reasoning": "...",
  "hard_constraints_pass": true/false,
  "constraint_issues": [],
  "decision": "PASS"/"KILL",
  "reasoning": "..."
}}

PASS if: domain_fit >= MEDIUM AND content_authenticity = CAN AND hard_constraints_pass = true
"""

    response = call_openai_fn(prompt, model="gpt-5-mini", response_format="json")
    if not response:
        return {"verdict": "KILL", "reason": "API Error"}

    try:
        data = json.loads(response)
        domain_ok = data.get("domain_fit") in ["HIGH", "MEDIUM"]
        can_create_content = data.get("content_authenticity") == "CAN"
        constraints_ok = data.get("hard_constraints_pass", False)

        if domain_ok and can_create_content and constraints_ok:
            print(f"\n✅ PASS - {data.get('domain_fit')} domain fit, can create authentic content")
            return {"verdict": "PASS", "analysis": data}
        else:
            reasons = []
            if not domain_ok:
                reasons.append(f"weak domain fit ({data.get('domain_fit')})")
            if not can_create_content:
                reasons.append("can't create authentic content")
            if not constraints_ok:
                reasons.append("violates hard constraints")

            print(f"\n❌ KILL - {', '.join(reasons)}")
            return {"verdict": "KILL", "analysis": data}
    except json.JSONDecodeError:
        return {"verdict": "KILL", "reason": "Parse error"}


# ═══════════════════════════════════════════════════════════
# STAGE 7: VALIDATION PLAYBOOK
# ═══════════════════════════════════════════════════════════

def stage7_validation_playbook(idea: Dict, stage2_evidence: Dict) -> Dict:
    """Generate custom MVT validation playbook"""
    print(f"\n{'─'*60}")
    print(f"STAGE 7: VALIDATION PLAYBOOK - Idea #{idea['id']}")
    print(f"{'─'*60}")

    evidence = stage2_evidence.get("evidence", {})
    score = stage2_evidence.get("score", 0)

    playbook = f"""
{'='*80}
🎯 FINALIST #{idea['id']}: {idea['business']}
{'='*80}

PAIN POINT:
{idea['pain']}

{'='*80}
📊 EVIDENCE SUMMARY
{'='*80}

Total Evidence Score: {score}/33 {'🟢 STRONG' if score >= 20 else '🟡 MODERATE' if score >= 12 else '🔴 WEAK'}
Signals Triggered: {stage2_evidence.get('signals', 0)}/7

SIGNAL BREAKDOWN:
✓ Search Volume: {evidence.get('search_volume', {}).get('score', 0)}/5 ({evidence.get('search_volume', {}).get('total_monthly_searches', 0)} searches/mo)
✓ DIY Demand: {evidence.get('diy_demand', {}).get('score', 0)}/5 ({evidence.get('diy_demand', {}).get('monthly_diy_searches', 0)} template searches/mo)
✓ Job Postings: {evidence.get('job_postings', {}).get('score', 0)}/5 ({evidence.get('job_postings', {}).get('pain_mentions', 0)} mentions)
✓ Competitor Gaps: {evidence.get('competitor_gaps', {}).get('score', 0)}/5 ({evidence.get('competitor_gaps', {}).get('reviews_mentioning_gap', 0)} gap reviews)
✓ Forum Threads: {evidence.get('forums', {}).get('score', 0)}/4 ({evidence.get('forums', {}).get('threads_found', 0)} discussions)
✓ Web Evidence: {evidence.get('web_evidence', {}).get('score', 0)}/4 ({evidence.get('web_evidence', {}).get('sources_found', 0)} sources)
✓ Cost Research: {evidence.get('cost_research', {}).get('score', 0)}/5

Market Size: {evidence.get('market_size', {}).get('tam_estimate', 'Unknown')} TAM

{'='*80}
🎯 48-HOUR VALIDATION SPRINT
{'='*80}

DAY 1 - OUTREACH & RESEARCH (4 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TASK 1.1: LinkedIn Outreach (2 hours)
□ Search LinkedIn: "{idea['business']} operations manager" in [your city]
□ Find 15-20 people
□ Send DM template:

   "Hi [Name], quick question for someone in {idea['business']}:
   
   How do you currently handle {idea['pain'][:80]}?
   
   We're researching this challenge - would love 2 min of your insight."

□ Goal: Get 5 responses confirming pain is real
□ Success metric: 3+ say "this is painful" or "we use spreadsheets"

TASK 1.2: Forum Research (1 hour)
□ Join relevant forums:
  {', '.join(evidence.get('forums', {}).get('sample_threads', [{}])[:2])}
□ Read discussions about this pain
□ Reply to 2-3 threads asking: "What tool do you use for this?"
□ Goal: Confirm they use manual processes/no good solution

TASK 1.3: Facebook Group Poll (1 hour)
□ Find Facebook groups for {idea['business']}
□ Post poll: "How do you handle {idea['pain'][:60]}?"
   Options:
   A) We have a good tool
   B) We use spreadsheets (painful!)
   C) Manual processes only
   D) Not a problem for us
□ Goal: 20+ responses, >40% choose B or C

DAY 2 - COMPETITIVE ANALYSIS (2 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TASK 2.1: Competitor Demo (1 hour)
□ Sign up for free trials of:
  {', '.join(evidence.get('competitor_gaps', {}).get('tools_found', ['[no tools found]'])[:3])}
□ Check if they actually solve this pain
□ Note limitations and gaps
□ Goal: Confirm gap exists in existing tools

TASK 2.2: Review Deep Dive (1 hour)
□ Read 20 1-star reviews of top competitors
□ Count how many mention this specific pain
□ Extract exact quotes about what's missing
□ Goal: Find 5+ reviews mentioning this gap

DAY 2 - DEMAND TEST (Optional, $50)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TASK 2.3: Landing Page + Facebook Ad
□ Create simple landing page:
   Headline: "Stop [painful outcome from this problem]"
   Subhead: Brief description of solution
   CTA: "Join Waitlist" → Typeform

□ Typeform questions:
   1. How do you currently handle this?
   2. How much time/money does this cost you?
   3. What would you pay for a solution?
   4. Can we email you when ready?

□ Facebook Ad:
   Target: {idea['business']}, age 30-55, US
   Budget: $50, 3 days
   Goal: 10+ email signups = real demand

{'='*80}
📋 VALIDATION CHECKLIST
{'='*80}

Must get 3 out of 4 to proceed:

□ 5+ LinkedIn confirmations that pain is real → ✅ GO
□ Forum confirms pain + no good solution exists → ✅ GO
□ Competitor demos show clear gap → ✅ GO
□ 10+ landing page signups (if you run ad test) → ✅ STRONG GO

DECISION CRITERIA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Get 3-4 checkmarks → BUILD MVP
⚠️  Get 2 checkmarks → Do deeper research (1 more week)
❌ Get 0-1 checkmarks → KILL, move to next idea

{'='*80}
📈 NEXT STEPS IF VALIDATED
{'='*80}

If this passes validation:

WEEK 3-4: BUILD MVT (Minimum Viable Test)
- NOT the full product
- Simple landing page + Typeform + Zapier automation
- Tests willingness to pay
- Cost: $0-100, Time: 2 days

WEEK 5-6: MVT TESTING
- Email the 10 waitlist signups
- Offer: "We'll build custom solution for $200/mo, need 3 commits to proceed"
- Goal: Get 3+ paying commitments

WEEK 7-18: BUILD MVP (only if 3+ commitments)
- Now build the actual product
- Launch to your 3 committed customers
- Iterate based on feedback

{'='*80}
💰 ESTIMATED COSTS
{'='*80}

Validation Phase (Days 1-2): $50 (optional ad test)
MVT Phase (Week 3-6): $100 (domains, tools)
MVP Phase (Week 7-18): $500 (hosting, APIs, your time)

Total investment before knowing if it works: $150
Total investment before building product: $650

{'='*80}
⚠️  RISK ASSESSMENT
{'='*80}

Evidence Strength: {'🟢 LOW RISK' if score >= 20 else '🟡 MEDIUM RISK' if score >= 15 else '🔴 HIGH RISK'}

Validation Time: 2 days + 2 weeks = Total 16 days to know if real
Financial Risk: $50-150
Opportunity Cost: ~20 hours of your time

If this fails validation, you've lost 2 days and $50.
Better than spending 3 months building something nobody wants.

{'='*80}
"""

    print(playbook)

    return {
        "playbook": playbook,
        "validation_tasks": 6,
        "estimated_time_hours": 6,
        "estimated_cost": 50,
        "risk_level": "LOW" if score >= 20 else "MEDIUM" if score >= 15 else "HIGH"
    }

