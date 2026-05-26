# app/pages/9_Database_Explorer.py

import streamlit as st
import sys
import os

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE)

from database import (
    get_db_stats, get_top_dangerous_states,
    get_recent_live_news, get_query_log,
    get_incidents_by_state, create_tables
)

st.set_page_config(
    page_title="Database Explorer",
    page_icon="🗄️",
    layout="wide"
)

st.title("🗄️ Database Explorer")
st.markdown("Live view of your Nigeria Incident Intelligence database.")
st.markdown("---")

# ── Ensure tables exist ───────────────────────────────────────────────────────
create_tables()

# ── Stats ─────────────────────────────────────────────────────────────────────
stats = get_db_stats()

col1, col2, col3, col4 = st.columns(4)
col1.metric("📋 Incidents",     stats["incidents"])
col2.metric("📰 Live News",     stats["live_news"])
col3.metric("🔍 Queries Logged", stats["query_log"])
col4.metric("📸 Snapshots",     stats["risk_snapshots"])

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
t1, t2, t3, t4 = st.tabs([
    "🏆 Dangerous States",
    "📰 Live News",
    "🔍 Query Log",
    "📋 Incidents by State"
])

with t1:
    st.subheader("Top Most Dangerous States")
    df = get_top_dangerous_states(20)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("state")["total_deaths"])
    else:
        st.info("No data yet.")

with t2:
    st.subheader("Recent Live News Articles")
    df = get_recent_live_news(50)
    if not df.empty:
        st.dataframe(
            df[["title", "state", "category", "deaths", "source", "fetched_at"]],
            use_container_width=True
        )
    else:
        st.info("No live news in database yet. Fetch from the Live News page.")

with t3:
    st.subheader("Location Query Log")
    df = get_query_log(50)
    if not df.empty:
        st.dataframe(df, use_container_width=True)

        st.markdown("**Most Searched States**")
        st.bar_chart(df["resolved_state"].value_counts().head(10))
    else:
        st.info("No queries logged yet.")

with t4:
    st.subheader("Search Incidents by State")
    from location_engine import NIGERIAN_STATES
    selected = st.selectbox("Select State", sorted(NIGERIAN_STATES))

    if st.button("Search"):
        df = get_incidents_by_state(selected)
        if not df.empty:
            st.success(f"{len(df)} incidents found in {selected}")
            st.dataframe(
                df[["title", "category", "deaths", "start_date"]],
                use_container_width=True
            )
        else:
            st.info(f"No incidents found for {selected}")