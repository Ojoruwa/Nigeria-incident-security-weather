import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Live Nigeria Threat Monitor",
    page_icon="🚨",
    layout="wide"
)

# =========================================
# LOAD DATA
# =========================================

df = pd.read_csv(
    "data/live_news_incidents.csv"
)

# =========================================
# HEADER
# =========================================

st.title("🚨 Live Nigeria Threat Intelligence Monitor")

st.markdown("""
Real-time AI-powered security monitoring system.

Tracks:
- attacks
- kidnappings
- explosions
- bandit activity
- crashes
- violent incidents
""")

# =========================================
# METRICS
# =========================================

total_news = len(df)

sources = df["Source"].nunique()

alerts = len(
    df[
        df["KeywordMatch"] == True
    ]
)

headline_volume = len(
    df["Headline"].unique()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Threat Headlines",
    total_news
)

col2.metric(
    "News Sources",
    sources
)

col3.metric(
    "Threat Alerts",
    alerts
)

col4.metric(
    "Unique Headlines",
    headline_volume
)

st.markdown("---")

# =========================================
# SOURCE DISTRIBUTION
# =========================================

st.subheader("📰 Threat Sources")

source_counts = df[
    "Source"
].value_counts().reset_index()

source_counts.columns = [
    "Source",
    "Count"
]

fig1 = px.bar(

    source_counts,

    x="Source",

    y="Count",

    color="Count",

    text_auto=True,

    title="Threat Headlines by News Source"
)

fig1.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# =========================================
# LIVE THREAT FEED
# =========================================

st.subheader("⚠️ Live Threat Feed")

for _, row in df.iterrows():

    headline = row["Headline"]

    lower_headline = headline.lower()

    # =====================================
    # ALERT COLORS
    # =====================================

    if (
        "kidnap" in lower_headline or
        "terrorist" in lower_headline or
        "bandit" in lower_headline
    ):

        st.error(
            f"{row['Source']} • {headline}"
        )

    elif (
        "attack" in lower_headline or
        "gunmen" in lower_headline
    ):

        st.warning(
            f"{row['Source']} • {headline}"
        )

    else:

        st.info(
            f"{row['Source']} • {headline}"
        )

# =========================================
# SEARCH
# =========================================

st.markdown("---")

st.subheader("🔍 Search Intelligence Feed")

search = st.text_input(
    "Search Threat Headlines"
)

if search:

    filtered_df = df[
        df["Headline"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

# =========================================
# RAW DATA
# =========================================

st.markdown("---")

st.subheader("📊 Full Intelligence Feed")

st.dataframe(
    df,
    use_container_width=True
)

# =========================================
# DOWNLOAD
# =========================================

csv = df.to_csv(index=False)

st.download_button(

    label="⬇ Download Threat Feed",

    data=csv,

    file_name="live_threat_feed.csv",

    mime="text/csv"
)

# =========================================
# FOOTER
# =========================================

st.markdown("---")

st.caption(
    "Nigeria Live Threat Intelligence Platform"
)