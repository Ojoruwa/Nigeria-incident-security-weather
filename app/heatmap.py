import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Nigeria Security Intelligence System",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# LOAD DATA
# =========================================

df = pd.read_csv(
    "data/engineered_incidents.csv"
)

# =========================================
# CUSTOM CSS
# =========================================

st.markdown(
    """
    <style>

    .main {
        background-color: #0E1117;
        color: white;
    }

    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid #333;
    }

    .big-font {
        font-size:22px !important;
        font-weight: bold;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================
# HEADER
# =========================================

st.title("🚨 Nigeria Security Intelligence System")

st.markdown("""
Advanced AI-powered platform for:
- Incident intelligence
- Bandit hotspot analysis
- Route danger detection
- Travel risk analytics
- National safety monitoring
""")

# =========================================
# SIDEBAR
# =========================================

st.sidebar.title("🛠 Intelligence Filters")

# State filter
states = sorted(df["State"].dropna().unique())

selected_states = st.sidebar.multiselect(
    "Select States",
    states,
    default=states
)

# Route alert filter
alerts = sorted(df["RouteAlert"].dropna().unique())

selected_alerts = st.sidebar.multiselect(
    "Route Alerts",
    alerts,
    default=alerts
)

# Region filter
regions = sorted(df["Region"].dropna().unique())

selected_regions = st.sidebar.multiselect(
    "Regions",
    regions,
    default=regions
)

# =========================================
# FILTER DATA
# =========================================

filtered_df = df[
    (df["State"].isin(selected_states)) &
    (df["RouteAlert"].isin(selected_alerts)) &
    (df["Region"].isin(selected_regions))
]

# =========================================
# METRICS
# =========================================

total_incidents = len(filtered_df)

avoid_routes = len(
    filtered_df[
        filtered_df["RouteAlert"] == "Avoid Route"
    ]
)

total_deaths = int(
    filtered_df["Number of deaths"].sum()
)

bandit_cases = len(
    filtered_df[
        filtered_df["BanditScore"] > 0
    ]
)

# =========================================
# TOP METRIC ROW
# =========================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Incidents",
        total_incidents
    )

with col2:
    st.metric(
        "Avoid Routes",
        avoid_routes
    )

with col3:
    st.metric(
        "Total Deaths",
        total_deaths
    )

with col4:
    st.metric(
        "Bandit Cases",
        bandit_cases
    )

st.markdown("---")

# =========================================
# TABS
# =========================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🔥 Hotspots",
    "🚨 Bandit Intelligence",
    "🛣 Route Analysis",
    "📊 Raw Intelligence"
])

# =========================================
# TAB 1 — HOTSPOTS
# =========================================

with tab1:

    st.subheader("Top Incident Hotspots")

    hotspot_data = filtered_df[
        "State"
    ].value_counts().reset_index()

    hotspot_data.columns = [
        "State",
        "Incidents"
    ]

    fig1 = px.bar(
        hotspot_data,
        x="State",
        y="Incidents",
        text_auto=True,
        title="Incident Hotspots by State"
    )

    fig1.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    # Death Heatmap
    death_data = filtered_df.groupby(
        "State"
    )["Number of deaths"].sum().reset_index()

    fig2 = px.treemap(
        death_data,
        path=["State"],
        values="Number of deaths",
        title="Deaths Distribution"
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
# TAB 2 — BANDIT INTELLIGENCE
# =========================================

with tab2:

    st.subheader("Bandit & Violent Activity Intelligence")

    bandit_df = filtered_df[
        filtered_df["BanditScore"] > 0
    ]

    bandit_counts = bandit_df[
        "State"
    ].value_counts().reset_index()

    bandit_counts.columns = [
        "State",
        "Bandit Incidents"
    ]

    fig3 = px.bar(
        bandit_counts,
        x="State",
        y="Bandit Incidents",
        color="Bandit Incidents",
        title="Bandit Activity by State"
    )

    fig3.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    st.subheader("Most Dangerous Reports")

    dangerous_reports = bandit_df.sort_values(
        by="TravelRiskScore",
        ascending=False
    )

    st.dataframe(
        dangerous_reports[[
            "Title",
            "State",
            "Region",
            "Number of deaths",
            "TravelRiskScore",
            "RouteAlert"
        ]].head(20),
        use_container_width=True
    )

# =========================================
# TAB 3 — ROUTE ANALYSIS
# =========================================

with tab3:

    st.subheader("Travel Route Intelligence")

    route_counts = filtered_df[
        "RouteAlert"
    ].value_counts().reset_index()

    route_counts.columns = [
        "RouteAlert",
        "Count"
    ]

    fig4 = px.pie(
        route_counts,
        names="RouteAlert",
        values="Count",
        hole=0.5,
        title="Travel Safety Distribution"
    )

    fig4.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

    # Risk table
    risk_table = filtered_df.sort_values(
        by="TravelRiskScore",
        ascending=False
    )

    st.subheader("High Risk Travel Alerts")

    st.dataframe(
        risk_table[[
            "Title",
            "State",
            "TravelRiskScore",
            "RouteAlert"
        ]].head(25),
        use_container_width=True
    )

# =========================================
# TAB 4 — RAW DATA
# =========================================

with tab4:

    st.subheader("Full Intelligence Dataset")

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

# =========================================
# FOOTER
# =========================================

st.markdown("---")

st.caption(
    "Nigeria Security Intelligence System • AI-Powered Analytics"
)