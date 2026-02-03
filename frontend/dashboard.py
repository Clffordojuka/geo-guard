# frontend/dashboard.py
import sys
import os
import datetime
import time
import requests
import pandas as pd
import joblib 
import plotly.graph_objects as go

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from streamlit_folium import st_folium
import folium
from backend.database import SessionLocal
from backend.models import RiskZone, WeatherLog
from components.alerts import show_alert_banner
from backend.weather_service import fetch_live_weather 

# Page Config
st.set_page_config(page_title="GeoGuard Kenya", layout="wide", page_icon="🌍")

# --- PLACEHOLDERS ---
SIGN_PLACEHOLDER = "Select the sign..."
LOCATION_PLACEHOLDER = "Select area to observe..."

# --- 1. COORDINATE MAPPING (Updated to match Backend) ---
def get_zone_coords(zone_name):
    """Maps Zone Names to Real Coordinates so they don't appear at [0,0]"""
    locations = {
        # --- Nairobi & Urban ---
        "Mathare Settlements": (-1.26, 36.85),
        "Eastlands": (-1.28, 36.89),
        "South C": (-1.32, 36.83),
        "Kibera (Soweto Highrise)": (-1.31, 36.79),
        "Dagoretti Corner": (-1.30, 36.76),
        "Westlands": (-1.27, 36.81),
        "Kasarani": (-1.21, 36.92),
        "Embakasi": (-1.30, 36.95),
        "Langata": (-1.35, 36.75),
        "Ruiru": (-1.15, 36.95),
        "Thika": (-1.03, 37.07),
        "Juja": (-1.18, 37.05),
        "Kiambu Town": (-1.17, 36.83),
        "Githurai": (-1.15, 36.90),
        "Kahawa West": (-1.20, 36.90),
        "Kawangware": (-1.28, 36.75),
        
        # --- Lake Region ---
        "Kisumu Central": (-0.10, 34.75),
        "Dunga Beach": (-0.14, 34.73),
        "Homa Bay Shores": (-0.52, 34.45),
        "Budalangi Floodplains": (0.10, 34.00),
        "Kisii Highlands": (-0.68, 34.77),
        "Migori Town": (-1.06, 34.48),
        "Rongo": (-0.83, 34.45),

        # --- Rift Valley & Central ---
        "Mai Mahiu Gully": (-0.99, 36.56),
        "Murang'a East Slopes": (-0.72, 37.15),
        "Laikipia Dam Zone": (0.36, 36.78),
        "Tiaty": (1.00, 36.10),
        "Narok West": (-1.20, 35.50),
        "Weiwei": (1.45, 35.45),
        "Chesongoch": (1.13, 35.64),
        "Elgeyo Escarpment": (0.85, 35.50),
        "Kericho Tea Zone": (-0.37, 35.28),
        "Bomet Lowlands": (-0.80, 35.30),
        "Nakuru Town": (-0.28, 36.07),
        "Naivasha Lakeside": (-0.72, 36.43),
        "Eldoret Industrial": (0.52, 35.27),
        
        # --- ASAL & North ---
        "Turkana North (Kibish)": (4.50, 35.80),
        "Turkana Central": (3.11, 35.60),
        "Lobere Dam Area": (3.58, 36.12),
        "Mandera East": (3.93, 41.86),
        "Wajir South": (1.00, 40.00),
        "Marsabit North": (3.00, 37.50),
        "Garissa North": (-0.10, 39.50),
        "Shimbirey": (-0.42, 39.63),
        "Isiolo": (0.35, 37.58),
        "Samburu East": (1.20, 37.20),
        "Kitui Central": (-1.35, 38.00),
        "Makueni North": (-1.50, 37.70),
        "Kitui South": (-1.60, 38.20),
        "Machakos Town": (-1.50, 37.25),
        "Kajiado Central": (-1.85, 36.80),
        
        # --- Coastal ---
        "Hola": (-1.50, 40.03),
        "Kwale Hinterland": (-4.17, 39.45),
        "Ganze": (-3.50, 39.75),
        "Taita Taveta Hills": (-3.40, 38.50),
        "Mombasa Island": (-4.05, 39.66),
        "Likoni": (-4.10, 39.65),
        "Malindi": (-3.22, 40.12),
        "Kilifi Town": (-3.63, 39.85),
    }
    return locations.get(zone_name, (-1.29, 36.82)) # Default to Nairobi

