# scripts/seed_db.py
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from sqlalchemy import text # Import text to run raw SQL
from backend.database import SessionLocal, engine
from backend.models import RiskZone, Base

def seed_data():
    print("🛠️  Initializing Database Tables...")

    # --- 1. CRITICAL FIX: ENABLE POSTGIS EXTENSION ---
    # We connect directly to the engine to run the enabling command
    with engine.connect() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        connection.commit()
    print("✅ PostGIS Extension Enabled.")

    # --- 2. Create Tables (Now that PostGIS is active) ---
    Base.metadata.create_all(bind=engine)
    print("✅ Tables Verified.")

    db = SessionLocal()
    
    # --- 3. FLOOD ZONES ---
    flood_zones = [
        {"name": "Mathare Settlements", "county": "Nairobi", "risk": "Critical", "type": "Urban Flood", "desc": "Severely flooded informal settlement.", 
         "geom": "POLYGON((36.85 -1.25, 36.87 -1.25, 36.87 -1.27, 36.85 -1.27, 36.85 -1.25))"},
        {"name": "Eastlands", "county": "Nairobi", "risk": "High", "type": "Urban Flood", "desc": "Displacement reported due to drainage failure.", 
         "geom": "POLYGON((36.87 -1.28, 36.90 -1.28, 36.90 -1.30, 36.87 -1.30, 36.87 -1.28))"},
        {"name": "South C", "county": "Nairobi", "risk": "High", "type": "Urban Flood", "desc": "Building collapse risk and severe flooding.", 
         "geom": "POLYGON((36.82 -1.31, 36.84 -1.31, 36.84 -1.33, 36.82 -1.33, 36.82 -1.31))"},
        {"name": "Kisumu Central", "county": "Kisumu", "risk": "High", "type": "Lake Backflow", "desc": "Over 340 households affected by Lake Victoria.", 
         "geom": "POLYGON((34.73 -0.08, 34.78 -0.08, 34.78 -0.12, 34.73 -0.12, 34.73 -0.08))"},
        {"name": "Dunga Beach", "county": "Kisumu", "risk": "High", "type": "Lake Backflow", "desc": "Submerged tourism and fishing areas.", 
         "geom": "POLYGON((34.73 -0.10, 34.75 -0.10, 34.75 -0.12, 34.73 -0.12, 34.73 -0.10))"},
        {"name": "Hola", "county": "Tana River", "risk": "Critical", "type": "Riverine Flood", "desc": "67 households submerged by Tana River.", 
         "geom": "POLYGON((40.00 -1.45, 40.10 -1.45, 40.10 -1.55, 40.00 -1.55, 40.00 -1.45))"},
        {"name": "Lobere Dam Area", "county": "Turkana", "risk": "Critical", "type": "Flash Flood", "desc": "89 households displaced, 25k affected.", 
         "geom": "POLYGON((36.00 3.50, 36.30 3.50, 36.30 3.80, 36.00 3.80, 36.00 3.50))"},
        {"name": "Laikipia Dam Zone", "county": "Laikipia", "risk": "High", "type": "Dam Overflow", "desc": "Downstream risk from Lobere Dam overflow.", 
         "geom": "POLYGON((36.70 0.00, 36.85 0.00, 36.85 0.15, 36.70 0.15, 36.70 0.00))"},
        {"name": "Homa Bay Shores", "county": "Homa Bay", "risk": "High", "type": "Lake Backflow", "desc": "7,000 households severely affected.", 
         "geom": "POLYGON((34.40 -0.45, 34.55 -0.45, 34.55 -0.60, 34.40 -0.60, 34.40 -0.45))"},
        {"name": "Shimbirey", "county": "Garissa", "risk": "Medium", "type": "Flash Flood", "desc": "Livestock loss (300 goats) reported.", 
         "geom": "POLYGON((39.60 -0.40, 39.75 -0.40, 39.75 -0.55, 39.60 -0.55, 39.60 -0.40))"},
    ]

    # --- 4. LANDSLIDE ZONES ---
    landslide_zones = [
        {"name": "Chesongoch", "county": "Elgeyo Marakwet", "risk": "Critical", "type": "Landslide", "desc": "Major tragedy site: 41 deaths recorded.", 
         "geom": "POLYGON((35.60 1.10, 35.68 1.10, 35.68 1.16, 35.60 1.16, 35.60 1.10))"},
        {"name": "Elgeyo Escarpment", "county": "Elgeyo Marakwet", "risk": "High", "type": "Landslide", "desc": "Unstable soil structure along the escarpment.", 
         "geom": "POLYGON((35.50 0.95, 35.70 0.95, 35.70 1.20, 35.50 1.20, 35.50 0.95))"},
        {"name": "Weiwei", "county": "West Pokot", "risk": "Critical", "type": "Landslide", "desc": "2 deaths reported in October 2024.", 
         "geom": "POLYGON((35.05 1.20, 35.20 1.20, 35.20 1.35, 35.05 1.35, 35.05 1.20))"},
        {"name": "Kisii Highlands", "county": "Kisii", "risk": "Medium", "type": "Landslide", "desc": "Steep slopes with ongoing heavy rains.", 
         "geom": "POLYGON((34.75 -0.65, 34.90 -0.65, 34.90 -0.80, 34.75 -0.80, 34.75 -0.65))"},
        {"name": "Narok West", "county": "Narok", "risk": "High", "type": "Landslide", "desc": "Western highlands rain warning.", 
         "geom": "POLYGON((35.80 -1.00, 36.10 -1.00, 36.10 -1.20, 35.80 -1.20, 35.80 -1.00))"},
    ]

    # --- 5. DROUGHT ZONES ---
    drought_zones = [
        {"name": "Mandera East", "county": "Mandera", "risk": "Critical", "type": "Drought", "desc": "IPC Phase 3: Severe food insecurity.", 
         "geom": "POLYGON((41.00 3.50, 41.95 3.50, 41.95 4.00, 41.00 4.00, 41.00 3.50))"},
        {"name": "Turkana Central", "county": "Turkana", "risk": "Critical", "type": "Drought", "desc": "Dual Crisis: Drought + Floods simultaneously.", 
         "geom": "POLYGON((35.00 2.50, 36.50 2.50, 36.50 4.50, 35.00 4.50, 35.00 2.50))"},
        {"name": "Wajir South", "county": "Wajir", "risk": "High", "type": "Drought", "desc": "Deteriorating pasture and water conditions.", 
         "geom": "POLYGON((39.50 0.50, 40.80 0.50, 40.80 2.00, 39.50 2.00, 39.50 0.50))"},
        {"name": "Marsabit North", "county": "Marsabit", "risk": "High", "type": "Drought", "desc": "High malnutrition rates reported.", 
         "geom": "POLYGON((37.20 2.00, 38.50 2.00, 38.50 3.50, 37.20 3.50, 37.20 2.00))"},
        {"name": "Garissa North", "county": "Garissa", "risk": "High", "type": "Drought", "desc": "287,700 people in need of assistance.", 
         "geom": "POLYGON((39.00 -1.00, 40.80 -1.00, 40.80 0.50, 39.00 0.50, 39.00 -1.00))"},
        {"name": "Isiolo", "county": "Isiolo", "risk": "Medium", "type": "Drought", "desc": "Alert Drought Phase.", 
         "geom": "POLYGON((37.50 0.20, 38.80 0.20, 38.80 1.50, 37.50 1.50, 37.50 0.20))"},
        {"name": "Samburu East", "county": "Samburu", "risk": "Medium", "type": "Drought", "desc": "Water crisis in pastoral areas.", 
         "geom": "POLYGON((36.50 0.80, 37.80 0.80, 37.80 2.20, 36.50 2.20, 36.50 0.80))"},
        {"name": "Tiaty", "county": "Baringo", "risk": "High", "type": "Drought", "desc": "Significant livestock losses.", 
         "geom": "POLYGON((35.80 0.30, 36.50 0.30, 36.50 1.20, 35.80 1.20, 35.80 0.30))"},
        {"name": "Kwale Hinterland", "county": "Kwale", "risk": "Medium", "type": "Drought", "desc": "Coastal drought alert.", 
         "geom": "POLYGON((39.30 -4.50, 39.70 -4.50, 39.70 -3.90, 39.30 -3.90, 39.30 -4.50))"},
        {"name": "Ganze", "county": "Kilifi", "risk": "Medium", "type": "Drought", "desc": "Ganze area specifically affected.", 
         "geom": "POLYGON((39.50 -3.80, 40.20 -3.80, 40.20 -2.90, 39.50 -2.90, 39.50 -3.80))"},
        {"name": "Kitui South", "county": "Kitui", "risk": "Medium", "type": "Drought", "desc": "Southern parts facing water stress.", 
         "geom": "POLYGON((37.80 -1.70, 39.00 -1.70, 39.00 -0.50, 37.80 -0.50, 37.80 -1.70))"},
    ]
    
    # Combine all lists
    all_zones = flood_zones + landslide_zones + drought_zones

    print(f"🌱 Seeding {len(all_zones)} National Disaster Zones...")
    
    count = 0
    try:
        for zone in all_zones:
            # Check if exists to avoid duplicates
            exists = db.query(RiskZone).filter(RiskZone.name == zone["name"]).first()
            if not exists:
                new_zone = RiskZone(
                    name=zone["name"],
                    county=zone["county"],
                    risk_level=zone["risk"],
                    disaster_type=zone["type"],
                    description=zone["desc"],
                    geom=zone["geom"]
                )
                db.add(new_zone)
                count += 1
                print(f" -> Added {zone['name']} ({zone['county']})")
        
        db.commit()
        print(f"✅ Success! Added {count} new zones to the National Registry.")
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()