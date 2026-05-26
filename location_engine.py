# location_engine.py

import pandas as pd
import re
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# ── Nigerian States List ──────────────────────────────────────────────────────
NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi",
    "Bayelsa", "Benue", "Borno", "Cross River", "Delta",
    "Ebonyi", "Edo", "Ekiti", "Enugu", "FCT", "Gombe",
    "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi",
    "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun",
    "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto",
    "Taraba", "Yobe", "Zamfara"
]

# ── Known Nigerian Routes & Areas ─────────────────────────────────────────────
KNOWN_ROUTES = {
    # Major Roads
    "lagos-ibadan expressway":    {"state": "Ogun",      "lat": 6.8956,  "lon": 3.7173},
    "abuja-kaduna road":          {"state": "Kaduna",    "lat": 10.5105, "lon": 7.4165},
    "abuja-lokoja road":          {"state": "Kogi",      "lat": 7.8069,  "lon": 6.7335},
    "benin-asaba road":           {"state": "Delta",     "lat": 6.2000,  "lon": 6.7333},
    "third mainland bridge":      {"state": "Lagos",     "lat": 6.4833,  "lon": 3.3833},
    "carter bridge":              {"state": "Lagos",     "lat": 6.4550,  "lon": 3.3900},

    # Lagos Areas
    "lekki":                      {"state": "Lagos",     "lat": 6.4698,  "lon": 3.5852},
    "ojota":                      {"state": "Lagos",     "lat": 6.5833,  "lon": 3.3833},
    "berger":                     {"state": "Lagos",     "lat": 6.6167,  "lon": 3.3500},
    "mile 2":                     {"state": "Lagos",     "lat": 6.4667,  "lon": 3.2833},
    "oshodi":                     {"state": "Lagos",     "lat": 6.5561,  "lon": 3.3514},
    "ikeja":                      {"state": "Lagos",     "lat": 6.6018,  "lon": 3.3515},
    "surulere":                   {"state": "Lagos",     "lat": 6.5059,  "lon": 3.3547},
    "ikorodu":                    {"state": "Lagos",     "lat": 6.6194,  "lon": 3.5106},
    "victoria island":            {"state": "Lagos",     "lat": 6.4281,  "lon": 3.4219},
    "apapa":                      {"state": "Lagos",     "lat": 6.4500,  "lon": 3.3667},
    "yaba":                       {"state": "Lagos",     "lat": 6.5095,  "lon": 3.3742},
    "lagos island":               {"state": "Lagos",     "lat": 6.4550,  "lon": 3.3940},

    # State Capitals & Major Cities
    "lagos":                      {"state": "Lagos",     "lat": 6.5244,  "lon": 3.3792},
    "ibadan":                     {"state": "Oyo",       "lat": 7.3775,  "lon": 3.9470},
    "oyo":                        {"state": "Oyo",       "lat": 7.8500,  "lon": 3.9300},
    "abuja":                      {"state": "FCT",       "lat": 9.0579,  "lon": 7.4951},
    "fct":                        {"state": "FCT",       "lat": 9.0579,  "lon": 7.4951},
    "kano":                       {"state": "Kano",      "lat": 12.0022, "lon": 8.5920},
    "kaduna":                     {"state": "Kaduna",    "lat": 10.5105, "lon": 7.4165},
    "port harcourt":              {"state": "Rivers",    "lat": 4.8156,  "lon": 7.0498},
    "maiduguri":                  {"state": "Borno",     "lat": 11.8333, "lon": 13.1500},
    "aba":                        {"state": "Abia",      "lat": 5.1066,  "lon": 7.3667},
    "enugu":                      {"state": "Enugu",     "lat": 6.4584,  "lon": 7.5464},
    "benin city":                 {"state": "Edo",       "lat": 6.3350,  "lon": 5.6270},
    "warri":                      {"state": "Delta",     "lat": 5.5167,  "lon": 5.7500},
    "zaria":                      {"state": "Kaduna",    "lat": 11.0667, "lon": 7.7000},
    "jos":                        {"state": "Plateau",   "lat": 9.9285,  "lon": 8.8921},
    "sokoto":                     {"state": "Sokoto",    "lat": 13.0622, "lon": 5.2339},
    "abeokuta":                   {"state": "Ogun",      "lat": 7.1557,  "lon": 3.3451},
    "akure":                      {"state": "Ondo",      "lat": 7.2526,  "lon": 5.1938},
    "oshogbo":                    {"state": "Osun",      "lat": 7.7827,  "lon": 4.5418},
    "osogbo":                     {"state": "Osun",      "lat": 7.7827,  "lon": 4.5418},
    "ilorin":                     {"state": "Kwara",     "lat": 8.5000,  "lon": 4.5500},
    "lokoja":                     {"state": "Kogi",      "lat": 7.8069,  "lon": 6.7335},
    "asaba":                      {"state": "Delta",     "lat": 6.2000,  "lon": 6.7333},
    "uyo":                        {"state": "Akwa Ibom", "lat": 5.0500,  "lon": 7.9333},
    "calabar":                    {"state": "Cross River","lat": 4.9500, "lon": 8.3250},
    "owerri":                     {"state": "Imo",       "lat": 5.4836,  "lon": 7.0333},
    "umuahia":                    {"state": "Abia",      "lat": 5.5333,  "lon": 7.4833},
    "awka":                       {"state": "Anambra",   "lat": 6.2104,  "lon": 7.0739},
    "onitsha":                    {"state": "Anambra",   "lat": 6.1667,  "lon": 6.7833},
    "bauchi":                     {"state": "Bauchi",    "lat": 10.3158, "lon": 9.8442},
    "gombe":                      {"state": "Gombe",     "lat": 10.2904, "lon": 11.1671},
    "yola":                       {"state": "Adamawa",   "lat": 9.2035,  "lon": 12.4954},
    "jalingo":                    {"state": "Taraba",    "lat": 8.8937,  "lon": 11.3597},
    "damaturu":                   {"state": "Yobe",      "lat": 11.7470, "lon": 11.9606},
    "dutse":                      {"state": "Jigawa",    "lat": 11.7904, "lon": 9.3437},
    "birnin kebbi":               {"state": "Kebbi",     "lat": 12.4539, "lon": 4.1975},
    "gusau":                      {"state": "Zamfara",   "lat": 12.1628, "lon": 6.6634},
    "lafia":                      {"state": "Nasarawa",  "lat": 8.4918,  "lon": 8.5137},
    "minna":                      {"state": "Niger",     "lat": 9.6139,  "lon": 6.5569},
    "makurdi":                    {"state": "Benue",     "lat": 7.7337,  "lon": 8.5374},
    "abakaliki":                  {"state": "Ebonyi",    "lat": 6.3249,  "lon": 8.1137},
    "ado ekiti":                  {"state": "Ekiti",     "lat": 7.6167,  "lon": 5.2167},
    "ikare":                      {"state": "Ondo",      "lat": 7.5333,  "lon": 5.7500},
    "katsina":                    {"state": "Katsina",   "lat": 12.9889, "lon": 7.6006},
}