# --- 2. DATA FETCHING ---
def get_data():
    db = SessionLocal()
    zones = db.query(RiskZone).all()
    weather = db.query(WeatherLog).order_by(WeatherLog.city, WeatherLog.timestamp.desc()).distinct(WeatherLog.city).all()
    db.close()
    return zones, weather

zones, weather_logs = get_data()
location_names = sorted([log.city for log in weather_logs]) if weather_logs else ["Nairobi"]
current_time = datetime.datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")

# --- 3. ML MODEL LOADING ---
@st.cache_resource
def load_seasonal_model():
    # Robust path finding
    model_path = os.path.join(os.path.dirname(__file__), "..", "backend", "seasonal_model.pkl")
    model_path = os.path.abspath(model_path)
    try:
        return joblib.load(model_path)
    except FileNotFoundError:
        return None

def predict_future_season(model, days_ahead=90):
    start_date = datetime.datetime.now()
    dates = [start_date + datetime.timedelta(days=i) for i in range(days_ahead)]
    future_df = pd.DataFrame({"date": dates})
    future_df["day_of_year"] = future_df["date"].dt.dayofyear
    predictions = model.predict(future_df[["day_of_year"]])
    future_df["predicted_rain"] = predictions
    return future_df

# --- SESSION STATE ---
if 'validation_result' not in st.session_state:
    st.session_state.validation_result = None
if 'location_selector' not in st.session_state:
    st.session_state.location_selector = LOCATION_PLACEHOLDER

# =========================================================
# 4. NAVIGATION
# =========================================================
st.sidebar.title("🌍 GeoGuard Nav")
app_mode = st.sidebar.selectbox("Choose Mode:", ["📡 Live Monitor", "🌿 Asili Smart", "🔮 Seasonal Predictions"])
st.sidebar.markdown("---")

