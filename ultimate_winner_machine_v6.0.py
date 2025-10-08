#!/usr/bin/env python3
"""
ULTIMATE WINNER MACHINE v6.0 - THE SELF-IMPROVING ROI HUNTER

Philosophy: Mine 1000+ quantified pain points with ROI data, generate 100 ideas,
filter through 7 stages to find 8-10 validated candidates worth testing.

Key improvements over v5.0:
- Dynamic source discovery (no hardcoded forums)
- ROI-first pain mining (extract time/cost data)
- Economic proof validation (prove $5k-$10k/year value)
- Digital-only enforcement from start
- Higher quality input = higher pass rate

Expected output: 8-10 finalists with "$X/year waste" proof
Expected cost: ~$16 per 100 ideas
Expected time: ~100 minutes
"""

import os
import sys
import json
import time
import hashlib
import argparse
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from anthropic import Anthropic

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# API clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Perplexity client (uses OpenAI-compatible interface)
perplexity_client = None
if os.getenv("PERPLEXITY_API_KEY"):
    perplexity_client = OpenAI(
        api_key=os.getenv("PERPLEXITY_API_KEY"),
        base_url="https://api.perplexity.ai"
    )

# File paths
IDEAS_BANK_FILE = "ideas_bank.json"
FOUNDER_PROFILE_FILE = "founder_profile.json"

# Stage imports (reuse v5.0 stages 3-7)
from v5_stages_2_through_7 import (
    stage3_build_feasibility as v5_build,
    stage4_cost_calculator as v5_cost,
    stage5_gtm_fit as v5_gtm,
    stage6_founder_fit as v5_founder,
    stage7_validation_playbook as v5_playbook
)

# Wrapper functions to match v5.0 signatures
def stage3_build_feasibility(idea: Dict) -> Tuple[bool, str, Dict]:
    result = v5_build(idea, call_openai)
    # v5 returns {"verdict": "PASS/KILL", "analysis": {...}}
    passed = result.get("verdict") == "PASS"
    reason = "" if passed else result.get("analysis", {}).get("reasoning", "Failed build checks")
    return passed, reason, result

def stage4_cost_analysis(idea: Dict) -> Tuple[bool, str, Dict]:
    result = v5_cost(idea, call_perplexity, call_openai)
    return result.get("passed", False), result.get("reason", ""), result

def stage5_gtm_validation(idea: Dict) -> Tuple[bool, str, Dict]:
    result = v5_gtm(idea, call_openai)
    return result.get("passed", False), result.get("reason", ""), result

def stage6_founder_fit(idea: Dict, founder_profile: Dict) -> Tuple[bool, str, Dict]:
    result = v5_founder(idea, founder_profile, call_openai)
    return result.get("passed", False), result.get("reason", ""), result

def stage7_validation_playbook(idea: Dict) -> str:
    # v5 expects stage2_evidence dict, but we have it in idea already
    evidence = idea.get("stage2_evidence_analysis", {})
    return v5_playbook(idea, evidence)

# ═══════════════════════════════════════════════════════════
# API WRAPPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def call_perplexity(prompt: str) -> str:
    """Call Perplexity API for real-time web research"""
    if not perplexity_client:
        print("      ⚠️  Perplexity API not configured")
        return None

    time.sleep(1)
    try:
        response = perplexity_client.chat.completions.create(
            model="sonar",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"      ⚠️  Perplexity API error: {str(e)}")
        return None

def call_openai(prompt: str, system_message: str = "You are a business research expert.",
                model: str = "gpt-5-mini", response_format: str = None) -> str:
    """Call OpenAI API with rate limiting"""
    time.sleep(1)
    try:
        params = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        }

        if "gpt-5" in model.lower() or "o1" in model.lower():
            params["max_completion_tokens"] = 8000
        else:
            params["max_tokens"] = 8000
            params["temperature"] = 0.7

        if response_format == "json":
            params["response_format"] = {"type": "json_object"}

        response = openai_client.chat.completions.create(**params)
        return response.choices[0].message.content
    except Exception as e:
        print(f"      ⚠️  OpenAI API error: {str(e)}")
        return None

def call_claude(prompt: str, system_message: str = "You are a business idea specification expert.") -> str:
    """Call Claude API for idea specification"""
    time.sleep(1)
    try:
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            system=system_message,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"      ⚠️  Claude API error: {str(e)}")
        return None

def perplexity_to_json(perplexity_response: str, expected_schema: Dict, call_openai_fn) -> Dict:
    """Convert Perplexity's conversational response into structured JSON"""
    if not perplexity_response:
        return expected_schema

    prompt = f"""Convert this research response into JSON matching the schema.

RESEARCH RESPONSE:
{perplexity_response}

REQUIRED JSON SCHEMA:
{json.dumps(expected_schema, indent=2)}

Extract relevant information and return ONLY valid JSON matching the schema.
If data is missing, use reasonable defaults (0 for numbers, [] for arrays).
Return ONLY the JSON, no other text."""

    response = call_openai_fn(prompt, model="gpt-5-mini", response_format="json")
    try:
        return json.loads(response)
    except:
        return expected_schema

# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def load_founder_profile() -> Dict:
    """Load founder profile from JSON"""
    if os.path.exists(FOUNDER_PROFILE_FILE):
        with open(FOUNDER_PROFILE_FILE, 'r') as f:
            return json.load(f)
    return {}

def generate_idea_hash(business: str, pain: str) -> str:
    """Generate unique hash for business+pain combination"""
    combined = f"{business.lower().strip()}||{pain.lower().strip()}"
    return hashlib.md5(combined.encode()).hexdigest()[:12]

