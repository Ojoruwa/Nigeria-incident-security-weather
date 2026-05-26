import pandas as pd

# =========================================
# LOAD GEO DATA
# =========================================

df = pd.read_csv(
    "data/geo_incidents.csv"
)

# =========================================
# NIGERIA HIGHWAYS
# =========================================

routes = {

    "Abuja-Kaduna": [
        "FCT",
        "Kaduna"
    ],

    "Lagos-Ibadan": [
        "Lagos",
        "Oyo"
    ],

    "Benin-Ore": [
        "Edo",
        "Ondo"
    ],

    "Kaduna-Kano": [
        "Kaduna",
        "Kano"
    ],

    "Abuja-Lokoja": [
        "FCT",
        "Kogi"
    ],

    "Enugu-Port Harcourt": [
        "Enugu",
        "Rivers"
    ],

    "Sokoto-Zamfara": [
        "Sokoto",
        "Zamfara"
    ]
}

# =========================================
# CALCULATE ROUTE RISKS
# =========================================

route_results = []

for route_name, states in routes.items():

    route_df = df[
        df["State"].isin(states)
    ]

    total_incidents = len(route_df)

    total_deaths = route_df[
        "Number of deaths"
    ].sum()

    avg_bandit_score = route_df[
        "BanditScore"
    ].mean()

    avg_travel_risk = route_df[
        "TravelRiskScore"
    ].mean()

    # =====================================
    # RISK CLASSIFICATION
    # =====================================

    if avg_travel_risk >= 7:
        risk_level = "Extreme"

    elif avg_travel_risk >= 4:
        risk_level = "High"

    elif avg_travel_risk >= 2:
        risk_level = "Moderate"

    else:
        risk_level = "Low"

    route_results.append({

        "Route": route_name,

        "States": ", ".join(states),

        "Incidents": total_incidents,

        "Deaths": int(total_deaths),

        "BanditScore": round(
            avg_bandit_score,
            2
        ),

        "TravelRisk": round(
            avg_travel_risk,
            2
        ),

        "RiskLevel": risk_level
    })

# =========================================
# CREATE DATAFRAME
# =========================================

route_df = pd.DataFrame(
    route_results
)

# =========================================
# SAVE RESULTS
# =========================================

route_df.to_csv(
    "data/route_risk_analysis.csv",
    index=False
)

print("\nROUTE INTELLIGENCE COMPLETE\n")

print(route_df)