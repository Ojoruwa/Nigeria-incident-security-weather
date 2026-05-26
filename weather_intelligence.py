import pandas as pd
import random

# =========================================
# LOAD ENGINEERED DATA
# =========================================

df = pd.read_csv(
    "data/engineered_incidents.csv"
)

# =========================================
# NIGERIA WEATHER ZONES
# =========================================

high_rainfall_states = [

    "Lagos",
    "Rivers",
    "Bayelsa",
    "Delta",
    "Akwa Ibom",
    "Cross River"
]

medium_rainfall_states = [

    "Ogun",
    "Ondo",
    "Edo",
    "Anambra",
    "Enugu",
    "Abia",
    "Imo"
]

# =========================================
# WEATHER SCORE
# =========================================

def weather_risk(state):

    if state in high_rainfall_states:

        rainfall = random.randint(80, 100)

        flood_risk = "High"

        weather_score = 5

    elif state in medium_rainfall_states:

        rainfall = random.randint(50, 79)

        flood_risk = "Moderate"

        weather_score = 3

    else:

        rainfall = random.randint(10, 49)

        flood_risk = "Low"

        weather_score = 1

    return pd.Series([

        rainfall,
        flood_risk,
        weather_score
    ])

# =========================================
# APPLY WEATHER ANALYSIS
# =========================================

df[[
    "RainfallLevel",
    "FloodRisk",
    "WeatherRiskScore"
]] = df["State"].apply(weather_risk)

# =========================================
# COMBINED RISK SCORE
# =========================================

df["CombinedRiskScore"] = (

    df["TravelRiskScore"] +

    df["WeatherRiskScore"] +

    df["BanditScore"]
)

# =========================================
# COMBINED ALERT
# =========================================

def combined_alert(score):

    if score >= 12:
        return "Extreme Danger"

    elif score >= 8:
        return "High Risk"

    elif score >= 4:
        return "Moderate Risk"

    return "Low Risk"

df["CombinedAlert"] = df[
    "CombinedRiskScore"
].apply(combined_alert)

# =========================================
# SAVE DATA
# =========================================

df.to_csv(
    "data/weather_intelligence.csv",
    index=False
)

# =========================================
# OUTPUT
# =========================================

print("\nWEATHER INTELLIGENCE COMPLETE\n")

print(df[[
    "State",
    "RainfallLevel",
    "FloodRisk",
    "CombinedRiskScore",
    "CombinedAlert"
]].head())