import streamlit as st
import pandas as pd
import folium

from folium.plugins import HeatMap
from folium.plugins import MarkerCluster

from streamlit_folium import st_folium

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Nigeria GIS Intelligence",
    page_icon="🗺️",
    layout="wide"
)

# =========================================
# LOAD DATA
# =========================================

df = pd.read_csv(
    "data/geo_incidents.csv"
)

# =========================================
# REMOVE BAD COORDINATES
# =========================================

df = df.dropna(
    subset=["Latitude", "Longitude"]
)

# =========================================
# HEADER
# =========================================

st.title("🗺️ Nigeria GIS Security Intelligence")

st.markdown("""
Interactive national threat intelligence system.

Features:
- Live GIS danger zones
- Route intelligence
- Bandit hotspot tracking
- Travel safety monitoring
- Security analytics
""")

# =========================================
# SIDEBAR
# =========================================

st.sidebar.header("Map Intelligence Filters")

# States
states = sorted(df["State"].dropna().unique())

selected_states = st.sidebar.multiselect(
    "Select States",
    states,
    default=states
)

# Route alerts
alerts = sorted(df["RouteAlert"].dropna().unique())

selected_alerts = st.sidebar.multiselect(
    "Route Alerts",
    alerts,
    default=alerts
)

# =========================================
# FILTER DATA
# =========================================

filtered_df = df[
    (df["State"].isin(selected_states)) &
    (df["RouteAlert"].isin(selected_alerts))
]

# =========================================
# METRICS
# =========================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Incidents",
    len(filtered_df)
)

col2.metric(
    "Avoid Routes",
    len(
        filtered_df[
            filtered_df["RouteAlert"] == "Avoid Route"
        ]
    )
)

col3.metric(
    "Bandit Incidents",
    len(
        filtered_df[
            filtered_df["BanditScore"] > 0
        ]
    )
)

col4.metric(
    "Deaths",
    int(
        filtered_df[
            "Number of deaths"
        ].sum()
    )
)

st.markdown("---")

# =========================================
# CREATE MAP
# =========================================

m = folium.Map(

    location=[9.0820, 8.6753],

    zoom_start=6,

    control_scale=True,

    tiles="CartoDB dark_matter"
)

# =========================================
# HEATMAP
# =========================================

heat_data = filtered_df[[
    "Latitude",
    "Longitude",
    "TravelRiskScore"
]].values.tolist()

HeatMap(
    heat_data,
    radius=30,
    blur=20
).add_to(m)

# =========================================
# MARKER CLUSTER
# =========================================

marker_cluster = MarkerCluster().add_to(m)

# =========================================
# INCIDENT MARKERS
# =========================================

for _, row in filtered_df.iterrows():

    if row["RouteAlert"] == "Avoid Route":
        color = "red"

    elif row["RouteAlert"] == "Caution":
        color = "orange"

    else:
        color = "green"

    popup = f"""
    <b>Incident:</b> {row['Title']}<br>
    <b>State:</b> {row['State']}<br>
    <b>Deaths:</b> {row['Number of deaths']}<br>
    <b>Bandit Score:</b> {row['BanditScore']}<br>
    <b>Travel Risk:</b> {row['TravelRiskScore']}<br>
    <b>Route Alert:</b> {row['RouteAlert']}
    """

    folium.CircleMarker(

        location=[
            row["Latitude"],
            row["Longitude"]
        ],

        radius=7,

        popup=popup,

        color=color,

        fill=True,

        fill_color=color,

        fill_opacity=0.8

    ).add_to(marker_cluster)

# =========================================
# DISPLAY MAP
# =========================================

st.subheader("🚨 National GIS Threat Map")

map_data = st_folium(
    m,
    width=1400,
    height=700
)

# =========================================
# HIGH RISK TABLE
# =========================================

st.markdown("---")

st.subheader("⚠️ Highest Risk Incidents")

high_risk_df = filtered_df.sort_values(
    by="TravelRiskScore",
    ascending=False
)

st.dataframe(
    high_risk_df[[
        "Title",
        "State",
        "Region",
        "Number of deaths",
        "BanditScore",
        "TravelRiskScore",
        "RouteAlert"
    ]].head(30),
    use_container_width=True
)

# =========================================
# FOOTER
# =========================================

st.markdown("---")

st.caption(
    "Nigeria GIS Threat Intelligence Platform"
)