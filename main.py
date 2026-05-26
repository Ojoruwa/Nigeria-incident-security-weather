import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

# =========================================
# LOAD DATASET
# =========================================

df = pd.read_csv("data/incidents.csv")

print("Dataset Loaded Successfully")

# =========================================
# CLEAN NUMBER OF DEATHS
# =========================================

df["Number of deaths"] = pd.to_numeric(
    df["Number of deaths"],
    errors="coerce"
)

df["Number of deaths"] = df["Number of deaths"].fillna(0)

# =========================================
# SAFE DATE CONVERSION
# =========================================

df["Start date"] = pd.to_datetime(
    df["Start date"],
    errors="coerce"
)

df["End date"] = pd.to_datetime(
    df["End date"],
    errors="coerce"
)

# Remove invalid dates
df = df.dropna(subset=["Start date"])

# =========================================
# CREATE YEAR + MONTH
# =========================================

df["Year"] = df["Start date"].dt.year
df["Month"] = df["Start date"].dt.month

# =========================================
# NIGERIAN STATES
# =========================================

states = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra",
    "Bauchi", "Bayelsa", "Benue", "Borno",
    "Cross River", "Delta", "Ebonyi", "Edo",
    "Ekiti", "Enugu", "FCT", "Gombe",
    "Imo", "Jigawa", "Kaduna", "Kano",
    "Katsina", "Kebbi", "Kogi", "Kwara",
    "Lagos", "Nasarawa", "Niger", "Ogun",
    "Ondo", "Osun", "Oyo", "Plateau",
    "Rivers", "Sokoto", "Taraba", "Yobe",
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

df["State"] = df["Title"].apply(extract_state)

# =========================================
# INCIDENT CLASSIFICATION
# =========================================

categories = {

    "Auto Crash": [
        "crash",
        "accident",
        "collision"
    ],

    "Gun Violence": [
        "gunmen",
        "shoot",
        "bullet",
        "attack",
        "bandit",
        "kill",
        "killed"
    ],

    "Explosion": [
        "explosion",
        "blast",
        "bomb"
    ],

    "Fire Outbreak": [
        "fire",
        "burn"
    ],

    "Flood": [
        "flood"
    ],

    "Poisoning": [
        "poison"
    ],

    "Stampede": [
        "stampede"
    ],

    "Communal Clash": [
        "clash"
    ]
}

# =========================================
# CLASSIFY INCIDENT
# =========================================

def classify_incident(title):

    if pd.isna(title):
        return "Other"

    title = str(title).lower()

    for category, keywords in categories.items():

        for keyword in keywords:

            if keyword in title:
                return category

    return "Other"

df["Category"] = df["Title"].apply(classify_incident)

# =========================================
# CREATE RISK LABELS
# =========================================

def create_risk(deaths):

    if deaths >= 10:
        return "Extreme"

    elif deaths >= 3:
        return "High"

    else:
        return "Low"

df["Risk"] = df["Number of deaths"].apply(create_risk)

# =========================================
# ENCODE DATA
# =========================================

state_encoder = LabelEncoder()
category_encoder = LabelEncoder()

df["StateEncoded"] = state_encoder.fit_transform(
    df["State"]
)

df["CategoryEncoded"] = category_encoder.fit_transform(
    df["Category"]
)

# =========================================
# FEATURES + LABELS
# =========================================

X = df[[
    "StateEncoded",
    "CategoryEncoded",
    "Number of deaths",
    "Year",
    "Month"
]]

y = df["Risk"]

# =========================================
# SPLIT DATA
# =========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# =========================================
# TRAIN MODEL
# =========================================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# =========================================
# PREDICT
# =========================================

predictions = model.predict(X_test)

# =========================================
# EVALUATE
# =========================================

accuracy = accuracy_score(
    y_test,
    predictions
)

print("\nMODEL ACCURACY:")
print(f"{accuracy * 100:.2f}%")

print("\nCLASSIFICATION REPORT:")
print(classification_report(
    y_test,
    predictions
))

print("\nCONFUSION MATRIX:")
print(confusion_matrix(
    y_test,
    predictions
))

# =========================================
# SAVE MODELS
# =========================================

joblib.dump(
    model,
    "models/risk_model.pkl"
)

joblib.dump(
    state_encoder,
    "models/state_encoder.pkl"
)

joblib.dump(
    category_encoder,
    "models/category_encoder.pkl"
)

print("\nMODEL SAVED SUCCESSFULLY")