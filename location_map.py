# location_map.py

import folium
import os
import numpy as np
import pandas as pd
from location_engine import load_data, geocode_location, extract_state

# ── Risk colour mapping ───────────────────────────────────────────────────────
RISK_COLOURS = {
    "🔴 CRITICAL": "red",
    "🟠 HIGH":     "orange",
    "🟡 MODERATE": "beige",
    "🟢 LOW":      "green",
    "⚪ MINIMAL":  "lightgray",
    "⚪ UNKNOWN":  "lightgray",
}

def risk_colour(risk_level: str) -> str:
    return RISK_COLOURS.get(risk_level, "lightgray")


# ── Build map for a queried location ─────────────────────────────────────────
def build_location_map(query: str, df: pd.DataFrame, result: dict) -> str:

    lat   = result["coordinates"]["lat"]
    lon   = result["coordinates"]["lon"]
    state = result["state"]
    risk  = result["risk_level"]

    # Centre map on queried location
    m = folium.Map(location=[lat, lon], zoom_start=9, tiles="CartoDB positron")

    # ── Queried location marker ───────────────────────────────────────────────
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(
            f"""
            <b>{query}</b><br>
            State: {state}<br>
            Risk: {risk}<br>
            Incidents: {result['total_incidents']}<br>
            Deaths: {result['total_deaths']}
            """,
            max_width=200
        ),
        tooltip=f"📍 {query}",
        icon=folium.Icon(color=risk_colour(risk), icon="star", prefix="fa")
    ).add_to(m)

    # ── Plot incidents in this state ──────────────────────────────────────────
    state_df = df[df["State"].str.lower() == state.lower()].copy()

    np.random.seed(42)

    plotted = 0
    for _, row in state_df.iterrows():
        jitter_lat = lat + np.random.uniform(-0.8, 0.8)
        jitter_lon = lon + np.random.uniform(-0.8, 0.8)

        deaths = int(row["Number of deaths"])
        title  = str(row["Title"])
        cat    = str(row.get("Category", "Other"))

        if deaths > 10:
            colour = "red"
        elif deaths > 4:
            colour = "orange"
        elif deaths > 0:
            colour = "beige"
        else:
            colour = "lightblue"

        folium.CircleMarker(
            location=[jitter_lat, jitter_lon],
            radius=5 + min(deaths, 10),
            color=colour,
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(
                f"<b>{title}</b><br>Deaths: {deaths}<br>Type: {cat}",
                max_width=220
            ),
            tooltip=f"{cat} — {deaths} deaths"
        ).add_to(m)
        plotted += 1

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_html = """
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                background: white; padding: 12px 16px; border-radius: 8px;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.3); font-size: 13px;">
        <b>Incident Severity</b><br>
        <span style="color:red;">●</span> 10+ deaths<br>
        <span style="color:orange;">●</span> 5–10 deaths<br>
        <span style="color:#c8b400;">●</span> 1–4 deaths<br>
        <span style="color:lightblue;">●</span> No deaths recorded<br>
        <span style="color:blue;">★</span> Queried location
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # ── Save ──────────────────────────────────────────────────────────────────
    BASE = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(BASE, "outputs", f"map_{state.lower().replace(' ', '_')}.html")
    m.save(output_path)
    print(f"\n✅ Map saved → {output_path}")
    print(f"   Plotted {plotted} incidents in {state} state.")
    return output_path


# ── CLI test ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from location_engine import query_location

    df = load_data()

    query = input("Enter location to map: ").strip()
    result = query_location(query, df)

    if result["error"]:
        print(f"❌ {result['message']}")
    else:
        print(f"📍 {result['resolved_name']} → {result['state']} state")
        build_location_map(query, df, result)
        print("Open the HTML file in your browser to view the map.")