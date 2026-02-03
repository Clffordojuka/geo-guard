# backend/weather_service.py
import os
import requests
import datetime
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import RiskZone, WeatherLog
from dotenv import load_dotenv

# Load API Key
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def fetch_live_weather():
    """
    1. Gets all RiskZones from DB.
    2. Pings OpenWeatherMap for each zone.
    3. Saves the new data to WeatherLog table.
    """
    if not API_KEY:
        print("❌ Error: OPENWEATHER_API_KEY not found in .env")
        return

    db = SessionLocal()
    zones = db.query(RiskZone).all()
    
    if not zones:
        print("⚠️ No zones found in DB. Did you run the seed script?")
        return

    print(f"🌍 Starting Weather Scan for {len(zones)} zones...")
    
    count = 0
    for zone in zones:
        # 1. Get Coordinates based on the specific Zone Name
        lat, lon = get_coords(zone.name)
        
        try:
            # 2. Call API
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
            res = requests.get(url, timeout=10).json()
            
            # 3. Validate Response
            if res.get("cod") != 200:
                print(f"⚠️ API Error for {zone.name}: {res.get('message')}")
                continue

            # Rain is often missing from API if it's 0, so we default to 0.0
            rain_1h = res.get("rain", {}).get("1h", 0.0)
            
            # 4. Save to DB
            new_log = WeatherLog(
                city=zone.name,
                temperature=res["main"]["temp"],
                humidity=res["main"]["humidity"],
                rainfall_1h=rain_1h,
                lat=lat,
                lon=lon,
                timestamp=datetime.datetime.now()
            )
            db.add(new_log)
            count += 1
            print(f"   ✅ {zone.name}: {res['main']['temp']}°C, {rain_1h}mm Rain")
            
        except Exception as e:
            print(f"   ❌ Error fetching {zone.name}: {e}")

    db.commit()
    db.close()
    print(f"🚀 Scan Complete. Added {count} new weather logs.")

def get_coords(zone_name):
    """
    Maps the exact Zone Names from seed_db.py to real-world coordinates.
    """
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
    # Default to Nairobi if name doesn't match
    return locations.get(zone_name, (-1.29, 36.82))

if __name__ == "__main__":
    fetch_live_weather()