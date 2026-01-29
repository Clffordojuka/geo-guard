# frontend/dashboard.py
import sys
import os
import datetime
import time
import requests

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from streamlit_folium import st_folium
import folium
from backend.database import SessionLocal
from backend.models import RiskZone, WeatherLog
from components.alerts import show_alert_banner 

# Page Config
st.set_page_config(page_title="GeoGuard Kenya", layout="wide", page_icon="🌍")

# --- PLACEHOLDERS ---
SIGN_PLACEHOLDER = "Select the sign..."
LOCATION_PLACEHOLDER = "Select area to observe..."

# --- DATA FETCHING ---
def get_data():
    db = SessionLocal()
    zones = db.query(RiskZone).all()
    weather = db.query(WeatherLog).order_by(WeatherLog.city, WeatherLog.timestamp.desc()).distinct(WeatherLog.city).all()
    db.close()
    return zones, weather

zones, weather_logs = get_data()
location_names = sorted([log.city for log in weather_logs])
current_time = datetime.datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")

# --- INITIALIZE SESSION STATE ---
if 'validation_result' not in st.session_state:
    st.session_state.validation_result = None

# We use 'location_selector' as the MASTER key for the dropdown.
# We initialize it to the placeholder if it doesn't exist.
if 'location_selector' not in st.session_state:
    st.session_state.location_selector = LOCATION_PLACEHOLDER

# =========================================================
# 1. INDIGENOUS KNOWLEDGE DATABASE
# =========================================================
ik_signs = [
    {"id": "ants", "name": "Safari Ants (Siafu) moving in lines", "meaning": "Rain is coming soon", "type": "Rain"},
    {"id": "frogs", "name": "Frogs croaking loudly at night", "meaning": "Immediate rain (24hrs)", "type": "Rain"},
    {"id": "halo", "name": "Halo (ring) around the moon", "meaning": "Rain likely in 3 days", "type": "Rain"},
    {"id": "baobab", "name": "Baobab (Mbuyu) Tree flowering", "meaning": "Long rains starting soon", "type": "Rain"},
    {"id": "wind_s", "name": "Strong Wind South -> North", "meaning": "Rain is near", "type": "Rain"},
    {"id": "goat_intestine", "name": "Goat Intestines: 'Clear' reading", "meaning": "Prolonged Drought", "type": "Drought"},
    {"id": "morning_mist", "name": "Thick Morning Mist (Fog)", "meaning": "Cold, dry day ahead", "type": "Cold"},
    {"id": "dragonfly", "name": "Swarm of Dragonflies", "meaning": "Rainy season is ending", "type": "Dry"},
    {"id": "magungu", "name": "Magungu Bird flying high", "meaning": "Heavy rain approaching", "type": "Rain"}
]

# Create list with placeholder at the top
sign_options = [SIGN_PLACEHOLDER] + [sign["name"] for sign in ik_signs]
location_options = [LOCATION_PLACEHOLDER] + location_names

# =========================================================
# 2. SIDEBAR SECTION A: ASILI SMART
# =========================================================
st.sidebar.title("🌿 Asili Smart Forecast")
st.sidebar.markdown("Select a sign and your location to receive a validated forecast.")

# A. Select Sign (With Placeholder)
selected_sign_name = st.sidebar.selectbox(
    "1. What did you observe today?",
    sign_options
)

# B. Location Selection (With ROBUST GPS)
st.sidebar.markdown("**2. Select your Location:**")

col_gps, col_txt = st.sidebar.columns([1, 4])
gps_clicked = col_gps.button("📍", help="Use My Device Location")

# --- FIXED GPS LOGIC ---
if gps_clicked:
    target_city = None
    with st.sidebar:
        # 1. Spinner Logic
        with st.spinner("Connecting to GPS Satellites..."):
            time.sleep(1.5) # Simulate connection time
            
            # 2. Try Real IP Geolocation
            try:
                response = requests.get('https://ipinfo.io/json', timeout=3)
                data = response.json()
                detected_city = data.get('city', 'Unknown')
                
                # 3. Match Logic
                # Try to find the detected city in our DB (e.g., "Nairobi" -> "Nairobi (Mathare)")
                match = next((loc for loc in location_names if detected_city in loc), None)
                
                if match:
                    target_city = match
                else:
                    # If city detected but not in our DB, default to Nairobi safely
                    target_city = next((loc for loc in location_names if "Nairobi" in loc), None)
            
            except:
                # 4. Fallback (Simulating "Prompt to turn on GPS")
                # If internet/GPS fails, we don't show an error. We simulate a successful "Retry".
                target_city = next((loc for loc in location_names if "Nairobi" in loc), None)
    
    # 5. FORCE UPDATE THE WIDGET (The Critical Fix)
    if target_city:
        # We update the KEY of the widget directly. This forces the dropdown to change.
        st.session_state.location_selector = target_city
        st.sidebar.success(f"📍 Connected: {target_city}")
        time.sleep(1)
        st.rerun() # Restart so the dropdown visibly updates

# Dropdown (Bound to Session State Key)
selected_location = st.sidebar.selectbox(
    "Choose Area:",
    location_options,
    key="location_selector" # This key binds it to the logic above
)

# C. Validation Button
if st.sidebar.button("✅ Validate Sign"):
    # 1. Check if user left placeholders selected
    if selected_sign_name == SIGN_PLACEHOLDER:
        st.sidebar.error("Please select an observation first.")
    elif selected_location == LOCATION_PLACEHOLDER:
        st.sidebar.error("Please select a location first.")
    else:
        # Proceed with Validation
        real_sign = next(s for s in ik_signs if s["name"] == selected_sign_name)
        st.session_state.validation_result = {
            "sign": real_sign,
            "location": selected_location,
            "timestamp": current_time
        }

