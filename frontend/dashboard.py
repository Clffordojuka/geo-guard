# frontend/dashboard.py
import sys
import os

# Add the parent directory (root folder) to the Python Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from streamlit_folium import st_folium
from components.map_view import render_map
from backend.database import SessionLocal
from backend.models import RiskZone

# Page Config (Browser Title)
st.set_page_config(page_title="GeoGuard Kenya", layout="wide", page_icon="🌍")

# --- HEADER & METRICS ---
st.title("🌍 GeoGuard Kenya: National Climate Monitor")
st.markdown("Real-time disaster early warning system for Floods, Droughts, and Landslides.")

# Fetch quick stats
db = SessionLocal()
total_zones = db.query(RiskZone).count()
critical_zones = db.query(RiskZone).filter(RiskZone.risk_level == "Critical").count()
drought_areas = db.query(RiskZone).filter(RiskZone.disaster_type.contains("Drought")).count()
db.close()

# Display Metrics in 3 Columns
col1, col2, col3 = st.columns(3)
col1.metric("Monitored Zones", total_zones, "Across 47 Counties")
col2.metric("Critical Alerts", critical_zones, "Immediate Action Req", delta_color="inverse")
col3.metric("Active Drought Zones", drought_areas, "ASAL Region")

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Views")
disaster_filter = st.sidebar.radio(
    "Select Disaster Type:",
    ["All", "Urban Flood", "Riverine Flood", "Flash Flood", "Landslide", "Drought"]
)

st.sidebar.markdown("---")
st.sidebar.info("Data Sources: OpenWeatherMap, NDMA, Kenya Met Dept.")

# --- THE MAIN MAP ---
st.subheader(f"Live Situation Map: {disaster_filter}")
map_obj = render_map(disaster_filter)
st_folium(map_obj, width="100%", height=600)

# --- REFRESH BUTTON ---
if st.button("🔄 Refresh Real-Time Data"):
    st.rerun()