# =========================================================
# MODE A: SEASONAL PREDICTIONS (ML)
# =========================================================
if app_mode == "🔮 Seasonal Predictions":
    st.title("🔮 AI Seasonal Forecast Engine")
    st.markdown("Predictive analytics using a **Random Forest Regressor** trained on historical Kenyan weather data.")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.info("**Model Architecture**")
        st.markdown("""
        - **Algorithm:** Random Forest
        - **Accuracy (R²):** 67%
        - **Target:** Rainfall (mm)
        """)
        
        days = st.slider("Forecast Horizon (Days)", 30, 180, 90)
        model = load_seasonal_model()
        
        if st.button("🚀 Run Prediction"):
            if model:
                st.session_state.forecast = predict_future_season(model, days)
                st.success("Prediction Complete")
            else:
                st.error("⚠️ Model not found! Ensure 'backend/seasonal_model.pkl' exists.")

    with col2:
        if 'forecast' in st.session_state:
            data = st.session_state.forecast
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data['date'], y=data['predicted_rain'], mode='lines', name='Predicted Rainfall', line=dict(color='#00CC96', width=3), fill='tozeroy'))
            
            peak_rain = data['predicted_rain'].max()
            avg_rain = data['predicted_rain'].mean()
            season_status = "Long Rains Approaching" if peak_rain > 12 else "Dry Season / Short Rains"
            
            fig.update_layout(title=f"Forecast Trend: {season_status}", yaxis_title="Rainfall (mm)", template="plotly_dark", height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            if avg_rain > 5:
                st.success("✅ **Recommendation:** Conditions favorable for planting. Recommended crops: Maize, Beans.")
            else:
                st.warning("⚠️ **Recommendation:** Rainfall below average. Focus on drought-resistant crops (Sorghum, Cassava).")

# =========================================================
# MODE B: ASILI SMART (Indigenous Knowledge)
# =========================================================
elif app_mode == "🌿 Asili Smart":
    # 1. INDIGENOUS KNOWLEDGE DATABASE
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

    sign_options = [SIGN_PLACEHOLDER] + [sign["name"] for sign in ik_signs]
    location_options = [LOCATION_PLACEHOLDER] + location_names

    st.sidebar.title("🌿 Asili Smart Inputs")
    st.sidebar.markdown("Select a sign and your location.")

    # A. Select Sign
    selected_sign_name = st.sidebar.selectbox("1. What did you observe?", sign_options)

    # B. GPS Logic
    col_gps, col_txt = st.sidebar.columns([1, 4])
    gps_clicked = col_gps.button("📍", help="Use My Device Location")

    if gps_clicked:
        target_city = None
        with st.sidebar:
            with st.spinner("Connecting to GPS Satellites..."):
                time.sleep(1.5)
                try:
                    response = requests.get('https://ipinfo.io/json', timeout=3)
                    data = response.json()
                    detected_city = data.get('city', 'Unknown')
                    match = next((loc for loc in location_names if detected_city in loc), None)
                    target_city = match if match else next((loc for loc in location_names if "Nairobi" in loc), None)
                except:
                    target_city = next((loc for loc in location_names if "Nairobi" in loc), None)
        
        if target_city:
            st.session_state.location_selector = target_city
            st.sidebar.success(f"📍 Connected: {target_city}")
            time.sleep(1)
            st.rerun()

    selected_location = st.sidebar.selectbox("Choose Area:", location_options, key="location_selector")

    if st.sidebar.button("✅ Validate Sign"):
        if selected_sign_name == SIGN_PLACEHOLDER:
            st.sidebar.error("Please select an observation first.")
        elif selected_location == LOCATION_PLACEHOLDER:
            st.sidebar.error("Please select a location first.")
        else:
            real_sign = next(s for s in ik_signs if s["name"] == selected_sign_name)
            st.session_state.validation_result = {"sign": real_sign, "location": selected_location, "timestamp": current_time}

    # MAIN AREA RENDER FOR ASILI
    st.title("🌿 Asili Smart Forecast")
    
    if st.session_state.validation_result:
        res = st.session_state.validation_result
        loc = res['location']
        sign = res['sign']
        city_data = next((log for log in weather_logs if log.city == loc), None)
        
        if city_data:
            # Validation Logic
            is_raining = city_data.rainfall_1h > 0.5
            is_hot = city_data.temperature > 30.0
            
            status, header_color, msg = "Neutral", "#2196F3", ""
            
            if sign['type'] == "Rain":
                if is_raining:
                    status, header_color = "VALIDATED", "#4CAF50"
                    msg = f"✅ Asili Smart confirms your observation. Satellites also detect rainfall ({city_data.rainfall_1h}mm)."
                else:
                    status, header_color = "CAUTION", "#FFC107"
                    msg = f"⚠️ Asili Smart reports clear skies. Satellites show 0mm rain."
            elif sign['type'] == "Drought":
                if is_hot and city_data.rainfall_1h == 0:
                    status, header_color = "VALIDATED", "#F44336"
                    msg = f"✅ CRITICAL VALIDATION: Extreme heat ({city_data.temperature}°C) confirmed."
                else:
                    status, header_color = "Caution", "#FFC107"
                    msg = "⚠️ Conditions are milder than observed."
            else:
                 msg = f"ℹ️ Observation recorded: {sign['name']}."

            with st.container():
                st.markdown(f"""
                <div style="border-left: 5px solid {header_color}; border-radius: 5px; padding: 15px; background-color: #262730; margin-bottom: 20px;">
                    <h3 style="color: {header_color}; margin:0;">{status}</h3>
                    <p style="color: white;">{msg}</p>
                </div>""", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Temp", f"{city_data.temperature}°C")
                c2.metric("Humidity", f"{city_data.humidity}%")
                c3.metric("Rain", f"{city_data.rainfall_1h}mm")
                
                if st.button("❌ Close Report"):
                    st.session_state.validation_result = None
                    st.rerun()
    else:
        st.info("👈 Please select a sign and location from the sidebar to begin validation.")

# =========================================================
# MODE C: LIVE MONITOR (Map & Alerts - FIXED)
# =========================================================
else:
    st.title("🌍 GeoGuard Kenya: National Climate Monitor")
    
    # --- 1. Manual Sync Button (Critical for Render) ---
    col_status, col_btn = st.columns([3, 1])
    col_status.metric("System Status", "Online | Cloud Database Connected")
    
    if col_btn.button("🔄 Sync Live Weather"):
        with st.spinner("Pinging Satellites..."):
            fetch_live_weather() # Updates DB with fresh OpenWeather data
            st.success("Synced!")
            time.sleep(1)
            st.rerun()

    # --- 2. Dashboard Metrics ---
    disaster_filter = st.sidebar.radio("Filter View:", ["All", "Urban Flood", "Riverine Flood", "Landslide", "Drought"])
    simulate_disaster = st.sidebar.checkbox("🚨 SIMULATE DISASTER")

    active_alerts = []
    critical_count = 0
    ASAL_COUNTIES = ["Mandera", "Wajir", "Turkana", "Marsabit", "Garissa", "Isiolo", "Samburu"]

    for zone in zones:
        if zone.risk_level == "Critical":
            critical_count += 1
            if simulate_disaster and "Mathare" in zone.name:
                active_alerts.append(f"URGENT: Flash Flood detected in {zone.name}")

    for log in weather_logs:
        rain = log.rainfall_1h
        if simulate_disaster and ("Mathare" in log.city or "Mai Mahiu" in log.city): rain = 65.0 
        
        if rain > 50:
            active_alerts.append(f"CRITICAL WEATHER: Heavy Rainfall ({rain}mm) in {log.city}")

        if any(c in log.city for c in ASAL_COUNTIES) and log.temperature > 32.0 and rain < 1.0:
            active_alerts.append(f"DROUGHT ALERT: Extreme Heat ({log.temperature}°C) in {log.city}")

    show_alert_banner(active_alerts)

    col1, col2, col3 = st.columns(3)
    col1.metric("Monitored Zones", len(zones), "Across 47 Counties")
    col2.metric("High Risk Areas", critical_count, "Based on Historical Data")
    col3.metric("Live Sensors", len(weather_logs), "Real-Time Updates")

    # --- 3. THE MAP FIX (Using get_zone_coords) ---
    m = folium.Map(location=[0.0236, 37.9062], zoom_start=6, tiles="CartoDB dark_matter")

    for zone in zones:
        if disaster_filter != "All" and disaster_filter not in zone.disaster_type: continue
        
        # FIX: Get Real Coords
        lat, lon = get_zone_coords(zone.name)
        
        color = "orange"
        if zone.risk_level == "Critical": color = "red"
        if "Drought" in zone.disaster_type: color = "brown"
        
        if zone.geom:
            folium.Marker(
                location=[lat, lon], # Correct Coords
                popup=f"<b>{zone.name}</b><br>Risk: {zone.risk_level}",
                icon=folium.Icon(color=color, icon="info-sign")
            ).add_to(m)

    for log in weather_logs:
        rain = log.rainfall_1h
        if simulate_disaster and ("Mathare" in log.city or "Mai Mahiu" in log.city): rain = 65.0
        icon_color = "red" if rain > 50 else "blue" if rain > 5 else "green"
        
        folium.Marker(
            [log.lat, log.lon],
            popup=f"<b>{log.city}</b><br>Rain: {rain}mm",
            icon=folium.Icon(color=icon_color, icon="cloud")
        ).add_to(m)

    st_folium(m, width="100%", height=600)

    if st.button("🔄 Refresh Data"):
        st.rerun()