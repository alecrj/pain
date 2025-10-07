#!/usr/bin/env python3
"""Quick script to fix all Signal parsing in Stage 2"""

with open('v5_stages_2_through_7.py', 'r') as f:
    content = f.read()

# Signal 3: Jobs
old_jobs = """    jobs_response = call_perplexity_fn(prompt_jobs)
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
        evidence["job_postings"] = {"score": 0}"""

new_jobs = """    jobs_response = call_perplexity_fn(prompt_jobs)
    schema = {"pain_mentions": 0, "sample_jobs": [], "score": 0}
    jobs_data = perplexity_to_json(jobs_response, schema, call_openai_fn) if jobs_response else schema

    jobs_score = jobs_data.get("score", 0)
    total_score += jobs_score
    if jobs_score > 0:
        signals_triggered += 1
    evidence["job_postings"] = jobs_data
    print(f"      ✅ Score: {jobs_score}/5 ({jobs_data.get('pain_mentions', 0)} mentions in jobs)")"""

content = content.replace(old_jobs, new_jobs)

# Signal 4: Gaps
old_gaps = """    gaps_response = call_perplexity_fn(prompt_gaps)
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
        evidence["competitor_gaps"] = {"score": 0}"""

new_gaps = """    gaps_response = call_perplexity_fn(prompt_gaps)
    schema = {"tools_found": [], "reviews_mentioning_gap": 0, "sample_complaints": [], "score": 0}
    gaps_data = perplexity_to_json(gaps_response, schema, call_openai_fn) if gaps_response else schema

    gaps_score = gaps_data.get("score", 0)
    total_score += gaps_score
    if gaps_score > 0:
        signals_triggered += 1
    evidence["competitor_gaps"] = gaps_data
    print(f"      ✅ Score: {gaps_score}/5 ({gaps_data.get('reviews_mentioning_gap', 0)} gap mentions)")"""

content = content.replace(old_gaps, new_gaps)

# Signal 5: Forums
old_forums = """    forums_response = call_perplexity_fn(prompt_forums)
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
        evidence["forums"] = {"score": 0}"""

new_forums = """    forums_response = call_perplexity_fn(prompt_forums)
    schema = {"threads_found": 0, "sample_threads": [], "score": 0}
    forums_data = perplexity_to_json(forums_response, schema, call_openai_fn) if forums_response else schema

    forums_score = forums_data.get("score", 0)
    total_score += forums_score
    if forums_score > 0:
        signals_triggered += 1
    evidence["forums"] = forums_data
    print(f"      ✅ Score: {forums_score}/4 ({forums_data.get('threads_found', 0)} forum threads)")"""

content = content.replace(old_forums, new_forums)

# Signal 6: Web
old_web = """    web_response = call_perplexity_fn(prompt_web)
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
        evidence["web_evidence"] = {"score": 0}"""

new_web = """    web_response = call_perplexity_fn(prompt_web)
    schema = {"sources_found": 0, "sample_sources": [], "score": 0}
    web_data = perplexity_to_json(web_response, schema, call_openai_fn) if web_response else schema

    web_score = web_data.get("score", 0)
    total_score += web_score
    if web_score > 0:
        signals_triggered += 1
    evidence["web_evidence"] = web_data
    print(f"      ✅ Score: {web_score}/4 ({web_data.get('sources_found', 0)} web sources)")"""

content = content.replace(old_web, new_web)

# Signal 7: Cost
old_cost = """    cost_response = call_perplexity_fn(prompt_cost)
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
        evidence["cost_research"] = {"score": 0}"""

new_cost = """    cost_response = call_perplexity_fn(prompt_cost)
    schema = {"cost_estimates": [], "sources": [], "has_third_party_validation": False, "score": 0}
    cost_data = perplexity_to_json(cost_response, schema, call_openai_fn) if cost_response else schema

    cost_score = cost_data.get("score", 0)
    total_score += cost_score
    if cost_score > 0:
        signals_triggered += 1
    evidence["cost_research"] = cost_data
    print(f"      ✅ Score: {cost_score}/5 (third-party cost validation)")"""

content = content.replace(old_cost, new_cost)

# Signal 8: Market
old_market = """    market_response = call_perplexity_fn(prompt_market)
    try:
        market_data = json.loads(market_response) if market_response else {}
        market_score = market_data.get("score", 0)
        # Market size is pass/fail, not added to score
        evidence["market_size"] = market_data
        print(f"      ✅ TAM: {market_data.get('tam_estimate', 'Unknown')} (Score: {market_score}/5)")
    except:
        print(f"      ⚠️  Could not parse market size")
        evidence["market_size"] = {"score": 0}
        market_score = 0"""

new_market = """    market_response = call_perplexity_fn(prompt_market)
    schema = {"total_businesses": 0, "addressable_percent": 0, "addressable_market": 0, "tam_estimate": "Unknown", "score": 0}
    market_data = perplexity_to_json(market_response, schema, call_openai_fn) if market_response else schema

    market_score = market_data.get("score", 0)
    # Market size is pass/fail, not added to score
    evidence["market_size"] = market_data
    print(f"      ✅ TAM: {market_data.get('tam_estimate', 'Unknown')} (Score: {market_score}/5)")"""

content = content.replace(old_market, new_market)

with open('v5_stages_2_through_7.py', 'w') as f:
    f.write(content)

print("✅ Fixed all 8 signals in Stage 2!")
