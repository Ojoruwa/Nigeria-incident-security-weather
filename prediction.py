import pandas as pd
import joblib

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
# USER INPUT
# =========================================

print("\n=== Nigeria Incident Risk Predictor ===\n")

state = input("Enter State: ")
category = input("Enter Incident Category: ")
deaths = int(input("Enter Number of Deaths: "))
year = int(input("Enter Year: "))
month = int(input("Enter Month (1-12): "))

# =========================================
# ENCODE INPUTS
# =========================================

try:

    state_encoded = state_encoder.transform(
        [state]
    )[0]

    category_encoded = category_encoder.transform(
        [category]
    )[0]

except:

    print("\nERROR:")
    print("Unknown State or Category")
    exit()

# =========================================
# CREATE INPUT DATA
# =========================================

input_data = pd.DataFrame({

    "StateEncoded": [state_encoded],

    "CategoryEncoded": [category_encoded],

    "Number of deaths": [deaths],

    "Year": [year],

    "Month": [month]

})

# =========================================
# PREDICT
# =========================================

prediction = model.predict(
    input_data
)[0]

# =========================================
# OUTPUT
# =========================================

print("\n===================================")
print(f"Predicted Risk Level: {prediction}")
print("===================================")