def load_ideas_bank() -> List[Dict]:
    """Load existing ideas bank"""
    if os.path.exists(IDEAS_BANK_FILE):
        with open(IDEAS_BANK_FILE, 'r') as f:
            data = json.load(f)
            return data.get("ideas", []) if isinstance(data, dict) else data
    return []

def save_ideas_bank(ideas: List[Dict]):
    """Save ideas bank"""
    with open(IDEAS_BANK_FILE, 'w') as f:
        json.dump({"ideas": ideas}, f, indent=2)

def idea_exists(ideas_bank: List[Dict], business: str, pain: str) -> bool:
    """Check if idea already exists"""
    idea_hash = generate_idea_hash(business, pain)
    return any(idea.get("hash") == idea_hash for idea in ideas_bank)

# ═══════════════════════════════════════════════════════════
# STAGE 0A-META: DYNAMIC SOURCE DISCOVERY
# ═══════════════════════════════════════════════════════════

def stage0a_meta_source_discovery() -> List[str]:
    """
    Dynamically discover 100+ online communities where B2B operators complain about pain points.
    No hardcoding - system finds sources itself.

    Returns: List of 100-200 source URLs/communities
    """
    print("\n" + "="*80)
    print("STAGE 0A-META: DYNAMIC SOURCE DISCOVERY")
    print("="*80)
    print("\n🔍 Discovering online communities where B2B operators complain...")

    sources = []

    # Query 1: Industry forums
    print("\n   Finding industry-specific forums...")
    forums_prompt = """Find 30 active online forums and communities where small-to-mid-sized business owners ($2M-$50M revenue) discuss operational problems, software gaps, and workflow frustrations.

Focus on:
- Construction/contractor forums
- Logistics/trucking forums
- Manufacturing forums
- Distribution/wholesale forums
- Professional services forums
- Field service forums

For each, provide:
- Forum name
- URL (if available)
- Primary industry
- Activity level (high/medium/low)

Return as JSON array: [{name, url, industry, activity}]"""

    forums_response = call_perplexity(forums_prompt)
    if forums_response:
        forums_data = perplexity_to_json(forums_response, {"forums": []}, call_openai)
        for forum in forums_data.get("forums", [])[:30]:
            sources.append({
                "type": "forum",
                "name": forum.get("name", "Unknown"),
                "url": forum.get("url", ""),
                "industry": forum.get("industry", "General")
            })

    # Query 2: Reddit communities
    print("   Finding relevant subreddits...")
    reddit_prompt = """Find 25 active subreddits where B2B business owners discuss operational challenges, manual processes, and software needs.

Look for subreddits about:
- Small business operations
- Specific industries (construction, logistics, manufacturing, etc.)
- Entrepreneurship and scaling
- Software recommendations
- Workflow automation

Return as JSON array: [{subreddit, description, subscriber_count}]"""

    reddit_response = call_perplexity(reddit_prompt)
    if reddit_response:
        reddit_data = perplexity_to_json(reddit_response, {"subreddits": []}, call_openai)
        for sub in reddit_data.get("subreddits", [])[:25]:
            sources.append({
                "type": "reddit",
                "name": sub.get("subreddit", "Unknown"),
                "url": f"https://reddit.com/{sub.get('subreddit', '')}",
                "industry": "General"
            })

    # Query 3: Review sites for competitor gaps
    print("   Finding software review sites...")
    reviews_prompt = """List 20 software categories on G2, Capterra, and Software Advice where B2B operational tools are reviewed (field service, logistics, contractor management, inventory, scheduling, etc.).

Return as JSON array: [{category, platform, review_count}]"""

    reviews_response = call_perplexity(reviews_prompt)
    if reviews_response:
        reviews_data = perplexity_to_json(reviews_response, {"categories": []}, call_openai)
        for cat in reviews_data.get("categories", [])[:20]:
            sources.append({
                "type": "reviews",
                "name": f"{cat.get('category', 'Unknown')} reviews",
                "url": cat.get("platform", "G2"),
                "industry": cat.get("category", "General")
            })

    # Query 4: Job boards for pain signals
    print("   Identifying job titles that signal operational pains...")
    jobs_prompt = """List 25 job titles in B2B operations roles where job descriptions reveal pain points (operations manager, dispatcher, inventory coordinator, service coordinator, etc.).

Return as JSON array: [{job_title, common_responsibilities, pain_signals}]"""

    jobs_response = call_perplexity(jobs_prompt)
    if jobs_response:
        jobs_data = perplexity_to_json(jobs_response, {"job_titles": []}, call_openai)
        for job in jobs_data.get("job_titles", [])[:25]:
            sources.append({
                "type": "jobs",
                "name": job.get("job_title", "Unknown"),
                "url": "job_boards",
                "industry": "Operations"
            })

    print(f"\n✅ Discovered {len(sources)} sources dynamically")
    return sources

# ═══════════════════════════════════════════════════════════
# STAGE 0B-DEEP: ROI-FOCUSED PAIN MINING
# ═══════════════════════════════════════════════════════════

