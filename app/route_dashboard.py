import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Nigeria Route Security Intelligence",
    page_icon="🛣️",
    layout="wide"
)

# =========================================
# LOAD DATA
# =========================================

df = pd.read_csv(
    "data/route_risk_analysis.csv"
)

# =========================================
# CUSTOM STYLING
# =========================================

st.markdown(
    """
    <style>

    .main {
        background-color: #0E1117;
        color: white;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================
# HEADER
# =========================================

st.title("🛣️ Nigeria Route Security Intelligence")

st.markdown("""
AI-powered highway risk analysis platform.

Monitor:
- dangerous highways
- bandit-prone corridors
- travel safety
- route intelligence
- security threats
""")

# =========================================
# METRICS
# =========================================

total_routes = len(df)

extreme_routes = len(
    df[df["RiskLevel"] == "Extreme"]
)

high_routes = len(
    df[df["RiskLevel"] == "High"]
)

total_deaths = int(
    df["Deaths"].sum()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Analyzed Routes",
    total_routes
)

col2.metric(
    "Extreme Risk Routes",
    extreme_routes
)

col3.metric(
    "High Risk Routes",
    high_routes
)

col4.metric(
    "Deaths Across Routes",
    total_deaths
)

st.markdown("---")

# =========================================
# RISK RANKING
# =========================================

st.subheader("🚨 Highway Risk Rankings")

sorted_df = df.sort_values(
    by="TravelRisk",
    ascending=False
)

fig1 = px.bar(

    sorted_df,

    x="Route",

    y="TravelRisk",

    color="RiskLevel",

    text_auto=True,

    title="Travel Risk Scores by Highway"
)

fig1.update_layout(
    template="plotly_dark",
    height=550
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# =========================================
# DEATH ANALYSIS
# =========================================

st.subheader("⚠️ Death Distribution by Route")

fig2 = px.pie(

    sorted_df,

    names="Route",

    values="Deaths",

    hole=0.5,

    title="Deaths Across Highways"
)

fig2.update_layout(
    template="plotly_dark",
    height=550
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =========================================
# BANDIT ANALYSIS
# =========================================

st.subheader("🔫 Bandit Corridor Analysis")

fig3 = px.scatter(

    sorted_df,

    x="BanditScore",

    y="TravelRisk",

    size="Deaths",

    color="RiskLevel",

    hover_name="Route",

    title="Bandit Threat Intelligence"
)

fig3.update_layout(
    template="plotly_dark",
    height=600
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =========================================
# SAFETY RECOMMENDATIONS
# =========================================

st.subheader("🛡️ Route Recommendations")

for _, row in sorted_df.iterrows():

    if row["RiskLevel"] == "Extreme":

        st.error(
            f"AVOID: {row['Route']} "
            f"(Travel Risk: {row['TravelRisk']})"
        )

    elif row["RiskLevel"] == "High":

        st.warning(
            f"CAUTION: {row['Route']} "
            f"(Travel Risk: {row['TravelRisk']})"
        )

    else:

        st.success(
            f"SAFE: {row['Route']} "
            f"(Travel Risk: {row['TravelRisk']})"
        )

# =========================================
# RAW INTELLIGENCE TABLE
# =========================================

st.markdown("---")

st.subheader("📊 Full Route Intelligence Table")

st.dataframe(
    sorted_df,
    use_container_width=True
)

# =========================================
# FOOTER
# =========================================

st.markdown("---")

st.caption(
    "Nigeria AI Route Security Intelligence System"
)