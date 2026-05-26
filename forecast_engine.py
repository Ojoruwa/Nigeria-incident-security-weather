import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

# =========================================
# LOAD DATA
# =========================================

df = pd.read_csv(
    "data/engineered_incidents.csv"
)

# =========================================
# CLEAN DATES
# =========================================

df["Year"] = pd.to_numeric(
    df["Year"],
    errors="coerce"
)

df["Month"] = pd.to_numeric(
    df["Month"],
    errors="coerce"
)

df = df.dropna(
    subset=["Year", "Month"]
)

# =========================================
# CREATE TIME INDEX
# =========================================

df["TimeIndex"] = (
    (df["Year"] - df["Year"].min()) * 12
    + df["Month"]
)

# =========================================
# AGGREGATE INCIDENTS
# =========================================

trend_df = df.groupby(
    "TimeIndex"
).size().reset_index()

trend_df.columns = [
    "TimeIndex",
    "IncidentCount"
]

# =========================================
# TRAIN MODEL
# =========================================

X = trend_df[["TimeIndex"]]

y = trend_df["IncidentCount"]

model = LinearRegression()

model.fit(X, y)

# =========================================
# FUTURE FORECAST
# =========================================

future_months = []

last_index = trend_df[
    "TimeIndex"
].max()

for i in range(1, 13):

    future_months.append(
        last_index + i
    )

future_X = pd.DataFrame({
    "TimeIndex": future_months
})

predictions = model.predict(
    future_X
)

# =========================================
# BUILD FORECAST TABLE
# =========================================

forecast_df = pd.DataFrame({

    "FutureMonthIndex": future_months,

    "PredictedIncidents": predictions
})

forecast_df["PredictedIncidents"] = (
    forecast_df["PredictedIncidents"]
    .round()
    .astype(int)
)

# =========================================
# RISK TREND
# =========================================

def risk_level(value):

    if value >= 250:
        return "Extreme"

    elif value >= 150:
        return "High"

    elif value >= 80:
        return "Moderate"

    return "Low"

forecast_df["ForecastRisk"] = forecast_df[
    "PredictedIncidents"
].apply(risk_level)

# =========================================
# SAVE FORECAST
# =========================================

forecast_df.to_csv(
    "data/forecast_predictions.csv",
    index=False
)

# =========================================
# OUTPUT
# =========================================

print("\nFORECAST ENGINE COMPLETE\n")

print(forecast_df)