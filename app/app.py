import streamlit as st
import pandas as pd
import joblib

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Nigeria Incident Risk Predictor",
    page_icon="🚨",
    layout="wide"
)

# =========================================
# LOAD MODELS
# =========================================

model = joblib.load(
    "models/risk_model.pkl"
)

state_encoder = joblib.load(
    "models/state_encoder.pkl"
)

category_encoder = joblib.load(
    "models/category_encoder.pkl"
)

# =========================================
# TITLE
# =========================================

st.title("🚨 Nigeria Incident Risk Predictor")

st.markdown(
    """
This AI system predicts incident
risk levels across Nigeria using
Machine Learning.
"""
)

# =========================================
# SIDEBAR
# =========================================

st.sidebar.header("Prediction Inputs")

# =========================================
# STATE DROPDOWN
# =========================================

states = list(state_encoder.classes_)

selected_state = st.sidebar.selectbox(
    "Select State",
    states
)

# =========================================
# CATEGORY DROPDOWN
# =========================================

categories = list(category_encoder.classes_)

selected_category = st.sidebar.selectbox(
    "Select Incident Category",
    categories
)

# =========================================
# NUMBER INPUTS
# =========================================

deaths = st.sidebar.number_input(
    "Number of Deaths",
    min_value=0,
    max_value=1000,
    value=1
)

year = st.sidebar.number_input(
    "Year",
    min_value=2000,
    max_value=2100,
    value=2025
)

month = st.sidebar.slider(
    "Month",
    min_value=1,
    max_value=12,
    value=5
)

# =========================================
# PREDICTION BUTTON
# =========================================

if st.sidebar.button("Predict Risk"):

    # Encode inputs
    state_encoded = state_encoder.transform(
        [selected_state]
    )[0]

    category_encoded = category_encoder.transform(
        [selected_category]
    )[0]

    # Create dataframe
    input_data = pd.DataFrame({

        "StateEncoded": [state_encoded],

        "CategoryEncoded": [category_encoded],

        "Number of deaths": [deaths],

        "Year": [year],

        "Month": [month]

    })

    # Predict
    prediction = model.predict(
        input_data
    )[0]

    # =====================================
    # DISPLAY RESULTS
    # =====================================

    st.subheader("Prediction Result")

    if prediction == "Extreme":

        st.error(
            f"🚨 EXTREME RISK detected in {selected_state}"
        )

    elif prediction == "High":

        st.warning(
            f"⚠️ HIGH RISK detected in {selected_state}"
        )

    else:

        st.success(
            f"✅ LOW RISK detected in {selected_state}"
        )

    # =====================================
    # DETAILS
    # =====================================

    st.write("### Prediction Details")

    st.write(f"State: {selected_state}")
    st.write(f"Category: {selected_category}")
    st.write(f"Deaths: {deaths}")
    st.write(f"Year: {year}")
    st.write(f"Month: {month}")

# =========================================
# FOOTER
# =========================================

st.markdown("---")

st.caption(
    "Built with Machine Learning and Streamlit"
)