# ── Classify incident type from title ─────────────────────────────────────────
def classify_incident(title):
    title = str(title).lower()
    if any(w in title for w in ["crash", "accident", "collision"]):
        return "Auto Crash"
    if any(w in title for w in ["gunmen", "killed", "attack", "bandit", "kidnap", "shooting", "murder"]):
        return "Violence"
    if any(w in title for w in ["fire", "burn", "inferno"]):
        return "Fire"
    if "flood" in title:
        return "Flood"
    if "poison" in title:
        return "Poisoning"
    if any(w in title for w in ["explosion", "blast", "bomb"]):
        return "Explosion"
    return "Other"


# ── Extract state from incident title using word boundaries ───────────────────
def extract_state(title):
    if not isinstance(title, str):
        return "Unknown"
    title_lower = title.lower()
    for state in NIGERIAN_STATES:
        pattern = r'\b' + re.escape(state.lower()) + r'\b'
        if re.search(pattern, title_lower):
            return state
    return "Unknown"


# ── Load & Prepare Dataset ────────────────────────────────────────────────────
def load_data(path="data/incidents.csv"):
    df = pd.read_csv(path)
    df["Number of deaths"] = pd.to_numeric(
        df["Number of deaths"], errors="coerce"
    ).fillna(0)
    df["Start date"] = pd.to_datetime(df["Start date"], errors="coerce")
    df["State"]    = df["Title"].apply(extract_state)
    df["Category"] = df["Title"].apply(classify_incident)
    return df