def stage0b_deep_pain_mining(sources: List[Dict]) -> List[Dict]:
    """
    Mine each source for quantified pain points (time/cost data required).
    Only keep complaints that mention specific time waste or cost.

    Returns: List of 800-1500 quantified complaints
    """
    print("\n" + "="*80)
    print("STAGE 0B-DEEP: ROI-FOCUSED PAIN MINING")
    print("="*80)
    print(f"\n💎 Mining {len(sources)} sources for quantified pain points...")
    print("   (Only keeping complaints with time/cost data)\n")

    quantified_pains = []

    for idx, source in enumerate(sources[:100], 1):  # Limit to 100 sources for now
        source_type = source.get("type", "unknown")
        source_name = source.get("name", "Unknown")

        if idx % 10 == 0:
            print(f"   Progress: {idx}/100 sources mined...")

        if source_type == "forum":
            prompt = f"""Search {source_name} forum for posts where people complain about operational problems and QUANTIFY the time or cost impact.

Look for phrases like:
- "I waste X hours per week on..."
- "This costs us $Y per year"
- "My team spends Z hours doing..."
- "We have N people doing this manually"
- "Takes X hours every day/week/month"

For each quantified complaint, extract:
1. Exact pain point (specific, not generic)
2. Time quantification (hours/day, hours/week, etc.)
3. Cost quantification (if mentioned)
4. Frequency (daily, weekly, monthly)
5. Business type/industry
6. Current workaround (Excel, email, paper, phone calls)

ONLY include complaints with time OR cost data.
Return JSON: {{complaints: [{{pain, time_waste, cost_waste, frequency, business_type, workaround}}]}}"""

        elif source_type == "reddit":
            prompt = f"""Search {source_name} for posts about operational pain points where people QUANTIFY time or money wasted.

Look for:
- "We waste X hours on..."
- "Costs us $Y annually"
- "My entire day is spent..."
- "Team of N people doing X manually"

Extract same data as forum prompt above.
Return JSON: {{complaints: [{{pain, time_waste, cost_waste, frequency, business_type, workaround}}]}}"""

        elif source_type == "reviews":
            prompt = f"""Find 1-2 star reviews in {source_name} category where reviewers complain about missing features or things they still have to do manually.

Look for time/cost impact mentions.
Extract same data format.
Return JSON: {{complaints: [{{pain, time_waste, cost_waste, frequency, business_type, workaround}}]}}"""

        elif source_type == "jobs":
            prompt = f"""Find recent job postings for '{source_name}' and extract the painful responsibilities they list.

Look for duties like:
- "Manually track/update/coordinate..."
- "Spend X hours per week on..."
- "Responsible for managing [tedious process]"

Extract same data format.
Return JSON: {{complaints: [{{pain, time_waste, cost_waste, frequency, business_type, workaround}}]}}"""

        else:
            continue

        response = call_perplexity(prompt)
        if response:
            data = perplexity_to_json(response, {"complaints": []}, call_openai)
            complaints = data.get("complaints", [])

            # Only keep complaints with time or cost data
            for complaint in complaints:
                if complaint.get("time_waste") or complaint.get("cost_waste"):
                    complaint["source"] = source_name
                    complaint["source_type"] = source_type
                    quantified_pains.append(complaint)

    print(f"\n✅ Extracted {len(quantified_pains)} quantified pain points (with time/cost data)")
    return quantified_pains

# ═══════════════════════════════════════════════════════════
# STAGE 0C: ROI-BASED CLUSTERING
# ═══════════════════════════════════════════════════════════

def stage0c_roi_clustering(quantified_pains: List[Dict]) -> List[Dict]:
    """
    Cluster pain points by similarity and rank by economic impact.

    Returns: Top 50 pain clusters ranked by (mentions × avg_cost × market_potential)
    """
    print("\n" + "="*80)
    print("STAGE 0C: ROI-BASED CLUSTERING")
    print("="*80)
    print(f"\n🧮 Clustering {len(quantified_pains)} pain points by economic impact...\n")

    # Prepare data for clustering
    pains_json = json.dumps(quantified_pains[:500], indent=2)  # Limit to 500 for prompt size

    prompt = f"""Analyze these {len(quantified_pains)} quantified pain points and cluster them by similarity.

DATA (first 500 complaints):
{pains_json}

CLUSTERING TASK:
Group similar pain points together (similar workflow, similar industry, similar time waste).

For each cluster, calculate:
1. Pain category name (specific, e.g., "Manually scheduling field techs across time zones")
2. Number of mentions
3. Average time waste (hours/week per person)
4. Average cost estimate ($/year per business) - calculate from time if not stated
5. Industries affected
6. Current workarounds mentioned
7. Why it persists (complexity, cost, no good solution)
8. Estimated market size (# of businesses with this exact problem)

RANKING:
Rank clusters by: (# mentions) × (avg annual cost) × (market size estimate / 1000)

Return top 50 clusters as JSON:
{{
  "clusters": [
    {{
      "pain_category": "...",
      "mention_count": 0,
      "avg_time_waste_hours_per_week": 0,
      "avg_annual_cost_per_business": 0,
      "industries": [],
      "current_workarounds": [],
      "why_persists": "...",
      "estimated_market_size": 0,
      "rank_score": 0,
      "sample_quotes": []
    }}
  ]
}}"""

    print("   🤖 Using GPT-4o to cluster and rank by ROI (this takes ~2-3 minutes)...\n")
    response = call_openai(prompt, model="gpt-4o", response_format="json")

    if response:
        try:
            data = json.loads(response)
            clusters = data.get("clusters", [])

            # Sort by rank_score descending
            clusters = sorted(clusters, key=lambda x: x.get("rank_score", 0), reverse=True)

            print(f"✅ Created {len(clusters)} pain clusters, ranked by economic impact\n")

            if len(clusters) == 0:
                print("⚠️  WARNING: GPT-4o returned 0 clusters. Response may have been truncated.")
                print(f"   Response preview: {response[:500]}...")
                print("\n   Falling back to simple grouping by business_type...\n")

                # Fallback: Simple grouping by business_type
                business_groups = {}
                for pain in quantified_pains:
                    biz_type = pain.get("business_type", "Unknown Business")
                    if biz_type not in business_groups:
                        business_groups[biz_type] = []
                    business_groups[biz_type].append(pain)

                # Convert to clusters
                clusters = []
                for biz_type, pains in business_groups.items():
                    cluster = {
                        "pain_category": f"{biz_type} - {pains[0].get('pain', 'Unknown pain')[:60]}",
                        "mention_count": len(pains),
                        "avg_time_waste_hours_per_week": 5.0,  # Default estimate
                        "avg_annual_cost_per_business": 10000,  # Default estimate
                        "industries": [biz_type],
                        "current_workarounds": [p.get("workaround", "") for p in pains if p.get("workaround")],
                        "why_persists": "No good solution exists",
                        "estimated_market_size": 1000,
                        "rank_score": len(pains) * 10000,
                        "sample_quotes": [p.get("pain", "") for p in pains[:3]]
                    }
                    clusters.append(cluster)

                clusters = sorted(clusters, key=lambda x: x.get("rank_score", 0), reverse=True)[:50]
                print(f"✅ Created {len(clusters)} fallback clusters\n")

            # Show top 5
            print("   🏆 TOP 5 CLUSTERS BY ROI:\n")
            for i, cluster in enumerate(clusters[:5], 1):
                print(f"   {i}. {cluster.get('pain_category', 'Unknown')}")
                print(f"      • {cluster.get('mention_count', 0)} mentions")
                print(f"      • ${cluster.get('avg_annual_cost_per_business', 0):,}/year per business")
                print(f"      • {cluster.get('estimated_market_size', 0):,} potential customers")
                print(f"      • Industries: {', '.join(cluster.get('industries', [])[:3])}")
                print()

            return clusters[:50]  # Return top 50

        except json.JSONDecodeError as e:
            print(f"⚠️  ERROR: Failed to parse GPT-4o response: {e}")
            print(f"   Response: {response[:500]}...")
            return []

    return []

