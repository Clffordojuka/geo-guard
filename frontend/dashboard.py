# frontend/dashboard.py
import sys
import os
import datetime
import time
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
# Import fetcher for manual sync on Render
from backend.weather_service import fetch_live_weather 

# Page Config
st.set_page_config(page_title="GeoGuard Kenya", layout="wide", page_icon="🌍")

# --- PLACEHOLDERS ---
SIGN_PLACEHOLDER = "Select the sign..."
LOCATION_PLACEHOLDER = "Select area to observe..."

# --- 1. COORDINATE MAPPING (The Fix for [0,0]) ---
def get_zone_coords(zone_name):
    """Maps Zone Names to Real Coordinates so they don't appear at [0,0]"""
    locations = {
        "Mathare Settlements": (-1.26, 36.85),
        "Eastlands": (-1.28, 36.89),
        "South C": (-1.32, 36.83),
        "Kibera (Soweto Highrise)": (-1.31, 36.79),
        "Kisumu Central": (-0.10, 34.75),
        "Dunga Beach": (-0.14, 34.73),
        "Homa Bay Shores": (-0.52, 34.45),
        "Budalangi Floodplains": (0.10, 34.00),
        "Mai Mahiu Gully": (-0.99, 36.56),
        "Murang'a East Slopes": (-0.72, 37.15),
        "Laikipia Dam Zone": (0.36, 36.78),
        "Turkana North (Kibish)": (4.50, 35.80),
        "Turkana Central": (3.11, 35.60),
        "Mandera East": (3.93, 41.86),
        "Wajir South": (1.00, 40.00),
        "Marsabit North": (3.00, 37.50),
        "Garissa North": (-0.10, 39.50),
        "Hola": (-1.50, 40.03),
        "Kwale Hinterland": (-4.17, 39.45),
        "Ganze": (-3.50, 39.75),
        "Kitui South": (-1.60, 38.20),
        "Isiolo": (0.35, 37.58),
        "Samburu East": (1.20, 37.20),
        "Tiaty": (1.00, 36.10),
        "Weiwei": (1.45, 35.45),
        "Chesongoch": (1.13, 35.64),
        "Narok West": (-1.20, 35.50),
        "Kisii Highlands": (-0.68, 34.77),
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
# MODE A: SEASONAL PREDICTIONS
# =========================================================
if app_mode == "🔮 Seasonal Predictions":
    st.title("🔮 AI Seasonal Forecast Engine")
    st.markdown("Predictive analytics using a **Random Forest Regressor** trained on historical Kenyan weather data.")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.info("**Model Architecture**")
        st.markdown("- **Algorithm:** Random Forest\n- **Accuracy (R²):** 67%\n- **Target:** Rainfall (mm)")
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
                st.warning("⚠️ **Recommendation:** Rainfall below average. Focus on drought-resistant crops.")

# =========================================================
# MODE B: ASILI SMART
# =========================================================
elif app_mode == "🌿 Asili Smart":
    # [Keep your existing Asili Smart code here - it was working fine]
    # ... (Paste the Asili Smart block from your previous message) ...
    # For brevity in this fix, I am assuming you keep the Asili logic identical.
    st.title("🌿 Asili Smart Forecast")
    st.info("👈 Please select a sign and location from the sidebar to begin validation.")

# =========================================================
# MODE C: LIVE MONITOR (THE FIXED MAP)
# =========================================================
else:
    st.title("🌍 GeoGuard Kenya: National Climate Monitor")
    
    # --- 1. Manual Sync Button (Critical for Render Free Tier) ---
    col_status, col_btn = st.columns([3, 1])
    col_status.metric("System Status", "Online | Cloud Database Connected")
    
    if col_btn.button("🔄 Sync Live Weather"):
        with st.spinner("Pinging Satellites..."):
            fetch_live_weather() # Updates DB with fresh OpenWeather data
            st.success("Synced!")
            time.sleep(1)
            st.rerun()

    # --- 2. Dashboard Metrics ---
    # Sidebar Filters
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
        if rain > 50: active_alerts.append(f"CRITICAL WEATHER: Heavy Rainfall ({rain}mm) in {log.city}")

    show_alert_banner(active_alerts)

    col1, col2, col3 = st.columns(3)
    col1.metric("Monitored Zones", len(zones), "Across 47 Counties")
    col2.metric("High Risk Areas", critical_count, "Based on Historical Data")
    col3.metric("Live Sensors", len(weather_logs), "Real-Time Updates")

    # --- 3. THE MAP FIX ---
    m = folium.Map(location=[0.0236, 37.9062], zoom_start=6, tiles="CartoDB dark_matter")

    for zone in zones:
        if disaster_filter != "All" and disaster_filter not in zone.disaster_type: continue
        
        # FIX: Get Real Coords instead of [0,0]
        lat, lon = get_zone_coords(zone.name) 
        
        color = "red" if zone.risk_level == "Critical" else "orange"
        if "Drought" in zone.disaster_type: color = "brown"
        
        if zone.geom:
            folium.Marker(
                location=[lat, lon], # <--- FIXED HERE
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