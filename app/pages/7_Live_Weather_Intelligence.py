import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Live Weather Intelligence",
    page_icon="🌦️",
    layout="wide"
)

# =========================================
# LOAD DATA
# =========================================

df = pd.read_csv(
    "data/live_weather_data.csv"
)

# =========================================
# HEADER
# =========================================

st.title("🌦️ Nigeria Live Weather Intelligence")

st.markdown("""
Real-time environmental intelligence powered by:
- OpenWeather API
- climate analytics
- travel-weather intelligence
- environmental monitoring
""")

# =========================================
# METRICS
# =========================================

avg_temp = round(
    df["Temperature"].mean(),
    1
)

avg_humidity = round(
    df["Humidity"].mean(),
    1
)

max_wind = round(
    df["WindSpeed"].max(),
    1
)

cities = len(df)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Monitored Cities",
    cities
)

col2.metric(
    "Average Temp",
    f"{avg_temp}°C"
)

col3.metric(
    "Average Humidity",
    f"{avg_humidity}%"
)

col4.metric(
    "Highest Wind Speed",
    f"{max_wind} m/s"
)

st.markdown("---")

# =========================================
# WEATHER TABLE
# =========================================

st.subheader("🌍 Live Weather Conditions")

st.dataframe(
    df,
    use_container_width=True
)

# =========================================
# TEMPERATURE ANALYSIS
# =========================================

st.subheader("🌡️ Temperature Intelligence")

fig1 = px.bar(

    df,

    x="City",

    y="Temperature",

    color="Temperature",

    text_auto=True,

    title="Live Temperature by City"
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
# HUMIDITY ANALYSIS
# =========================================

st.subheader("💧 Humidity Intelligence")

fig2 = px.scatter(

    df,

    x="City",

    y="Humidity",

    size="Humidity",

    color="Humidity",

    hover_data=["Weather"],

    title="Humidity Severity"
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
# WIND ANALYSIS
# =========================================

st.subheader("🌪️ Wind Intelligence")

fig3 = px.line(

    df,

    x="City",

    y="WindSpeed",

    markers=True,

    title="Wind Speed Analysis"
)

fig3.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =========================================
# WEATHER ALERTS
# =========================================

st.subheader("⚠️ Environmental Alerts")

for _, row in df.iterrows():

    if row["WindSpeed"] > 10:

        st.error(
            f"STORM WARNING → "
            f"{row['City']} | "
            f"Wind Speed: {row['WindSpeed']} m/s"
        )

    elif row["Humidity"] > 85:

        st.warning(
            f"FLOOD RISK → "
            f"{row['City']} | "
            f"Humidity: {row['Humidity']}%"
        )

    else:

        st.success(
            f"NORMAL CONDITIONS → "
            f"{row['City']} | "
            f"{row['Weather']}"
        )

# =========================================
# DOWNLOAD
# =========================================

csv = df.to_csv(index=False)

st.download_button(

    label="⬇ Download Live Weather Data",

    data=csv,

    file_name="live_weather_data.csv",

    mime="text/csv"
)

# =========================================
# FOOTER
# =========================================

st.markdown("---")

st.caption(
    "Nigeria Live Weather Intelligence Platform"
)