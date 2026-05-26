# app/pages/9_Live_News.py

import streamlit as st
import pandas as pd
import sys
import os

# ── Path setup ────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE)

from news_pipeline import fetch_all_feeds, save_live_news, load_live_news

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Live News Intelligence",
    page_icon="📰",
    layout="wide"
)

st.title("📰 Live News Intelligence")
st.markdown(
    "Real-time incident detection from Nigerian news sources. "
    "Automatically extracts state, category, and casualty data."
)

st.markdown("---")

# ── Fetch button ──────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 5])

with col1:
    fetch_clicked = st.button(
        "📡 Fetch Latest News",
        use_container_width=True
    )

with col2:
    st.caption(
        "Pulls from: Vanguard, Punch, Channels, "
        "Premium Times, Daily Post, The Nation, Tribune"
    )

# ── Fetch live ────────────────────────────────────────────────────────────────
if fetch_clicked:
    with st.spinner("Fetching from Nigerian news sources..."):
        df_live = fetch_all_feeds()

    if df_live.empty:
        st.error("No incidents found. Check your internet connection.")
    else:
        save_live_news(df_live, BASE)
        st.success(f"✅ {len(df_live)} incident articles fetched and saved.")
        st.session_state["live_news"] = df_live

# ── Load from saved file if not just fetched ──────────────────────────────────
if "live_news" not in st.session_state:
    df_saved = load_live_news(BASE)
    if not df_saved.empty:
        st.session_state["live_news"] = df_saved

# ── Display ───────────────────────────────────────────────────────────────────
if "live_news" in st.session_state:
    df = st.session_state["live_news"]

    # ── Summary metrics ───────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Articles",   len(df))
    col2.metric("States Affected",  df["State"].nunique())
    col3.metric("Total Deaths",     int(df["Number of deaths"].sum()))
    col4.metric("Sources",          df["Source"].nunique())

    st.markdown("---")

    # ── Filters ───────────────────────────────────────────────────────────────
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        states = ["All"] + sorted(df["State"].unique().tolist())
        selected_state = st.selectbox("Filter by State", states)

    with filter_col2:
        categories = ["All"] + sorted(df["Category"].unique().tolist())
        selected_cat = st.selectbox("Filter by Category", categories)

    with filter_col3:
        sources = ["All"] + sorted(df["Source"].unique().tolist())
        selected_source = st.selectbox("Filter by Source", sources)

    # Apply filters
    filtered = df.copy()
    if selected_state != "All":
        filtered = filtered[filtered["State"] == selected_state]
    if selected_cat != "All":
        filtered = filtered[filtered["Category"] == selected_cat]
    if selected_source != "All":
        filtered = filtered[filtered["Source"] == selected_source]

    st.markdown(f"**Showing {len(filtered)} articles**")
    st.markdown("---")

    # ── Article cards ─────────────────────────────────────────────────────────
    for _, row in filtered.head(50).iterrows():

        risk_color = (
            "#e74c3c" if row["Number of deaths"] > 10 else
            "#e67e22" if row["Number of deaths"] > 4  else
            "#f1c40f" if row["Number of deaths"] > 0  else
            "#2ecc71"
        )

        st.markdown(
            f"""
            <div style="
                border-left: 4px solid {risk_color};
                background: #1a1a2e;
                padding: 12px 16px;
                border-radius: 6px;
                margin-bottom: 10px;
            ">
                <div style="font-size:15px; font-weight:bold; margin-bottom:4px;">
                    {row['Title']}
                </div>
                <div style="font-size:12px; color:#aaa; margin-bottom:6px;">
                    📍 {row['State']} &nbsp;|&nbsp;
                    ⚠️ {row['Category']} &nbsp;|&nbsp;
                    💀 {int(row['Number of deaths'])} deaths &nbsp;|&nbsp;
                    📰 {row['Source']} &nbsp;|&nbsp;
                    🕒 {row['Fetched']}
                </div>
                <div style="font-size:13px; color:#ccc; margin-bottom:6px;">
                    {row['Summary']}
                </div>
                <a href="{row['URL']}" target="_blank"
                   style="font-size:12px; color:#3498db;">
                    Read full article →
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ── Charts ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📊 Analytics")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("**Incidents by State**")
        state_counts = filtered["State"].value_counts().head(10)
        st.bar_chart(state_counts)

    with chart_col2:
        st.markdown("**Incidents by Category**")
        cat_counts = filtered["Category"].value_counts()
        st.bar_chart(cat_counts)

else:
    st.info(
        "No news loaded yet. "
        "Click **📡 Fetch Latest News** to pull live incidents."
    )