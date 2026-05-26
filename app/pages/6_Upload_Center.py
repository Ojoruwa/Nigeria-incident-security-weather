import streamlit as st
import pandas as pd
import plotly.express as px
import joblib

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Nigeria Intelligence Upload Center",
    page_icon="📂",
    layout="wide"
)

# =========================================
# LOAD MODEL
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
# HEADER
# =========================================

st.title("📂 Nigeria Intelligence Upload Center")

st.markdown("""
Upload intelligence datasets for:
- incident analysis
- hotspot detection
- risk prediction
- route intelligence
- AI forecasting
""")

# =========================================
# FILE UPLOADER
# =========================================

uploaded_file = st.file_uploader(

    "Upload CSV, Excel or JSON File",

    type=["csv", "xlsx", "json"]
)

# =========================================
# PROCESS FILE
# =========================================

if uploaded_file is not None:

    # =====================================
    # READ FILE
    # =====================================

    if uploaded_file.name.endswith(".csv"):

        df = pd.read_csv(uploaded_file)

    elif uploaded_file.name.endswith(".xlsx"):

        df = pd.read_excel(uploaded_file)

    elif uploaded_file.name.endswith(".json"):

        df = pd.read_json(uploaded_file)

    else:

        st.error("Unsupported file format")
        st.stop()

    # =====================================
    # PREVIEW
    # =====================================

    st.subheader("📄 Dataset Preview")

    st.dataframe(
        df.head(),
        use_container_width=True
    )

    # =====================================
    # REQUIRED COLUMNS
    # =====================================

    required_columns = [
        "State",
        "Category",
        "Number of deaths",
        "Year",
        "Month"
    ]

    missing = []

    for col in required_columns:

        if col not in df.columns:
            missing.append(col)

    # =====================================
    # VALIDATION
    # =====================================

    if len(missing) > 0:

        st.error(
            f"Missing Columns: {missing}"
        )

        st.stop()

    # =====================================
    # ENCODE DATA
    # =====================================

    try:

        df["StateEncoded"] = state_encoder.transform(
            df["State"]
        )

        df["CategoryEncoded"] = category_encoder.transform(
            df["Category"]
        )

    except Exception as e:

        st.error(
            f"Encoding Error: {e}"
        )

        st.stop()

    # =====================================
    # FEATURES
    # =====================================

    X = df[[
        "StateEncoded",
        "CategoryEncoded",
        "Number of deaths",
        "Year",
        "Month"
    ]]

    # =====================================
    # PREDICT
    # =====================================

    predictions = model.predict(X)

    df["PredictedRisk"] = predictions

    # =====================================
    # METRICS
    # =====================================

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Records",
        len(df)
    )

    col2.metric(
        "Extreme Risks",
        len(
            df[
                df["PredictedRisk"] == "Extreme"
            ]
        )
    )

    col3.metric(
        "High Risks",
        len(
            df[
                df["PredictedRisk"] == "High"
            ]
        )
    )

    # =====================================
    # RISK DISTRIBUTION
    # =====================================

    st.subheader("🚨 Predicted Risk Distribution")

    risk_counts = df[
        "PredictedRisk"
    ].value_counts().reset_index()

    risk_counts.columns = [
        "Risk",
        "Count"
    ]

    fig1 = px.bar(

        risk_counts,

        x="Risk",

        y="Count",

        color="Risk",

        text_auto=True
    )

    fig1.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    # =====================================
    # STATE ANALYSIS
    # =====================================

    st.subheader("🔥 State Risk Analysis")

    state_counts = df[
        "State"
    ].value_counts().reset_index()

    state_counts.columns = [
        "State",
        "Incidents"
    ]

    fig2 = px.pie(

        state_counts,

        names="State",

        values="Incidents",

        hole=0.5
    )

    fig2.update_layout(
        template="plotly_dark",
        height=600
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # =====================================
    # RESULTS TABLE
    # =====================================

    st.subheader("📊 AI Intelligence Results")

    st.dataframe(
        df,
        use_container_width=True
    )

    # =====================================
    # DOWNLOAD RESULTS
    # =====================================

    csv = df.to_csv(index=False)

    st.download_button(

        label="⬇ Download Intelligence Report",

        data=csv,

        file_name="ai_intelligence_report.csv",

        mime="text/csv"
    )

# =========================================
# FOOTER
# =========================================

st.markdown("---")

st.caption(
    "Nigeria AI Intelligence Upload System"
)