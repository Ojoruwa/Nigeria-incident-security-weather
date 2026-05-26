import requests
import pandas as pd
import os

from dotenv import load_dotenv

# =========================================
# LOAD ENV VARIABLES
# =========================================

load_dotenv()

API_KEY = os.getenv(
    "OPENWEATHER_API_KEY"
)

# =========================================
# STATE COORDINATES
# =========================================

locations = {

    "Lagos": (6.5244, 3.3792),
    "Abuja": (9.0765, 7.3986),
    "Kano": (12.0022, 8.5920),
    "Kaduna": (10.5222, 7.4383),
    "Port Harcourt": (4.8156, 7.0498),
    "Ibadan": (7.3775, 3.9470),
    "Benin": (6.3350, 5.6037),
    "Maiduguri": (11.8469, 13.1603)
}

# =========================================
# STORAGE
# =========================================

weather_data = []

# =========================================
# FETCH LIVE WEATHER
# =========================================

for city, coords in locations.items():

    lat, lon = coords

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}"
        f"&lon={lon}"
        f"&appid={API_KEY}"
        "&units=metric"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()

        weather_data.append({

            "City": city,

            "Temperature": data["main"]["temp"],

            "Humidity": data["main"]["humidity"],

            "Weather": data["weather"][0]["main"],

            "Description": data["weather"][0]["description"],

            "WindSpeed": data["wind"]["speed"]
        })

        print(f"Fetched weather for {city}")

    except Exception as e:

        print(
            f"Error fetching {city}: {e}"
        )

# =========================================
# CREATE DATAFRAME
# =========================================

df = pd.DataFrame(weather_data)

# =========================================
# SAVE DATA
# =========================================

df.to_csv(
    "data/live_weather_data.csv",
    index=False
)

# =========================================
# OUTPUT
# =========================================

print("\nLIVE WEATHER DATA COMPLETE\n")

print(df)