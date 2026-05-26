import pandas as pd

# =========================================
# LOAD ENGINEERED DATA
# =========================================

df = pd.read_csv(
    "data/engineered_incidents.csv"
)

# =========================================
# STATE COORDINATES
# =========================================

state_coordinates = {

    "Lagos": (6.5244, 3.3792),
    "Ogun": (7.1608, 3.3486),
    "Oyo": (7.3775, 3.9470),
    "Osun": (7.5629, 4.5200),
    "Ondo": (7.2508, 5.2103),
    "Ekiti": (7.7190, 5.3110),

    "Kaduna": (10.5105, 7.4165),
    "Kano": (12.0022, 8.5920),
    "Katsina": (12.9908, 7.6018),
    "Jigawa": (12.2280, 9.5616),
    "Kebbi": (12.4539, 4.1975),
    "Sokoto": (13.0059, 5.2476),
    "Zamfara": (12.1704, 6.6641),

    "Benue": (7.3369, 8.7404),
    "Plateau": (9.2182, 9.5179),
    "Niger": (9.9309, 5.5983),
    "Kwara": (8.9669, 4.3874),
    "Kogi": (7.7337, 6.6906),
    "Nasarawa": (8.5378, 8.3086),
    "FCT": (9.0765, 7.3986),

    "Borno": (11.8846, 13.1510),
    "Yobe": (12.2939, 11.4390),
    "Adamawa": (9.3265, 12.3984),
    "Taraba": (7.9994, 10.7739),
    "Bauchi": (10.3158, 9.8442),
    "Gombe": (10.2796, 11.1732),

    "Rivers": (4.8156, 6.9780),
    "Delta": (5.7040, 5.9339),
    "Akwa Ibom": (5.0077, 7.8493),
    "Bayelsa": (4.7719, 6.0699),
    "Cross River": (5.8702, 8.5988),
    "Edo": (6.6342, 5.9304),

    "Abia": (5.4527, 7.5248),
    "Imo": (5.5720, 7.0588),
    "Anambra": (6.2209, 6.9369),
    "Ebonyi": (6.2649, 8.0137),
    "Enugu": (6.4584, 7.5464)
}

# =========================================
# ADD LAT/LON
# =========================================

def get_lat(state):

    if state in state_coordinates:
        return state_coordinates[state][0]

    return None

def get_lon(state):

    if state in state_coordinates:
        return state_coordinates[state][1]

    return None

df["Latitude"] = df["State"].apply(
    get_lat
)

df["Longitude"] = df["State"].apply(
    get_lon
)

# =========================================
# SAVE GEO DATA
# =========================================

df.to_csv(
    "data/geo_incidents.csv",
    index=False
)

print("\nGEO DATA CREATED SUCCESSFULLY")

print(df[[
    "State",
    "Latitude",
    "Longitude"
]].head(20))