# backend/logic.py
import requests
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import WeatherLog

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Representative coordinates for the 38 disaster zones
LOCATIONS = [
    {"city": "Mombasa", "lat": -4.04, "lon": 39.66},
    {"city": "Nairobi (Mathare)", "lat": -1.26, "lon": 36.86},
    {"city": "Nairobi (South C)", "lat": -1.32, "lon": 36.83},
    {"city": "Kiambu (Githurai)", "lat": -1.15, "lon": 36.90},
    {"city": "Thika", "lat": -1.03, "lon": 37.08},
    {"city": "Murang'a", "lat": -0.72, "lon": 37.15},
    {"city": "Nyeri", "lat": -0.42, "lon": 36.95},
    {"city": "Kirinyaga (Kutus)", "lat": -0.52, "lon": 37.28},
    {"city": "Embu", "lat": -0.53, "lon": 37.45},
    {"city": "Meru (Maua)", "lat": 0.05, "lon": 37.65},
    {"city": "Kisumu (Dunga)", "lat": -0.11, "lon": 34.74},
    {"city": "Homa Bay", "lat": -0.50, "lon": 34.45},
    {"city": "Migori", "lat": -1.00, "lon": 34.50},
    {"city": "Kisii", "lat": -0.70, "lon": 34.80},
    {"city": "Nyamira", "lat": -0.60, "lon": 34.95},
    {"city": "Nakuru (Mai Mahiu)", "lat": -1.00, "lon": 36.60},
    {"city": "West Pokot (Weiwei)", "lat": 1.25, "lon": 35.10},
    {"city": "Elgeyo (Chesongoch)", "lat": 1.13, "lon": 35.64},
    {"city": "Baringo (Tiaty)", "lat": 0.80, "lon": 36.00},
    {"city": "Turkana (Lobere)", "lat": 3.60, "lon": 36.15},
    {"city": "Narok", "lat": -1.10, "lon": 36.00},
    {"city": "Kericho", "lat": -0.30, "lon": 35.40},
    {"city": "Bomet", "lat": -0.80, "lon": 35.30},
    {"city": "Siaya", "lat": -0.06, "lon": 34.28},
    {"city": "Tana River (Hola)", "lat": -1.50, "lon": 40.05},
    {"city": "Kilifi (Ganze)", "lat": -3.40, "lon": 39.80},
    {"city": "Kwale", "lat": -4.20, "lon": 39.50},
    {"city": "Taita Taveta", "lat": -3.40, "lon": 38.50},
    {"city": "Mandera (East)", "lat": 3.93, "lon": 41.86},
    {"city": "Wajir (South)", "lat": 1.00, "lon": 40.00},
    {"city": "Garissa (Shimbirey)", "lat": -0.45, "lon": 39.65},
    {"city": "Marsabit", "lat": 2.50, "lon": 37.80},
    {"city": "Isiolo", "lat": 0.80, "lon": 37.60},
    {"city": "Samburu", "lat": 1.50, "lon": 37.00},
    {"city": "Kitui (South)", "lat": -1.20, "lon": 38.00},
    {"city": "Makueni", "lat": -2.00, "lon": 37.80},
    {"city": "Machakos", "lat": -1.30, "lon": 37.30},
    {"city": "Kajiado", "lat": -2.00, "lon": 36.80}
]

def fetch_national_weather(db: Session):
    if not API_KEY:
        print("❌ API Key missing.")
        return

    print(f"🌍 Starting National Weather Scan for {len(LOCATIONS)} regions...")
    
    count = 0
    for loc in LOCATIONS:
        params = {
            "lat": loc["lat"], "lon": loc["lon"],
            "appid": API_KEY, "units": "metric"
        }
        try:
            resp = requests.get(BASE_URL, params=params)
            if resp.status_code == 200:
                data = resp.json()
                
                # Extract Data
                temp = data["main"]["temp"]
                rain = data.get("rain", {}).get("1h", 0.0)
                humidity = data["main"]["humidity"]
                
                # Save to DB
                log = WeatherLog(
                    city=loc["city"],
                    temperature=temp,
                    rainfall_1h=rain,
                    humidity=humidity,
                    lat=loc["lat"],
                    lon=loc["lon"]
                )
                db.add(log)
                count += 1
                print(f" -> Scanned {loc['city']}: {temp}°C | Rain: {rain}mm")
            else:
                print(f"❌ Failed to fetch {loc['city']}")
        except Exception as e:
            print(f"❌ Error {loc['city']}: {e}")

    db.commit()
    print(f"✅ Scan Complete. {count} reports saved to database.")

if __name__ == "__main__":
    db = SessionLocal()
    fetch_national_weather(db)
    db.close()