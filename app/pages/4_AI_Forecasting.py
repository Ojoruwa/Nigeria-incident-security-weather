import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="AI Forecast Intelligence",
    page_icon="📈",
    layout="wide"
)

# =========================================
# LOAD DATA
# =========================================

df = pd.read_csv(
    "data/forecast_predictions.csv"
)

# =========================================
# HEADER
# =========================================

st.title("📈 Nigeria AI Forecast Intelligence")

st.markdown("""
Predictive intelligence system for:
- future incident forecasting
- danger escalation analysis
- hotspot prediction
- proactive security monitoring
""")

# =========================================
# METRICS
# =========================================

total_forecasts = len(df)

extreme_months = len(
    df[
        df["ForecastRisk"] == "Extreme"
    ]
)

high_months = len(
    df[
        df["ForecastRisk"] == "High"
    ]
)

average_prediction = int(
    df["PredictedIncidents"].mean()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Forecast Months",
    total_forecasts
)

col2.metric(
    "Extreme Risk Months",
    extreme_months
)

col3.metric(
    "High Risk Months",
    high_months
)

col4.metric(
    "Average Predicted Incidents",
    average_prediction
)

st.markdown("---")

# =========================================
# FORECAST TREND
# =========================================

st.subheader("🚨 Future Incident Forecast")

fig1 = px.line(

    df,

    x="FutureMonthIndex",

    y="PredictedIncidents",

    markers=True,

    color="ForecastRisk",

    title="Predicted Incident Escalation"
)

fig1.update_layout(
    template="plotly_dark",
    height=600
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# =========================================
# RISK DISTRIBUTION
# =========================================

st.subheader("⚠️ Forecast Risk Distribution")

risk_counts = df[
    "ForecastRisk"
].value_counts().reset_index()

risk_counts.columns = [
    "Risk",
    "Count"
]

fig2 = px.bar(

    risk_counts,

    x="Risk",

    y="Count",

    color="Risk",

    text_auto=True,

    title="Predicted Future Risks"
)

fig2.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =========================================
# SEVERITY ANALYSIS
# =========================================

st.subheader("🔥 Forecast Severity Analysis")

fig3 = px.scatter(

    df,

    x="FutureMonthIndex",

    y="PredictedIncidents",

    size="PredictedIncidents",

    color="ForecastRisk",

    hover_data=["ForecastRisk"],

    title="Future Threat Severity"
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
# FUTURE WARNINGS
# =========================================

st.subheader("🛡️ AI Forecast Warnings")

for _, row in df.iterrows():

    if row["ForecastRisk"] == "Extreme":

        st.error(
            f"EXTREME WARNING → "
            f"Month Index {row['FutureMonthIndex']} "
            f"Predicted Incidents: "
            f"{row['PredictedIncidents']}"
        )

    elif row["ForecastRisk"] == "High":

        st.warning(
            f"HIGH RISK → "
            f"Month Index {row['FutureMonthIndex']} "
            f"Predicted Incidents: "
            f"{row['PredictedIncidents']}"
        )

    else:

        st.success(
            f"MODERATE/LOW → "
            f"Month Index {row['FutureMonthIndex']} "
            f"Predicted Incidents: "
            f"{row['PredictedIncidents']}"
        )

# =========================================
# FORECAST TABLE
# =========================================

st.markdown("---")

st.subheader("📊 Full Forecast Intelligence")

st.dataframe(
    df,
    use_container_width=True
)

# =========================================
# DOWNLOAD
# =========================================

csv = df.to_csv(index=False)

st.download_button(

    label="⬇ Download Forecast Report",

    data=csv,

    file_name="forecast_intelligence.csv",

    mime="text/csv"
)

# =========================================
# FOOTER
# =========================================

st.markdown("---")

st.caption(
    "Nigeria AI Forecast Intelligence Platform"
)