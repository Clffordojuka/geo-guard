import sys
import os

# Added parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from streamlit_folium import st_folium
import folium
from backend.database import SessionLocal
from backend.models import RiskZone, WeatherLog

# IMPORT THE NEW COMPONENT
from components.alerts import show_alert_banner 

# Page Config
st.set_page_config(page_title="GeoGuard Kenya", layout="wide", page_icon="🌍")

# --- SIDEBAR & SIMULATION ---
st.sidebar.title("🎮 Command Center")
disaster_filter = st.sidebar.radio(
    "Filter View:",
    ["All", "Urban Flood", "Riverine Flood", "Landslide", "Drought"]
)

st.sidebar.markdown("---")
st.sidebar.header("⚠️ Simulation Mode")
simulate_disaster = st.sidebar.checkbox("🚨 SIMULATE DISASTER")

if simulate_disaster:
    st.sidebar.error("Simulation Active: Injecting Fake Risk Data")

# --- DATA FETCHING ---
def get_data():
    db = SessionLocal()
    zones = db.query(RiskZone).all()
    weather = db.query(WeatherLog).order_by(WeatherLog.city, WeatherLog.timestamp.desc()).distinct(WeatherLog.city).all()
    db.close()
    return zones, weather

zones, weather_logs = get_data()

# --- ALERT LOGIC ---
active_alerts = []
critical_count = 0

# 1. Define our specific "Drought Counties" for the logic
ASAL_COUNTIES = ["Mandera", "Wajir", "Turkana", "Marsabit", "Garissa", "Isiolo", "Samburu"]

for zone in zones:
    if zone.risk_level == "Critical":
        critical_count += 1
        # Simulation Logic for Mathare Flood
        if simulate_disaster and "Mathare" in zone.name:
            active_alerts.append(f"URGENT: Flash Flood detected in {zone.name} (Rainfall > 50mm/h)")

for log in weather_logs:
    rain = log.rainfall_1h
    temp = log.temperature
    city_name = log.city

    # --- SIMULATION OVERRIDES ---
    if simulate_disaster:
        if "Mathare" in city_name or "Mai Mahiu" in city_name:
            rain = 65.0 
    
    # --- REAL-WORLD DISASTER LOGIC ---
    
    # A. FLOOD LOGIC (Rainfall Threshold)
    if rain > 50:
        msg = f"CRITICAL WEATHER: Heavy Rainfall ({rain}mm) in {city_name}"
        if msg not in active_alerts:
            active_alerts.append(msg)

    # B. DROUGHT LOGIC (Heat + Dryness Threshold)
    # We check if the city is in our ASAL list AND matches conditions
    is_asal = any(asal in city_name for asal in ASAL_COUNTIES)
    
    if is_asal: 
        # Threshold: Hot (>32°C) and Dry (<1mm rain)
        if temp > 32.0 and rain < 1.0:
            msg = f"DROUGHT ALERT: Extreme Heat ({temp}°C) & Dry Conditions in {city_name}"
            if msg not in active_alerts:
                active_alerts.append(msg)

# --- DASHBOARD HEADER ---
st.title("🌍 GeoGuard Kenya: National Climate Monitor")

# --- CALL THE NEW ALERT COMPONENT ---
show_alert_banner(active_alerts)

# --- METRICS ---
col1, col2, col3 = st.columns(3)
col1.metric("Monitored Zones", len(zones), "Across 47 Counties")
col2.metric("High Risk Areas", critical_count, "Based on Historical Data")
col3.metric("Live Sensors Online", len(weather_logs), "Real-Time Updates")

# --- MAP RENDERER ---
m = folium.Map(location=[0.0236, 37.9062], zoom_start=6, tiles="CartoDB dark_matter")

for zone in zones:
    if disaster_filter != "All" and disaster_filter not in zone.disaster_type:
        continue
    
    color = "orange"
    if zone.risk_level == "Critical": color = "red"
    if "Drought" in zone.disaster_type: color = "brown"
    
    if zone.geom:
        folium.Marker(
            location=[0, 0], # Placeholder, handled by GeoJSON in real app
            popup=f"{zone.name}: {zone.risk_level}",
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(m)

for log in weather_logs:
    rain = log.rainfall_1h
    if simulate_disaster and ("Mathare" in log.city or "Mai Mahiu" in log.city):
        rain = 65.0
    
    icon_color = "green"
    if rain > 5: icon_color = "blue"
    if rain > 50: icon_color = "red" 
    
    folium.Marker(
        [log.lat, log.lon],
        popup=f"<b>{log.city}</b><br>Rain: {rain}mm",
        tooltip=f"{log.city}: {rain}mm",
        icon=folium.Icon(color=icon_color, icon="cloud")
    ).add_to(m)

st_folium(m, width="100%", height=600)

if st.button("🔄 Refresh Data"):
    st.rerun()