# ── Geocode: known routes first, then OpenStreetMap fallback ──────────────────
def geocode_location(query: str):
    q = query.strip().lower()

    # 1. Exact key match
    if q in KNOWN_ROUTES:
        val = KNOWN_ROUTES[q]
        return {
            "name": query,
            "state": val["state"],
            "lat": val["lat"],
            "lon": val["lon"],
            "source": "local"
        }

    # 2. Partial match — query contains a known key or vice versa
    for key, val in KNOWN_ROUTES.items():
        if key in q or q in key:
            return {
                "name": query,
                "state": val["state"],
                "lat": val["lat"],
                "lon": val["lon"],
                "source": "local"
            }

    # 3. Check if query matches a Nigerian state name directly
    for state in NIGERIAN_STATES:
        if q == state.lower():
            for key, val in KNOWN_ROUTES.items():
                if val["state"].lower() == state.lower():
                    return {
                        "name": query,
                        "state": state,
                        "lat": val["lat"],
                        "lon": val["lon"],
                        "source": "local"
                    }

    # 4. Fallback: OpenStreetMap Nominatim
    try:
        geolocator = Nominatim(user_agent="nigeria_incident_predictor_v2")
        location = geolocator.geocode(f"{query}, Nigeria", timeout=10)
        time.sleep(1)
        if location:
            state = "Unknown"
            for s in NIGERIAN_STATES:
                pattern = r'\b' + re.escape(s.lower()) + r'\b'
                if re.search(pattern, location.address.lower()):
                    state = s
                    break
            return {
                "name": query,
                "state": state,
                "lat": location.latitude,
                "lon": location.longitude,
                "source": "nominatim"
            }
    except GeocoderTimedOut:
        pass

    return None


# ── Build risk profile for a state ────────────────────────────────────────────
def state_risk_profile(state: str, df: pd.DataFrame) -> dict:
    state_df = df[df["State"].str.lower() == state.lower()]

    total_incidents = len(state_df)
    total_deaths    = int(state_df["Number of deaths"].sum())

    if total_incidents == 0:
        risk_level = "⚪ UNKNOWN"
        risk_score = 0
    elif total_deaths > 50 or total_incidents > 30:
        risk_level = "🔴 CRITICAL"
        risk_score = 5
    elif total_deaths > 20 or total_incidents > 15:
        risk_level = "🟠 HIGH"
        risk_score = 4
    elif total_deaths > 10 or total_incidents > 8:
        risk_level = "🟡 MODERATE"
        risk_score = 3
    elif total_incidents > 3:
        risk_level = "🟢 LOW"
        risk_score = 2
    else:
        risk_level = "⚪ MINIMAL"
        risk_score = 1

    recent = (
        state_df.sort_values("Start date", ascending=False)
        .head(3)["Title"]
        .tolist()
    )
    top_type = (
        state_df["Category"].mode()[0] if not state_df.empty else "N/A"
    )

    return {
        "state":            state,
        "total_incidents":  total_incidents,
        "total_deaths":     total_deaths,
        "risk_level":       risk_level,
        "risk_score":       risk_score,
        "top_incident_type": top_type,
        "recent_incidents": recent,
    }


# ── Main Query Function ───────────────────────────────────────────────────────
def query_location(user_input: str, df: pd.DataFrame) -> dict:
    geo = geocode_location(user_input)

    if geo is None:
        return {
            "error": True,
            "message": f"Could not resolve '{user_input}'. Try a state name, city, or known road."
        }

    profile = state_risk_profile(geo["state"], df)

    # ── Log query to database (never breaks main flow) ────────────────────────
    try:
        from database import log_query, save_risk_snapshot
        log_query(user_input, geo["state"], profile["risk_level"])
        save_risk_snapshot(
            geo["state"],
            profile["total_incidents"],
            profile["total_deaths"],
            profile["risk_level"]
        )
    except Exception:
        pass

    return {
        "error":          False,
        "query":          user_input,
        "resolved_name":  geo["name"],
        "state":          geo["state"],
        "coordinates":    {"lat": geo["lat"], "lon": geo["lon"]},
        "geocode_source": geo["source"],
        **profile
    }


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df = load_data()
    print("Nigeria Location Intelligence Engine")
    print("=" * 45)

    while True:
        user_query = input("\nEnter location (or 'quit'): ").strip()
        if user_query.lower() == "quit":
            break

        result = query_location(user_query, df)

        if result["error"]:
            print(f"\n❌ {result['message']}")
        else:
            print(f"\n📍 Location  : {result['resolved_name']}")
            print(f"🗺️  State      : {result['state']}")
            print(f"📊 Risk Level : {result['risk_level']}")
            print(f"💀 Deaths     : {result['total_deaths']}")
            print(f"📋 Incidents  : {result['total_incidents']}")
            print(f"⚠️  Top Type   : {result['top_incident_type']}")
            if result["recent_incidents"]:
                print(f"\n🕒 Recent Incidents:")
                for inc in result["recent_incidents"]:
                    print(f"   • {inc}")