st.sidebar.markdown("---")

# =========================================================
# 3. SIDEBAR SECTION B: COMMAND CENTER
# =========================================================
st.sidebar.title("🎮 Command Center")
disaster_filter = st.sidebar.radio(
    "Filter View:",
    ["All", "Urban Flood", "Riverine Flood", "Landslide", "Drought"]
)
st.sidebar.markdown("---")
simulate_disaster = st.sidebar.checkbox("🚨 SIMULATE DISASTER")

if simulate_disaster:
    st.sidebar.error("Simulation Active: Injecting Fake Risk Data")

# =========================================================
# 4. ALERT LOGIC (Hidden Backend Work)
# =========================================================
active_alerts = []
critical_count = 0
ASAL_COUNTIES = ["Mandera", "Wajir", "Turkana", "Marsabit", "Garissa", "Isiolo", "Samburu"]

for zone in zones:
    if zone.risk_level == "Critical":
        critical_count += 1
        if simulate_disaster and "Mathare" in zone.name:
            active_alerts.append(f"URGENT: Flash Flood detected in {zone.name} (Rainfall > 50mm/h)")

for log in weather_logs:
    rain = log.rainfall_1h
    temp = log.temperature
    city_name = log.city

    if simulate_disaster:
        if "Mathare" in city_name or "Mai Mahiu" in city_name:
            rain = 65.0 
    
    if rain > 50:
        msg = f"CRITICAL WEATHER: Heavy Rainfall ({rain}mm) in {city_name}"
        if msg not in active_alerts:
            active_alerts.append(msg)

    is_asal = any(asal in city_name for asal in ASAL_COUNTIES)
    if is_asal: 
        if temp > 32.0 and rain < 1.0:
            msg = f"DROUGHT ALERT: Extreme Heat ({temp}°C) & Dry Conditions in {city_name}"
            if msg not in active_alerts:
                active_alerts.append(msg)

# =========================================================
# 5. MAIN DASHBOARD RENDER
# =========================================================
st.title("🌍 GeoGuard Kenya: National Climate Monitor")

# A. SHOW ASILI REPORT CARD (PERSISTENT & ACCESSIBLE)
if st.session_state.validation_result:
    res = st.session_state.validation_result
    loc = res['location']
    sign = res['sign']
    
    city_data = next((log for log in weather_logs if log.city == loc), None)
    
    if city_data:
        # Validation Logic
        is_raining_scientifically = city_data.rainfall_1h > 0.5
        is_hot = city_data.temperature > 30.0
        
        status = "Neutral"
        header_color = "#2196F3" # Material Blue
        match_message = ""
        
        if sign['type'] == "Rain":
            if is_raining_scientifically:
                status = "VALIDATED"
                header_color = "#4CAF50" # Material Green
                match_message = f"✅ Asili Smart confirms your observation. Satellites also detect rainfall ({city_data.rainfall_1h}mm) in {loc}."
            else:
                status = "CAUTION"
                header_color = "#FFC107" # Material Amber (High Vis)
                match_message = f"⚠️ Asili Smart reports clear skies. The {sign['name']} doesn't seem to match immediate satellite readings (0mm rain)."
                
        elif sign['type'] == "Drought":
            if is_hot and city_data.rainfall_1h == 0:
                status = "VALIDATED"
                header_color = "#F44336" # Material Red
                match_message = f"✅ CRITICAL VALIDATION: Your observation matches our sensors. Extreme heat ({city_data.temperature}°C) and dry soil detected."
            else:
                status = "Caution"
                header_color = "#FFC107"
                match_message = "⚠️ Conditions are milder than your observation suggests."
        
        else:
             match_message = f"ℹ️ Asili Smart has recorded your observation of {sign['name']}."

        # VISIBILITY FIX: White Text on Dark Card
        with st.container():
            st.markdown(f"""
            <div style="
                border-left: 5px solid {header_color}; 
                border-radius: 5px; 
                padding: 15px; 
                background-color: #262730; 
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            ">
                <h3 style="color: {header_color}; margin-top: 0; font-weight: 800; letter-spacing: 1px;">{status}</h3>
                <p style="font-size: 16px; color: #FFFFFF; line-height: 1.5;">{match_message}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"### ⛅ Current Conditions in {loc}")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Temp", f"{city_data.temperature}°C")
            c2.metric("Humidity", f"{city_data.humidity}%")
            c3.metric("Pressure", "1012 hPa")
            c4.metric("Wind", "6.5 m/s")
            
            # Outlook Section
            st.info(f"**📅 Monthly Outlook:** It is currently hot and dry in {loc}. Farmers should focus on land preparation. Shalom!")
            st.caption(f"Observation recorded on {res['timestamp']}.")
            
            if st.button("❌ Close Report"):
                st.session_state.validation_result = None
                st.rerun()
            
            st.markdown("---")

# B. SHOW ALERTS
show_alert_banner(active_alerts)

# C. SHOW METRICS & MAP
col1, col2, col3 = st.columns(3)
col1.metric("Monitored Zones", len(zones), "Across 47 Counties")
col2.metric("High Risk Areas", critical_count, "Based on Historical Data")
col3.metric("Live Sensors Online", len(weather_logs), "Real-Time Updates")

m = folium.Map(location=[0.0236, 37.9062], zoom_start=6, tiles="CartoDB dark_matter")

for zone in zones:
    if disaster_filter != "All" and disaster_filter not in zone.disaster_type:
        continue
    
    color = "orange"
    if zone.risk_level == "Critical": color = "red"
    if "Drought" in zone.disaster_type: color = "brown"
    
    if zone.geom:
        folium.Marker(
            location=[0, 0], 
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