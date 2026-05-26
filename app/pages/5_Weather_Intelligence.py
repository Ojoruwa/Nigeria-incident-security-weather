import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Weather Security Intelligence",
    page_icon="🌧️",
    layout="wide"
)

# =========================================
# LOAD DATA
# =========================================

df = pd.read_csv(
    "data/weather_intelligence.csv"
)

# =========================================
# HEADER
# =========================================

st.title("🌧️ Nigeria Weather Security Intelligence")

st.markdown("""
AI-powered climate + security intelligence platform.

Combines:
- rainfall analytics
- flood monitoring
- route intelligence
- bandit threats
- environmental risk
""")

# =========================================
# METRICS
# =========================================

total_records = len(df)

extreme_alerts = len(
    df[
        df["CombinedAlert"] == "Extreme Danger"
    ]
)

high_risk = len(
    df[
        df["CombinedAlert"] == "High Risk"
    ]
)

avg_risk = round(
    df["CombinedRiskScore"].mean(),
    2
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Analyzed Records",
    total_records
)

col2.metric(
    "Extreme Alerts",
    extreme_alerts
)

col3.metric(
    "High Risk Alerts",
    high_risk
)

col4.metric(
    "Average Combined Risk",
    avg_risk
)

st.markdown("---")

# =========================================
# FLOOD RISK DISTRIBUTION
# =========================================

st.subheader("🌊 Flood Risk Distribution")

flood_counts = df[
    "FloodRisk"
].value_counts().reset_index()

flood_counts.columns = [
    "FloodRisk",
    "Count"
]

fig1 = px.bar(

    flood_counts,

    x="FloodRisk",

    y="Count",

    color="FloodRisk",

    text_auto=True,

    title="Flood Threat Levels"
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
# RAINFALL ANALYSIS
# =========================================

st.subheader("🌧️ Rainfall Intelligence")

state_rainfall = df.groupby(
    "State"
)["RainfallLevel"].mean().reset_index()

fig2 = px.scatter(

    state_rainfall,

    x="State",

    y="RainfallLevel",

    size="RainfallLevel",

    color="RainfallLevel",

    title="Rainfall Severity by State"
)

fig2.update_layout(
    template="plotly_dark",
    height=600
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =========================================
# COMBINED SECURITY ANALYSIS
# =========================================

st.subheader("🚨 Combined Threat Intelligence")

fig3 = px.scatter(

    df,

    x="WeatherRiskScore",

    y="TravelRiskScore",

    size="CombinedRiskScore",

    color="CombinedAlert",

    hover_name="State",

    title="Weather + Security Risk Matrix"
)

fig3.update_layout(
    template="plotly_dark",
    height=650
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =========================================
# EXTREME DANGER TABLE
# =========================================

st.subheader("⚠️ Extreme Danger States")

danger_df = df[
    df["CombinedAlert"] == "Extreme Danger"
]

st.dataframe(

    danger_df[[
        "Title",
        "State",
        "FloodRisk",
        "RainfallLevel",
        "BanditScore",
        "TravelRiskScore",
        "CombinedRiskScore",
        "CombinedAlert"
    ]],

    use_container_width=True
)

# =========================================
# SAFETY ALERTS
# =========================================

st.subheader("🛡️ AI Safety Alerts")

for _, row in df.iterrows():

    if row["CombinedAlert"] == "Extreme Danger":

        st.error(
            f"EXTREME DANGER → "
            f"{row['State']} | "
            f"Flood Risk: {row['FloodRisk']} | "
            f"Combined Score: {row['CombinedRiskScore']}"
        )

    elif row["CombinedAlert"] == "High Risk":

        st.warning(
            f"HIGH RISK → "
            f"{row['State']} | "
            f"Combined Score: {row['CombinedRiskScore']}"
        )

# =========================================
# FULL TABLE
# =========================================

st.markdown("---")

st.subheader("📊 Full Weather Intelligence Table")

st.dataframe(
    df,
    use_container_width=True
)

# =========================================
# DOWNLOAD
# =========================================

csv = df.to_csv(index=False)

st.download_button(

    label="⬇ Download Weather Intelligence",

    data=csv,

    file_name="weather_security_intelligence.csv",

    mime="text/csv"
)

# =========================================
# FOOTER
# =========================================

st.markdown("---")

st.caption(
    "Nigeria Climate + Security Intelligence Platform"
)