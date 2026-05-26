import streamlit as st
import pandas as pd
import joblib
import sys
import os

# Add parent directory to path so we can import location_engine etc.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from location_engine import load_data, query_location
from location_map import build_location_map

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Nigeria Incident Risk Predictor",
    page_icon="🚨",
    layout="wide"
)

# =========================================
# BASE PATH (one level up from app/)
# =========================================

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# =========================================
# LOAD MODELS
# =========================================

model            = joblib.load(os.path.join(BASE, "models", "risk_model.pkl"))
state_encoder    = joblib.load(os.path.join(BASE, "models", "state_encoder.pkl"))
category_encoder = joblib.load(os.path.join(BASE, "models", "category_encoder.pkl"))

# =========================================
# LOAD INCIDENT DATA
# =========================================

@st.cache_data
def get_data():
    return load_data(os.path.join(BASE, "data", "incidents.csv"))

df = get_data()

# =========================================
# TITLE
# =========================================

st.title("🚨 Nigeria Incident Risk Predictor")

st.markdown(
    "This AI system predicts incident risk levels across Nigeria using Machine Learning."
)

# =========================================
# TABS
# =========================================

tab1, tab2 = st.tabs([
    "📊 Risk Predictor",
    "📍 Location Intelligence"
])

# =========================================
# TAB 1 — RISK PREDICTOR (original)
# =========================================

with tab1:

    st.sidebar.header("Prediction Inputs")

    # State dropdown
    states = list(state_encoder.classes_)
    selected_state = st.sidebar.selectbox("Select State", states)

    # Category dropdown
    categories = list(category_encoder.classes_)
    selected_category = st.sidebar.selectbox("Select Incident Category", categories)

    # Number inputs
    deaths = st.sidebar.number_input(
        "Number of Deaths", min_value=0, max_value=1000, value=1
    )
    year = st.sidebar.number_input(
        "Year", min_value=2000, max_value=2100, value=2025
    )
    month = st.sidebar.slider(
        "Month", min_value=1, max_value=12, value=5
    )

    if st.sidebar.button("Predict Risk"):

        state_encoded    = state_encoder.transform([selected_state])[0]
        category_encoded = category_encoder.transform([selected_category])[0]

        input_data = pd.DataFrame({
            "StateEncoded":      [state_encoded],
            "CategoryEncoded":   [category_encoded],
            "Number of deaths":  [deaths],
            "Year":              [year],
            "Month":             [month],
        })

        prediction = model.predict(input_data)[0]

        st.subheader("Prediction Result")

        if prediction == "Extreme":
            st.error(f"🚨 EXTREME RISK detected in {selected_state}")
        elif prediction == "High":
            st.warning(f"⚠️ HIGH RISK detected in {selected_state}")
        else:
            st.success(f"✅ LOW RISK detected in {selected_state}")

        st.write("### Prediction Details")
        st.write(f"State: {selected_state}")
        st.write(f"Category: {selected_category}")
        st.write(f"Deaths: {deaths}")
        st.write(f"Year: {year}")
        st.write(f"Month: {month}")

# =========================================
# TAB 2 — LOCATION INTELLIGENCE
# =========================================

with tab2:

    st.header("📍 Location Intelligence")
    st.write(
        "Search any Nigerian location, road, or neighborhood "
        "to get a full risk intelligence report and interactive map."
    )

    # ── Search box ────────────────────────────────────────────────────────────
    col_input, col_btn = st.columns([4, 1])

    with col_input:
        location_query = st.text_input(
            label="Search location",
            placeholder="e.g. Ibadan, Lekki, Abuja-Kaduna Road, Maiduguri",
            label_visibility="collapsed"
        )

    with col_btn:
        search_clicked = st.button("🔎 Analyze", use_container_width=True)

    # ── Results ───────────────────────────────────────────────────────────────
    if search_clicked and location_query.strip():

        with st.spinner(f"Analyzing {location_query}..."):
            result = query_location(location_query.strip(), df)

        if result["error"]:
            st.error(result["message"])

        else:
            # ── Header ────────────────────────────────────────────────────────
            st.subheader(
                f"📍 {result['resolved_name'].title()}  —  {result['state']} State"
            )

            # ── Metric cards ──────────────────────────────────────────────────
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Risk Level",      result["risk_level"])
            col2.metric("Total Incidents", result["total_incidents"])
            col3.metric("Total Deaths",    result["total_deaths"])
            col4.metric("Top Threat",      result["top_incident_type"])

            st.markdown("---")

            # ── Two-column layout: map + recent incidents ─────────────────────
            map_col, info_col = st.columns([3, 1])

            with map_col:
                st.markdown("#### 🗺️ Incident Map")

                map_path = build_location_map(
                    location_query.strip(), df, result
                )

                with open(map_path, "r", encoding="utf-8") as f:
                    map_html = f.read()

                st.components.v1.html(map_html, height=480, scrolling=False)

            with info_col:
                st.markdown("#### 🕒 Recent Incidents")

                if result["recent_incidents"]:
                    for inc in result["recent_incidents"]:
                        st.markdown(
                            f"""
                            <div style="
                                background:#1e1e2e;
                                border-left: 3px solid #e74c3c;
                                padding: 8px 12px;
                                border-radius: 4px;
                                margin-bottom: 8px;
                                font-size: 13px;
                            ">
                                {inc}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No recent incidents found.")

                st.markdown("---")
                st.markdown("#### 📌 Location Details")
                st.write(f"**State:** {result['state']}")
                st.write(
                    f"**Coordinates:** "
                    f"{result['coordinates']['lat']:.4f}, "
                    f"{result['coordinates']['lon']:.4f}"
                )
                st.write(f"**Source:** {result['geocode_source']}")

    elif search_clicked and not location_query.strip():
        st.warning("Please enter a location to search.")

    else:
        st.markdown(
            """
            <div style="
                text-align: center;
                padding: 60px 20px;
                color: #888;
            ">
                <h3>🔍 Enter a location above to begin</h3>
                <p>Try: <b>Lagos</b>, <b>Maiduguri</b>,
                <b>Abuja-Kaduna Road</b>, <b>Lekki</b>, <b>Ibadan</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================================
# FOOTER
# =========================================

st.markdown("---")
st.caption("Built with Machine Learning and Streamlit")