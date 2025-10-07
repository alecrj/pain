#!/usr/bin/env python3
"""
White Space Hunter Dashboard
View all tested ideas, stage-by-stage breakdown, and winners
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="White Space Hunter Dashboard",
    page_icon="🏆",
    layout="wide"
)

# Load ideas bank
@st.cache_data
def load_ideas():
    if os.path.exists("ideas_bank.json"):
        with open("ideas_bank.json", 'r') as f:
            data = json.load(f)
            return data.get("ideas", [])
    return []

ideas = load_ideas()

# Header
st.title("🏆 White Space Hunter Dashboard")
st.markdown("---")

# Overview metrics
col1, col2, col3, col4 = st.columns(4)

total_ideas = len(ideas)
winners = [i for i in ideas if i.get("status") == "WINNER"]
stage1_pass = [i for i in ideas if i.get("status", "").startswith("passed_stage") or i.get("status") == "WINNER"]
in_progress = [i for i in ideas if i.get("status") == "generated"]

with col1:
    st.metric("Total Ideas Tested", total_ideas)
with col2:
    st.metric("🏆 Winners Found", len(winners))
with col3:
    st.metric("✅ Passed Stage 1", len([i for i in ideas if "passed_stage1" in i.get("status", "") or i.get("status") == "WINNER"]))
with col4:
    st.metric("⏳ In Progress", len(in_progress))

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Funnel", "💡 All Ideas", "🏆 Winners", "❌ Kill Reasons", "📈 Stats"])

# TAB 1: Funnel
with tab1:
    st.header("Stage-by-Stage Funnel")

    # Calculate stage counts
    stage_counts = {
        "Generated": len(ideas),
        "Stage 1: White Space": len([i for i in ideas if "passed_stage1" in i.get("status", "") or i.get("status") == "WINNER"]),
        "Stage 2: Build": len([i for i in ideas if "passed_stage2" in i.get("status", "") or i.get("status") == "WINNER"]),
        "Stage 3: Cost": len([i for i in ideas if "passed_stage3" in i.get("status", "") or i.get("status") == "WINNER"]),
        "Stage 4: Evidence": len([i for i in ideas if "passed_stage4" in i.get("status", "") or i.get("status") == "WINNER"]),
        "Stage 5: GTM": len([i for i in ideas if "passed_stage5" in i.get("status", "") or i.get("status") == "WINNER"]),
        "Stage 6: Founder": len([i for i in ideas if i.get("status") == "WINNER"])
    }

    # Create funnel chart
    if total_ideas > 0:
        for stage, count in stage_counts.items():
            percentage = (count / total_ideas) * 100
            killed = stage_counts.get(stage.split(":")[0].strip(), count) - count if "Stage" in stage else 0

            col1, col2 = st.columns([3, 1])
            with col1:
                st.progress(percentage / 100, text=f"{stage}: {count} ideas ({percentage:.1f}%)")
            with col2:
                if "Stage" in stage:
                    st.caption(f"🔻 {killed} killed")
    else:
        st.info("No ideas tested yet. Run `python ultimate_winner_machine_v4.0.py --count=10`")

# TAB 2: All Ideas
with tab2:
    st.header("All Tested Ideas")

    if total_ideas > 0:
        # Filter
        status_filter = st.multiselect(
            "Filter by status:",
            options=["All", "Winners", "Passed Stage 1", "Passed Stage 2", "Passed Stage 3", "Killed"],
            default=["All"]
        )

        # Prepare data
        ideas_data = []
        for idea in ideas:
            status = idea.get("status", "unknown")
            stage_killed = None

            if status.startswith("killed_"):
                stage_killed = status.replace("killed_stage", "Stage ")
            elif status == "WINNER":
                stage_killed = "✅ WINNER"
            else:
                stage_killed = f"✅ {status.replace('_', ' ').title()}"

            ideas_data.append({
                "ID": idea.get("id", "?"),
                "Business": idea.get("business", "Unknown"),
                "Pain": idea.get("pain", "Unknown")[:100] + "...",
                "Status": stage_killed,
                "Date": idea.get("generated_date", "Unknown")
            })

        df = pd.DataFrame(ideas_data)

        # Apply filter
        if "Winners" in status_filter:
            df = df[df["Status"] == "✅ WINNER"]
        elif "Killed" in status_filter and "All" not in status_filter:
            df = df[df["Status"].str.contains("Stage")]

        st.dataframe(df, use_container_width=True, height=600)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"ideas_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No ideas tested yet.")

# TAB 3: Winners
with tab3:
    st.header("🏆 True Winners")

    if len(winners) > 0:
        for winner in winners:
            with st.expander(f"💡 {winner.get('business')} - {winner.get('pain')[:80]}..."):
                st.markdown(f"**Business:** {winner.get('business')}")
                st.markdown(f"**Pain Point:** {winner.get('pain')}")
                st.markdown(f"**Generated:** {winner.get('generated_date')}")

                if winner.get("stage1_analysis"):
                    st.markdown("### Stage 1: White Space Analysis")
                    st.text(winner.get("stage1_analysis")[:500] + "...")

                if winner.get("stage3_analysis"):
                    st.markdown("### Stage 3: Cost Analysis")
                    st.text(winner.get("stage3_analysis")[:500] + "...")

                if winner.get("stage4_analysis"):
                    st.markdown("### Stage 4: Evidence")
                    st.text(winner.get("stage4_analysis")[:500] + "...")

                st.success(f"✅ This idea passed all 6 stages! See WINNER_{winner.get('id')}_*.txt for full report")
    else:
        st.warning("No winners found yet. This is normal - most runs find 0-1 winners per 100 ideas.")
        st.info("💡 Tip: Run 100 ideas to increase chances of finding validated opportunities")

# TAB 4: Kill Reasons
with tab4:
    st.header("❌ Why Ideas Were Killed")

    killed_ideas = [i for i in ideas if i.get("status", "").startswith("killed_")]

    if len(killed_ideas) > 0:
        # Count by stage
        kill_stages = {}
        for idea in killed_ideas:
            stage = idea.get("status", "unknown").replace("killed_stage", "Stage ")
            kill_stages[stage] = kill_stages.get(stage, 0) + 1

        # Display breakdown
        st.subheader("Kills by Stage")
        for stage, count in sorted(kill_stages.items()):
            st.metric(stage, count)

        st.markdown("---")

        # Show recent kills
        st.subheader("Recent Kills (Last 10)")
        recent_kills = killed_ideas[-10:]

        for idea in reversed(recent_kills):
            stage = idea.get("status", "").replace("killed_stage", "Stage ")
            with st.expander(f"{stage} - {idea.get('business')} - {idea.get('pain')[:60]}..."):
                st.markdown(f"**Business:** {idea.get('business')}")
                st.markdown(f"**Pain:** {idea.get('pain')}")
                st.markdown(f"**Killed in:** {stage}")

                reason = idea.get("kill_reason", "No reason provided")
                st.markdown("**Reason:**")
                st.text(reason[:800] + "..." if len(reason) > 800 else reason)
    else:
        st.info("No killed ideas yet (or all ideas passed!).")

# TAB 5: Stats
with tab5:
    st.header("📈 Statistics")

    if total_ideas > 0:
        # Pass rates by stage
        st.subheader("Pass Rates")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Stage 1: White Space", f"{len([i for i in ideas if 'passed_stage1' in i.get('status', '')])}/{total_ideas}")
            st.metric("Stage 2: Build", f"{len([i for i in ideas if 'passed_stage2' in i.get('status', '')])}/{total_ideas}")
            st.metric("Stage 3: Cost", f"{len([i for i in ideas if 'passed_stage3' in i.get('status', '')])}/{total_ideas}")

        with col2:
            st.metric("Stage 4: Evidence", f"{len([i for i in ideas if 'passed_stage4' in i.get('status', '')])}/{total_ideas}")
            st.metric("Stage 5: GTM", f"{len([i for i in ideas if 'passed_stage5' in i.get('status', '')])}/{total_ideas}")
            st.metric("Stage 6: Founder", f"{len(winners)}/{total_ideas}")

        st.markdown("---")

        # Most common businesses tested
        st.subheader("Most Tested Industries")
        businesses = {}
        for idea in ideas:
            biz = idea.get("business", "Unknown")
            businesses[biz] = businesses.get(biz, 0) + 1

        top_biz = sorted(businesses.items(), key=lambda x: x[1], reverse=True)[:10]
        for biz, count in top_biz:
            st.text(f"{biz}: {count} ideas")

        st.markdown("---")

        # Timeline
        st.subheader("Ideas Over Time")
        dates = {}
        for idea in ideas:
            date = idea.get("generated_date", "Unknown")
            dates[date] = dates.get(date, 0) + 1

        if dates:
            df_timeline = pd.DataFrame(list(dates.items()), columns=["Date", "Ideas"])
            df_timeline = df_timeline.sort_values("Date")
            st.line_chart(df_timeline.set_index("Date"))
    else:
        st.info("No statistics available yet.")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total ideas in bank: {total_ideas}")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
