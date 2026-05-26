import pandas as pd

# =========================================
# LOAD DATA
# =========================================

df = pd.read_csv(
    "data/incidents.csv"
)

print("\nDATASET LOADED\n")

# =========================================
# CLEAN DEATHS
# =========================================

df["Number of deaths"] = pd.to_numeric(
    df["Number of deaths"],
    errors="coerce"
)

df["Number of deaths"] = df[
    "Number of deaths"
].fillna(0)

# =========================================
# DETECT DATE COLUMN
# =========================================

possible_date_columns = [

    "Date",
    "date",
    "Incident Date",
    "incident_date",
    "Event Date",
    "event_date"
]

date_column = None

for col in possible_date_columns:

    if col in df.columns:
        date_column = col
        break

# =========================================
# CREATE YEAR + MONTH
# =========================================

if date_column is not None:

    print(f"\nUsing date column: {date_column}\n")

    df[date_column] = pd.to_datetime(
        df[date_column],
        errors="coerce",
        format="mixed"
    )

    df["Year"] = df[
        date_column
    ].dt.year

    df["Month"] = df[
        date_column
    ].dt.month

else:

    print(
        "\nWARNING: No date column found."
    )

    print(
        "Using default Year=2024 and Month=1\n"
    )

    df["Year"] = 2024

    df["Month"] = 1

# =========================================
# FILL MISSING DATES
# =========================================

df["Year"] = df["Year"].fillna(2024)

df["Month"] = df["Month"].fillna(1)

df["Year"] = df["Year"].astype(int)

df["Month"] = df["Month"].astype(int)

# =========================================
# STATES
# =========================================

states = [

    "Abia", "Adamawa", "Akwa Ibom",
    "Anambra", "Bauchi", "Bayelsa",
    "Benue", "Borno", "Cross River",
    "Delta", "Ebonyi", "Edo",
    "Ekiti", "Enugu", "FCT",
    "Gombe", "Imo", "Jigawa",
    "Kaduna", "Kano", "Katsina",
    "Kebbi", "Kogi", "Kwara",
    "Lagos", "Nasarawa", "Niger",
    "Ogun", "Ondo", "Osun",
    "Oyo", "Plateau", "Rivers",
    "Sokoto", "Taraba", "Yobe",
    "Zamfara"
]

# =========================================
# EXTRACT STATE
# =========================================

def extract_state(title):

    if pd.isna(title):
        return "Unknown"

    title = str(title).lower()

    for state in states:

        if state.lower() in title:
            return state

    return "Unknown"

df["State"] = df["Title"].apply(
    extract_state
)

# =========================================
# REGION MAP
# =========================================

region_map = {

    "Lagos": "South West",
    "Ogun": "South West",
    "Oyo": "South West",
    "Ondo": "South West",
    "Osun": "South West",
    "Ekiti": "South West",

    "Kaduna": "North West",
    "Kano": "North West",
    "Katsina": "North West",
    "Kebbi": "North West",
    "Sokoto": "North West",
    "Zamfara": "North West",
    "Jigawa": "North West",

    "Benue": "North Central",
    "Plateau": "North Central",
    "Niger": "North Central",
    "Kogi": "North Central",
    "Kwara": "North Central",
    "Nasarawa": "North Central",
    "FCT": "North Central",

    "Borno": "North East",
    "Yobe": "North East",
    "Adamawa": "North East",
    "Taraba": "North East",
    "Bauchi": "North East",
    "Gombe": "North East",

    "Rivers": "South South",
    "Delta": "South South",
    "Akwa Ibom": "South South",
    "Bayelsa": "South South",
    "Cross River": "South South",
    "Edo": "South South",

    "Abia": "South East",
    "Imo": "South East",
    "Anambra": "South East",
    "Ebonyi": "South East",
    "Enugu": "South East"
}

df["Region"] = df["State"].map(
    region_map
)

# =========================================
# BANDIT KEYWORDS
# =========================================

bandit_keywords = [

    "bandit",
    "kidnap",
    "gunmen",
    "terrorist",
    "attack",
    "herdsmen"
]

# =========================================
# BANDIT SCORE
# =========================================

def bandit_score(title):

    if pd.isna(title):
        return 0

    title = str(title).lower()

    score = 0

    for word in bandit_keywords:

        if word in title:
            score += 1

    return score

df["BanditScore"] = df["Title"].apply(
    bandit_score
)

# =========================================
# TRAVEL RISK
# =========================================

def travel_risk(row):

    score = 0

    if row["Number of deaths"] >= 10:
        score += 5

    elif row["Number of deaths"] >= 3:
        score += 3

    if row["BanditScore"] > 0:
        score += 5

    return score

df["TravelRiskScore"] = df.apply(
    travel_risk,
    axis=1
)

# =========================================
# ROUTE ALERTS
# =========================================

def route_alert(score):

    if score >= 8:
        return "Avoid Route"

    elif score >= 4:
        return "Caution"

    return "Safe"

df["RouteAlert"] = df[
    "TravelRiskScore"
].apply(route_alert)

# =========================================
# SAVE FILE
# =========================================

df.to_csv(
    "data/engineered_incidents.csv",
    index=False
)

print("\nFEATURE ENGINEERING COMPLETE\n")

print(df.head())