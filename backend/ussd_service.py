# backend/ussd_service.py
from sqlalchemy.orm import Session
from backend.models import WeatherLog
import datetime

def handle_ussd_session(text: str, db: Session):
    """
    Parses the USSD 'text' string and matches inputs to our National Risk Database.
    Now supports Drill-Down Menus for 26 Zones.
    """
    inputs = text.split("*") if text else []
    response = ""

    # --- SCREEN 0: MAIN MENU ---
    # MUST start with CON
    if text == "":
        response = "CON Jambo Clifford! Welcome to GeoGuard.\n"
        response += "1. Report Asili Sign (Citizen)\n"
        response += "2. Get Warning (Forecast)"

    # =========================================================
    # PATH 1: ASILI SMART (Indigenous Reporting)
    # =========================================================
    elif inputs[0] == "1":
        # Screen 1.1: Select Sign Category (Expanded from your Data)
        if len(inputs) == 1:
            response = "CON What sign did you observe?\n"
            response += "1. Rain (Ants/Frogs/Halo/Baobab)\n"
            response += "2. Drought (Intestines/Mist/Dragonfly)\n"
            response += "3. Landslide (Cracks/Magungu Bird)"
        
        # Screen 1.2: Select Broad Region
        elif len(inputs) == 2:
            response = "CON Select Your Location:\n"
            response += "1. Nairobi Region\n"
            response += "2. West/Lake (Kisumu/Kisii)\n"
            response += "3. North/Arid (Turkana/Wajir)\n"
            response += "4. Rift Valley (Elgeyo/Baringo)\n"
            response += "5. Coast (Tana/Kilifi)"
            
        # Screen 1.3: Submission & Validation
        elif len(inputs) == 3:
            # Map inputs to text for the report
            sign_cat_map = {
                "1": "Rain Sign (Ants/Frogs)", 
                "2": "Drought Sign (Intestines/Mist)", 
                "3": "Landslide Sign (Cracks/Birds)"
            }
            region_map = {
                "1": "Nairobi", "2": "West/Lake", "3": "North/Arid", 
                "4": "Rift Valley", "5": "Coast"
            }
            
            chosen_sign = sign_cat_map.get(inputs[1], "Unknown Sign")
            chosen_loc = region_map.get(inputs[2], "Unknown Region")
            
            # Logic: Fake Validation Message
            response = f"END Report Received: {chosen_sign} in {chosen_loc}.\n"
            response += "Validation: Cross-referencing with Satellite Data...\n"
            response += "Thank you for contributing to the National Knowledge Base."

    # =========================================================
    # PATH 2: GET FORECAST (The "Drill-Down" Logic)
    # =========================================================
    elif inputs[0] == "2":
        # Screen 2.1: Select Region (Level 1)
        if len(inputs) == 1:
            response = "CON Select Region to Monitor:\n"
            response += "1. Nairobi (Urban Flood)\n"
            response += "2. West/Lake (Backflow)\n"
            response += "3. North (Drought)\n"
            response += "4. Rift (Landslide)\n"
            response += "5. Coast (Riverine)"

        # Screen 2.2: Select Specific Zone (Level 2 - Dynamic)
        elif len(inputs) == 2:
            region_selection = inputs[1]
            
            if region_selection == "1": # Nairobi
                response = "CON Select Nairobi Zone:\n"
                response += "1. Mathare Settlements\n"
                response += "2. Eastlands\n"
                response += "3. South C"
            elif region_selection == "2": # West
                response = "CON Select West Zone:\n"
                response += "1. Kisumu Central\n"
                response += "2. Homa Bay Shores\n"
                response += "3. Kisii Highlands"
            elif region_selection == "3": # North
                response = "CON Select North Zone:\n"
                response += "1. Turkana North (Kibish)\n"
                response += "2. Mandera East\n"
                response += "3. Wajir South"
            elif region_selection == "4": # Rift
                response = "CON Select Rift Zone:\n"
                response += "1. Chesongoch (Elgeyo)\n"
                response += "2. Weiwei (West Pokot)\n"
                response += "3. Narok West"
            elif region_selection == "5": # Coast
                response = "CON Select Coast Zone:\n"
                response += "1. Hola (Tana River)\n"
                response += "2. Mombasa Island\n"
                response += "3. Ganze (Kilifi)"
            else:
                response = "END Invalid Region."

        # Screen 2.3: Fetch Data (Level 3 - The Result)
        elif len(inputs) == 3:
            region = inputs[1]
            zone = inputs[2]
            
            # HUGE MAPPING: Maps (Region, Zone) -> Exact DB Name
            # This matches the names in your new 'seed_db.py' data
            db_mapping = {
                ("1", "1"): "Mathare Settlements", ("1", "2"): "Eastlands", ("1", "3"): "South C",
                ("2", "1"): "Kisumu Central", ("2", "2"): "Homa Bay Shores", ("2", "3"): "Kisii Highlands",
                ("3", "1"): "Turkana North (Kibish)", ("3", "2"): "Mandera East", ("3", "3"): "Wajir South",
                ("4", "1"): "Chesongoch", ("4", "2"): "Weiwei", ("4", "3"): "Narok West",
                ("5", "1"): "Hola", ("5", "2"): "Mombasa Island", ("5", "3"): "Ganze"
            }
            
            city_name = db_mapping.get((region, zone))
            
            if city_name:
                # 1. Fetch latest log
                log = db.query(WeatherLog).filter(WeatherLog.city == city_name).order_by(WeatherLog.timestamp.desc()).first()
                
                if log:
                    # 2. Smart Status Logic based on Risk Type
                    status = "Normal"
                    
                    # Customize Warning based on Region Type
                    if region == "3": # North (Drought logic)
                        if log.temperature > 30 and log.rainfall_1h < 1: status = "☀️ ALERT: DROUGHT"
                    elif region == "4": # Rift (Landslide logic)
                        if log.rainfall_1h > 15: status = "⛰️ ALERT: LANDSLIDE"
                    else: # Flood logic (General)
                        if log.rainfall_1h > 10: status = "⚠️ ALERT: FLOOD"

                    time_str = log.timestamp.strftime("%H:%M")

                    response = f"END {city_name} ({time_str}):\n"
                    response += f"🌡 {log.temperature}°C | 🌧 {log.rainfall_1h}mm\n"
                    response += f"📢 {status}"
                else:
                    response = f"END No live data for {city_name} yet. Try syncing."
            else:
                response = "END Invalid Zone Selection."

    else:
        response = "END Invalid Input."

    return response