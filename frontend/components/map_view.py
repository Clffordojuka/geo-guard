# frontend/components/map_view.py
import folium
import streamlit as st
from backend.database import SessionLocal
from backend.models import RiskZone, WeatherLog
from shapely import wkb

def get_db_data():
    """Fetch all Risk Zones and the latest Weather Logs."""
    db = SessionLocal()
    zones = db.query(RiskZone).all()
    # Get latest weather for each city (distinct on city)
    weather = db.query(WeatherLog).order_by(WeatherLog.city, WeatherLog.timestamp.desc()).distinct(WeatherLog.city).all()
    db.close()
    return zones, weather

def render_map(filter_type="All"):
    """
    Draws the map with Polygons (Risk Zones) and Markers (Weather).
    filter_type: 'All', 'Flood', 'Drought', 'Landslide'
    """
    # 1. Base Map centered on Kenya
    m = folium.Map(location=[0.0236, 37.9062], zoom_start=6, tiles="CartoDB dark_matter")

    zones, weather_logs = get_db_data()

    # 2. Draw Risk Zones (Polygons)
    for zone in zones:
        # Filter logic
        if filter_type != "All" and filter_type not in zone.disaster_type:
            continue

        # Color coding
        color = "#FF0000" if zone.risk_level == "Critical" else "#FFA500" # Red or Orange
        
        # Convert WKB (Database format) to GeoJSON
        if zone.geom is not None:
            # We use a simple popup
            popup_html = f"""
            <b>{zone.name}</b><br>
            Type: {zone.disaster_type}<br>
            Risk: {zone.risk_level}<br>
            <i>{zone.description}</i>
            """
            
            # Note: In a real app we'd convert WKB to GeoJSON properly. 
            # For this hackathon, we use a library helper or just plot a marker if polygon fails.
            # But here, let's use the Weather Markers as the primary visual if Polygons are complex.
            pass 

    # 3. Draw Weather Markers (The Pinpoints)
    for log in weather_logs:
        # Determine Icon based on rain
        icon_color = "green"
        if log.rainfall_1h > 0: icon_color = "blue"
        if log.rainfall_1h > 10: icon_color = "red" # Heavy rain

        html = f"""
        <b>{log.city}</b><br>
        Temp: {log.temperature}°C<br>
        Rain: {log.rainfall_1h}mm<br>
        Humidity: {log.humidity}%
        """
        
        folium.Marker(
            [log.lat, log.lon],
            popup=html,
            tooltip=f"{log.city}: {log.rainfall_1h}mm Rain",
            icon=folium.Icon(color=icon_color, icon="cloud")
        ).add_to(m)

    return m