# ═══════════════════════════════════════════════════════════
# STAGE 0D: ROI-JUSTIFIED IDEA GENERATION
# ═══════════════════════════════════════════════════════════

def stage0d_idea_generation(pain_clusters: List[Dict], target_count: int) -> List[Dict]:
    """
    Generate specific ideas from pain clusters with ROI justification.
    Each idea must include time/cost waste statement.
    Digital-only filter enforced here.

    Returns: List of ideas with embedded ROI data
    """
    print("\n" + "="*80)
    print(f"STAGE 0D: ROI-JUSTIFIED IDEA GENERATION")
    print("="*80)
    print(f"\n📝 Generating {target_count} specific ideas from top pain clusters...\n")

    if len(pain_clusters) == 0:
        print("⚠️  ERROR: No pain clusters available. Cannot generate ideas.")
        print("   This likely means Stage 0C clustering failed or returned 0 results.\n")
        return []

    founder_profile = load_founder_profile()
    ideas = []
    ideas_per_cluster = max(2, target_count // len(pain_clusters[:25]))  # Use top 25 clusters

    for idx, cluster in enumerate(pain_clusters[:25], 1):
        if len(ideas) >= target_count:
            break

        print(f"   Generating from cluster {idx}/25: {cluster.get('pain_category', 'Unknown')[:60]}...")

        prompt = f"""Based on this pain point cluster, create {ideas_per_cluster} specific business ideas.

PAIN CLUSTER DATA:
- Pain: {cluster.get('pain_category')}
- Avg time waste: {cluster.get('avg_time_waste_hours_per_week', 0)} hours/week
- Avg cost: ${cluster.get('avg_annual_cost_per_business', 0)}/year
- Industries: {', '.join(cluster.get('industries', []))}
- Current workarounds: {', '.join(cluster.get('current_workarounds', []))}
- Why persists: {cluster.get('why_persists')}
- Market size: {cluster.get('estimated_market_size', 0)} businesses

FOUNDER CONSTRAINTS:
{json.dumps(founder_profile.get('constraints', {}), indent=2)}

REQUIREMENTS:
1. MUST be 100% digital (pure software, no hardware, no IoT, no tablets)
2. MUST be buildable in 3 months or less
3. MUST NOT require certifications (SOC2, HIPAA, PCI, etc.)
4. MUST NOT require enterprise APIs (SAP, Oracle, ServiceTitan, etc.)
5. MUST NOT require on-premise deployment
6. MUST be solo-founder feasible
7. Target customer: $5M-$50M revenue B2B businesses

For each idea, return JSON:
{{
  "ideas": [
    {{
      "business": "Specific business type (size, revenue, industry)",
      "pain": "Specific pain point (detailed, not generic)",
      "roi_statement": "You're wasting $X/year on Y, leading to Z",
      "current_annual_cost": 0,
      "time_waste_description": "X hours/day doing Y",
      "frequency": "daily/weekly/monthly",
      "current_workaround": "Excel/email/paper/phone",
      "why_persists": "Why no one has solved this well",
      "digital_solution_overview": "3-5 core features needed",
      "buildable_3_months": true,
      "no_hardware_required": true,
      "no_certifications_required": true,
      "solo_founder_feasible": true,
      "public_apis_only": true,
      "estimated_tam": 0,
      "evidence_preview": {{
        "forum_mentions": 0,
        "job_postings": 0,
        "reddit_threads": 0
      }}
    }}
  ]
}}

ONLY return ideas that pass ALL 7 requirements above."""

        response = call_claude(prompt)
        if response:
            try:
                # Extract JSON from response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    data = json.loads(json_str)

                    for idea in data.get("ideas", []):
                        # Validate digital-only constraints
                        if (idea.get("no_hardware_required") and
                            idea.get("no_certifications_required") and
                            idea.get("buildable_3_months") and
                            idea.get("solo_founder_feasible") and
                            idea.get("public_apis_only")):

                            ideas.append(idea)
                            print(f"      ✅ {idea.get('business', 'Unknown')[:50]}...")
                        else:
                            print(f"      ⚠️  Skipped (fails digital-only filter)")
            except Exception as e:
                print(f"      ⚠️  Parse error: {str(e)}")

    print(f"\n✅ Generated {len(ideas)} ROI-justified, digital-only ideas")
    return ideas[:target_count]

# ═══════════════════════════════════════════════════════════
# STAGE 1: WHITE SPACE + SWITCHING COST (from v5.0)
# ═══════════════════════════════════════════════════════════

def stage1_white_space(idea: Dict) -> Tuple[bool, str, Dict]:
    """Check for white space and switching costs (reused from v5.0)"""
    print(f"\n{'─'*60}")
    print(f"STAGE 1: WHITE SPACE + SWITCHING COST - Idea #{idea['id']}")
    print(f"Business: {idea['business']}")
    print(f"Pain: {idea['pain'][:80]}...")
    print(f"{'─'*60}\n")

    # Check for dominant player
    prompt_ws = f"""Is there a dominant software platform (>20% market share) that already solves this problem well?

Business: {idea['business']}
Pain: {idea['pain']}

Check for:
1. Major SaaS platforms (Salesforce, ServiceTitan, Toast, etc.)
2. Category leaders with strong market position
3. Well-funded startups that recently raised >$20M

Return JSON:
{{
  "market_type": "SATURATED" | "COMPETITIVE" | "WHITE_SPACE",
  "dominant_players": ["Player 1", "Player 2"],
  "market_share_leader": "Company name or None",
  "recent_funding": "Any >$20M raises in last 12 months?",
  "reasoning": "Why this classification"
}}"""

    ws_response = call_perplexity(prompt_ws)
    ws_data = perplexity_to_json(ws_response, {
        "market_type": "WHITE_SPACE",
        "dominant_players": [],
        "reasoning": ""
    }, call_openai) if ws_response else {"market_type": "WHITE_SPACE", "dominant_players": []}

    market_type = ws_data.get("market_type", "WHITE_SPACE")

    if market_type == "SATURATED":
        return False, f"SATURATED market - dominant player exists: {ws_data.get('market_share_leader')}", ws_data

    # Check switching costs
    prompt_sc = f"""Would customers switching from their current solution to a new tool face HIGH switching costs?

Business: {idea['business']}
Pain: {idea['pain']}
Current solutions: {', '.join(ws_data.get('dominant_players', ['None']))}

HIGH switching cost indicators:
- Multi-year contracts
- Deep integrations with core systems
- Extensive employee training required
- Data migration complexity
- Mission-critical dependency

Return JSON:
{{
  "switching_cost": "HIGH" | "MEDIUM" | "LOW",
  "reasons": ["reason 1", "reason 2"],
  "defensibility_moat": "What makes current solutions sticky?"
}}"""

    sc_response = call_perplexity(prompt_sc)
    sc_data = perplexity_to_json(sc_response, {
        "switching_cost": "LOW",
        "reasons": []
    }, call_openai) if sc_response else {"switching_cost": "LOW"}

    switching_cost = sc_data.get("switching_cost", "LOW")

    if switching_cost == "HIGH":
        return False, f"HIGH switching costs - hard to displace: {sc_data.get('defensibility_moat')}", {**ws_data, **sc_data}

    print(f"✅ PASS - {market_type} market, {switching_cost} switching cost")
    return True, "", {**ws_data, **sc_data}

# ═══════════════════════════════════════════════════════════
# STAGE 2: ENHANCED ECONOMIC PROOF VALIDATION
# ═══════════════════════════════════════════════════════════

def stage2_economic_proof(idea: Dict) -> Tuple[bool, str, Dict]:
    """
    Enhanced validation focused on economic proof.
    Must prove >$5k/year value with evidence.

    8 signals (max 39 points):
    1. Time Waste Evidence (0-5)
    2. Willingness to Pay Evidence (0-5)
    3. Current Cost Validation (0-5)
    4. Job Posting Demand (0-5)
    5. DIY Solution Evidence (0-5)
    6. Competitor Gap Mining (0-5)
    7. Market Size Validation (0-5)
    8. Frequency Validation (0-4)

    Pass criteria: ≥25/39 AND ≥6/8 signals triggered
    """
    print(f"\n{'─'*60}")
    print(f"STAGE 2: ECONOMIC PROOF VALIDATION - Idea #{idea['id']}")
    print(f"{'─'*60}\n")

    evidence = {}
    total_score = 0
    signals_triggered = 0

    # SIGNAL 1: Time Waste Evidence
    print("   📊 Signal 1: Time Waste Evidence")
    prompt_time = f"""Find 10+ forum posts, Reddit threads, or job postings where people mention SPECIFIC time spent on this pain point.

Business: {idea['business']}
Pain: {idea['pain']}

Look for:
- "Takes X hours per day/week"
- "I waste X hours on..."
- "Team spends X hours doing..."

Must find time quantification (not just "annoying").
Return JSON:
{{
  "mentions": [
    {{"source": "forum/reddit/jobs", "quote": "exact quote", "time_stated": "X hours/week"}}
  ],
  "score": 0-5  // 0=no mentions, 5=10+ quantified mentions
}}"""

    time_response = call_perplexity(prompt_time)
    time_data = perplexity_to_json(time_response, {
        "mentions": [],
        "score": 0
    }, call_openai) if time_response else {"mentions": [], "score": 0}

    time_score = time_data.get("score", 0)
    total_score += time_score
    if time_score > 0:
        signals_triggered += 1
    evidence["time_waste_evidence"] = time_data
    print(f"      ✅ Score: {time_score}/5 ({len(time_data.get('mentions', []))} quantified mentions)")

    # SIGNAL 2: Willingness to Pay Evidence
    print("\n   💰 Signal 2: Willingness to Pay Evidence")
    prompt_wtp = f"""Find discussions where people express willingness to pay for a solution or mention budget for this problem.

Business: {idea['business']}
Pain: {idea['pain']}

Look for:
- "I'd pay for..."
- "We budget $X for..."
- "Looking for software to..."
- "Need a tool that..."

Return JSON:
{{
  "mentions": [
    {{"source": "...", "quote": "...", "budget_mentioned": "$X or none"}}
  ],
  "score": 0-5
}}"""

    wtp_response = call_perplexity(prompt_wtp)
    wtp_data = perplexity_to_json(wtp_response, {
        "mentions": [],
        "score": 0
    }, call_openai) if wtp_response else {"mentions": [], "score": 0}

    wtp_score = wtp_data.get("score", 0)
    total_score += wtp_score
    if wtp_score > 0:
        signals_triggered += 1
    evidence["willingness_to_pay"] = wtp_data
    print(f"      ✅ Score: {wtp_score}/5 ({len(wtp_data.get('mentions', []))} mentions)")

    # SIGNAL 3: Current Cost Validation
    print("\n   🧮 Signal 3: Current Cost Calculation & Validation")
    time_waste = idea.get("time_waste_description", "Unknown")
    annual_cost = idea.get("current_annual_cost", 0)

    prompt_cost = f"""Calculate and validate the annual cost of this manual process.

Business: {idea['business']}
Pain: {idea['pain']}
Stated time waste: {time_waste}
Stated annual cost: ${annual_cost}

Calculate from first principles:
- Time waste per week: X hours
- Hourly rate for role doing this: $Y (research typical rate)
- Number of people affected per business: N
- Annual cost = X × Y × N × 52 weeks

Then find external sources validating this cost range.

Return JSON:
{{
  "calculated_annual_cost": 0,
  "validation_sources": ["source 1", "source 2"],
  "cost_breakdown": {{"time_per_week": 0, "hourly_rate": 0, "people_count": 0}},
  "score": 0-5  // 0=<$2k/year, 5=>$10k/year validated
}}"""

    cost_response = call_perplexity(prompt_cost)
    cost_data = perplexity_to_json(cost_response, {
        "calculated_annual_cost": 0,
        "validation_sources": [],
        "score": 0
    }, call_openai) if cost_response else {"calculated_annual_cost": 0, "score": 0}

    cost_score = cost_data.get("score", 0)
    total_score += cost_score
    if cost_score > 0:
        signals_triggered += 1
    evidence["cost_validation"] = cost_data
    print(f"      ✅ Score: {cost_score}/5 (${cost_data.get('calculated_annual_cost', 0):,}/year validated)")

    # SIGNAL 4: Job Posting Demand
    print("\n   💼 Signal 4: Job Posting Analysis")
    prompt_jobs = f"""Find job postings where this pain point appears as a responsibility or requirement.

Business type: {idea['business']}
Pain: {idea['pain']}

Look for:
- Job postings mentioning this task
- Responsibilities related to this problem
- Experience with tools for this problem

High score = companies hiring people to do this manually.

Return JSON:
{{
  "job_postings_found": 0,
  "sample_jobs": [{{"title": "...", "responsibility": "...", "company_size": "..."}}],
  "score": 0-5
}}"""

    jobs_response = call_perplexity(prompt_jobs)
    jobs_data = perplexity_to_json(jobs_response, {
        "job_postings_found": 0,
        "sample_jobs": [],
        "score": 0
    }, call_openai) if jobs_response else {"job_postings_found": 0, "score": 0}

    jobs_score = jobs_data.get("score", 0)
    total_score += jobs_score
    if jobs_score > 0:
        signals_triggered += 1
    evidence["job_demand"] = jobs_data
    print(f"      ✅ Score: {jobs_score}/5 ({jobs_data.get('job_postings_found', 0)} job postings)")

    # SIGNAL 5: DIY Solution Evidence
    print("\n   🔧 Signal 5: DIY Solution Evidence")
    prompt_diy = f"""Find evidence of homegrown/DIY solutions for this problem.

Business: {idea['business']}
Pain: {idea['pain']}

Look for:
- Excel templates
- Google Sheets shared in forums
- "Here's my workaround..."
- "I built a script to..."
- Custom internal tools

DIY solutions prove: (1) no good tool exists, (2) people care enough to hack it.

Return JSON:
{{
  "diy_solutions_found": 0,
  "sample_solutions": [{{"type": "Excel/Script/etc", "description": "...", "source": "..."}}],
  "score": 0-5
}}"""

    diy_response = call_perplexity(prompt_diy)
    diy_data = perplexity_to_json(diy_response, {
        "diy_solutions_found": 0,
        "sample_solutions": [],
        "score": 0
    }, call_openai) if diy_response else {"diy_solutions_found": 0, "score": 0}

    diy_score = diy_data.get("score", 0)
    total_score += diy_score
    if diy_score > 0:
        signals_triggered += 1
    evidence["diy_solutions"] = diy_data
    print(f"      ✅ Score: {diy_score}/5 ({diy_data.get('diy_solutions_found', 0)} DIY solutions)")

    # SIGNAL 6: Competitor Gap Mining
    print("\n   ⭐ Signal 6: Competitor Gap Analysis")
    prompt_gaps = f"""Find reviews of related software where users complain this specific pain point isn't solved.

Pain: {idea['pain']}
Related categories: field service, operations, scheduling, workflow automation

Look for 1-2 star reviews mentioning:
- "Doesn't handle X"
- "Still have to do Y manually"
- "Wish it had..."
- Missing features

Return JSON:
{{
  "competitor_gaps_found": 0,
  "sample_complaints": [{{"software": "...", "complaint": "...", "rating": 0}}],
  "score": 0-5
}}"""

    gaps_response = call_perplexity(prompt_gaps)
    gaps_data = perplexity_to_json(gaps_response, {
        "competitor_gaps_found": 0,
        "sample_complaints": [],
        "score": 0
    }, call_openai) if gaps_response else {"competitor_gaps_found": 0, "score": 0}

    gaps_score = gaps_data.get("score", 0)
    total_score += gaps_score
    if gaps_score > 0:
        signals_triggered += 1
    evidence["competitor_gaps"] = gaps_data
    print(f"      ✅ Score: {gaps_score}/5 ({gaps_data.get('competitor_gaps_found', 0)} gaps found)")

    # SIGNAL 7: Market Size Validation
    print("\n   📈 Signal 7: Market Size Estimation")
    prompt_market = f"""Estimate Total Addressable Market (TAM) for this specific solution.

Business: {idea['business']}
Pain: {idea['pain']}

Calculate:
1. How many businesses match this profile? (size, industry, etc.)
2. What % would have this exact problem?
3. At $5k-$10k/year ACV, what's TAM?

TAM = (# businesses) × (% with problem) × (ACV)

Must be >$10M TAM to score high.

Return JSON:
{{
  "total_businesses": 0,
  "percent_with_problem": 0,
  "acv": 0,
  "tam": 0,
  "score": 0-5  // 0=<$5M, 5=>$50M
}}"""

    market_response = call_perplexity(prompt_market)
    market_data = perplexity_to_json(market_response, {
        "total_businesses": 0,
        "tam": 0,
        "score": 0
    }, call_openai) if market_response else {"total_businesses": 0, "tam": 0, "score": 0}

    market_score = market_data.get("score", 0)
    total_score += market_score
    if market_score > 0:
        signals_triggered += 1
    evidence["market_size"] = market_data
    print(f"      ✅ Score: {market_score}/5 (${market_data.get('tam', 0):,} TAM)")

    # SIGNAL 8: Frequency Validation
    print("\n   🔄 Signal 8: Frequency Validation")
    prompt_freq = f"""Confirm how often this pain point occurs.

Business: {idea['business']}
Pain: {idea['pain']}

Questions:
- Is this daily, weekly, monthly, or one-time?
- Is it seasonal or year-round?
- Is it recurring or project-based?

High score = daily or multiple times per week.

Return JSON:
{{
  "frequency": "daily" | "weekly" | "monthly" | "one-time",
  "seasonality": "year-round" | "seasonal",
  "evidence": ["source 1", "source 2"],
  "score": 0-4
}}"""

    freq_response = call_perplexity(prompt_freq)
    freq_data = perplexity_to_json(freq_response, {
        "frequency": "unknown",
        "evidence": [],
        "score": 0
    }, call_openai) if freq_response else {"frequency": "unknown", "score": 0}

    freq_score = freq_data.get("score", 0)
    total_score += freq_score
    if freq_score > 0:
        signals_triggered += 1
    evidence["frequency"] = freq_data
    print(f"      ✅ Score: {freq_score}/4 ({freq_data.get('frequency', 'unknown')} frequency)")

    # SUMMARY
    print(f"\n   📊 ECONOMIC PROOF SUMMARY:")
    print(f"      Total Score: {total_score}/39")
    print(f"      Signals Triggered: {signals_triggered}/8")

    # Decision criteria
    if total_score < 25:
        return False, f"Economic proof too weak ({total_score}/39)", evidence
    elif signals_triggered < 6:
        return False, f"Too few signals triggered ({signals_triggered}/8)", evidence
    elif market_data.get("tam", 0) < 10000000:  # <$10M TAM
        return False, f"Market too small (${market_data.get('tam', 0):,} TAM)", evidence

    print(f"\n✅ PASS - Strong economic validation")
    return True, "", evidence

# ═══════════════════════════════════════════════════════════
# BATCH PROCESSING ENGINE
# ═══════════════════════════════════════════════════════════

def run_stage_batch(ideas: List[Dict], stage_func, stage_name: str) -> Tuple[List[Dict], List[Dict]]:
    """Run a stage on all ideas in batch"""
    print(f"\n{'='*80}")
    print(f"BATCH PROCESSING: {stage_name}")
    print(f"Processing {len(ideas)} ideas...")
    print(f"{'='*80}\n")

    survivors = []
    killed = []

    for idx, idea in enumerate(ideas, 1):
        print(f"[{idx}/{len(ideas)}] Processing Idea #{idea['id']}\n")

        passed, reason, analysis = stage_func(idea)

        if passed:
            idea[f"{stage_name.lower().replace(' ', '_').replace(':', '')}_analysis"] = analysis
            survivors.append(idea)
        else:
            idea["status"] = f"killed_{stage_name.lower().split(':')[0].replace(' ', '')}"
            idea["kill_reason"] = reason
            idea[f"{stage_name.lower().replace(' ', '_').replace(':', '')}_analysis"] = analysis
            killed.append(idea)

    print(f"\n{'='*80}")
    print(f"{stage_name} COMPLETE:")
    print(f"✅ {len(survivors)} passed")
    print(f"❌ {len(killed)} killed")
    print(f"{'='*80}\n")

    return survivors, killed

# ═══════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Ultimate Winner Machine v6.0")
    parser.add_argument("--count", type=int, default=10, help="Number of ideas to generate")
    args = parser.parse_args()

    target_count = args.count
    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    print("="*80)
    print("🏆 ULTIMATE WINNER MACHINE v6.0 - THE SELF-IMPROVING ROI HUNTER")
    print("="*80)
    print(f"Run ID: {run_id}")
    print(f"Target ideas: {target_count}")
    print()
    print("Philosophy: Mine quantified pain points → Generate ROI-justified ideas →")
    print("           Filter through 7 stages → Find 8-10 validated candidates")
    print("="*80)

    # Load existing ideas
    ideas_bank = load_ideas_bank()
    print(f"\nExisting ideas in bank: {len(ideas_bank)}")

    # STAGE 0A-META: Discover sources
    sources = stage0a_meta_source_discovery()

    # STAGE 0B-DEEP: Mine quantified pains
    quantified_pains = stage0b_deep_pain_mining(sources)

    if len(quantified_pains) < 50:
        print(f"\n⚠️  WARNING: Only found {len(quantified_pains)} quantified pains.")
        print("   System works best with 500+ pains. Consider:")
        print("   1. Running with more sources (increase limit in stage0b)")
        print("   2. Broadening search queries")
        print("   3. Looking in more diverse industries")

    # STAGE 0C: Cluster by ROI
    pain_clusters = stage0c_roi_clustering(quantified_pains)

    # STAGE 0D: Generate ideas
    new_ideas = stage0d_idea_generation(pain_clusters, target_count)

    # Assign IDs and filter duplicates
    ideas_to_process = []
    next_id = len(ideas_bank) + 1

    for idea in new_ideas:
        if not idea_exists(ideas_bank, idea["business"], idea["pain"]):
            idea["id"] = next_id
            idea["hash"] = generate_idea_hash(idea["business"], idea["pain"])
            idea["generated_date"] = datetime.now().strftime("%Y-%m-%d")
            idea["run_id"] = run_id
            idea["status"] = "generated"
            ideas_to_process.append(idea)
            ideas_bank.append(idea)
            next_id += 1

    print(f"\n✅ Generated {len(ideas_to_process)} new ideas (filtered duplicates)")

    if len(ideas_to_process) == 0:
        print("\n⚠️  No new ideas to process. All were duplicates.")
        return

    # STAGE 1: White Space
    survivors, killed = run_stage_batch(
        ideas_to_process,
        stage1_white_space,
        "Stage 1: White Space"
    )
    ideas_bank.extend(killed)
    save_ideas_bank(ideas_bank)

    if not survivors:
        print("\n⚠️  No ideas passed Stage 1. All hit dominant players or high switching costs.")
        return

    # STAGE 2: Economic Proof
    survivors, killed = run_stage_batch(
        survivors,
        stage2_economic_proof,
        "Stage 2: Evidence"
    )
    ideas_bank.extend(killed)
    save_ideas_bank(ideas_bank)

    if not survivors:
        print("\n⚠️  No ideas passed Stage 2. Economic proof too weak.")
        return

    # STAGE 3: Buildability
    survivors, killed = run_stage_batch(
        survivors,
        stage3_build_feasibility,
        "Stage 3: Build"
    )
    ideas_bank.extend(killed)
    save_ideas_bank(ideas_bank)

    if not survivors:
        print("\n⚠️  No ideas passed Stage 3. All too complex to build.")
        return

    # STAGE 4: Cost Analysis
    survivors, killed = run_stage_batch(
        survivors,
        stage4_cost_analysis,
        "Stage 4: Cost"
    )
    ideas_bank.extend(killed)
    save_ideas_bank(ideas_bank)

    # STAGE 5: GTM
    survivors, killed = run_stage_batch(
        survivors,
        stage5_gtm_validation,
        "Stage 5: GTM"
    )
    ideas_bank.extend(killed)
    save_ideas_bank(ideas_bank)

    # STAGE 6: Founder Fit
    founder_profile = load_founder_profile()
    survivors, killed = run_stage_batch(
        survivors,
        lambda idea: stage6_founder_fit(idea, founder_profile),
        "Stage 6: Founder"
    )
    ideas_bank.extend(killed)
    save_ideas_bank(ideas_bank)

    # STAGE 7: Validation Playbooks
    if survivors:
        print(f"\n{'='*80}")
        print(f"STAGE 7: VALIDATION PLAYBOOK GENERATION")
        print(f"{'='*80}\n")

        for idea in survivors:
            playbook = stage7_validation_playbook(idea)
            idea["validation_playbook"] = playbook
            idea["status"] = "FINALIST"

            # Write finalist report
            filename = f"FINALIST_{idea['id']}_{idea['business'][:30].replace(' ', '_').replace('/', '_')}.txt"
            with open(filename, 'w') as f:
                f.write(f"{'='*80}\n")
                f.write(f"🏆 FINALIST IDEA #{idea['id']}\n")
                f.write(f"{'='*80}\n\n")
                f.write(f"BUSINESS: {idea['business']}\n\n")
                f.write(f"PAIN POINT: {idea['pain']}\n\n")
                f.write(f"ROI STATEMENT: {idea.get('roi_statement', 'N/A')}\n\n")
                f.write(f"ANNUAL COST: ${idea.get('current_annual_cost', 0):,}\n")
                f.write(f"TIME WASTE: {idea.get('time_waste_description', 'Unknown')}\n")
                f.write(f"FREQUENCY: {idea.get('frequency', 'Unknown')}\n\n")
                f.write(f"{'='*80}\n")
                f.write(f"VALIDATION PLAYBOOK\n")
                f.write(f"{'='*80}\n\n")
                f.write(playbook)

            print(f"   ✅ Generated: {filename}")

        save_ideas_bank(ideas_bank)

        print(f"\n{'='*80}")
        print(f"🎉 SUCCESS! Found {len(survivors)} FINALISTS")
        print(f"{'='*80}\n")
        print("Next steps:")
        print("1. Review FINALIST_*.txt reports")
        print("2. Pick top 2-3 based on your interests")
        print("3. Execute validation playbooks")
        print("4. Build MVPs for validated ideas")
    else:
        print("\n⚠️  No finalists found. All ideas were killed in filtering.")

if __name__ == "__main__":
    main()
