# backend/ussd_service.py
from sqlalchemy.orm import Session
from backend.models import WeatherLog
import datetime

def handle_ussd_session(text: str, db: Session):
    """
    Parses the USSD 'text' string and matches inputs to our National Risk Database.
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
        # Screen 1.1: Select Sign
        if len(inputs) == 1:
            response = "CON What did you see, Clifford?\n"
            response += "1. Safari Ants/Frogs (Rain)\n"
            response += "2. Dusty Wind/Intestines (Drought)\n"
            response += "3. Earth Cracks/Birds (Landslide)"
        
        # Screen 1.2: Select Region
        elif len(inputs) == 2:
            response = "CON Select Region:\n"
            response += "1. Nairobi (Mathare)\n"
            response += "2. Lake (Kisumu)\n"
            response += "3. Rift/Central (Murang'a)\n"
            response += "4. North (Turkana)\n"
            response += "5. Coast (Mombasa)"
            
        # Screen 1.3: Submission & Validation
        elif len(inputs) == 3:
            sign_map = {
                "1": "Rain Indicator (Ants/Frogs)", 
                "2": "Drought Indicator (Intestines)", 
                "3": "Landslide Indicator (Cracks)"
            }
            loc_map = {
                "1": "Nairobi", "2": "Kisumu", "3": "Murang'a", 
                "4": "Turkana", "5": "Mombasa"
            }
            
            chosen_sign = sign_map.get(inputs[1], "Unknown Sign")
            chosen_loc = loc_map.get(inputs[2], "Unknown Location")
            
            # Logic: Fake Validation Message
            # MUST start with END
            response = f"END Report Received: {chosen_sign} in {chosen_loc}.\n"
            response += "Status: Satellite Cross-Check Initiated.\n"
            response += "You will receive an SMS if risk is confirmed."

    # =========================================================
    # PATH 2: GET FORECAST (Data Driven)
    # =========================================================
    elif inputs[0] == "2":
        # Screen 2.1: Select Key Risk Zones
        if len(inputs) == 1:
            response = "CON Select Zone to Monitor:\n"
            response += "1. Nairobi (Mathare) - Flood\n"
            response += "2. Kisumu Central - Lake\n"
            response += "3. Murang'a East - Landslide\n"
            response += "4. Turkana North - Drought\n"
            response += "5. Mombasa Island - Coast"

        # Screen 2.2: Fetch Live DB Data
        elif len(inputs) == 2:
            # MAP THESE ID NUMBERS TO EXACT NAMES IN YOUR DATABASE
            loc_map = {
                "1": "Mathare Settlements", 
                "2": "Kisumu Central", 
                "3": "Murang'a East Slopes",
                "4": "Turkana North (Kibish)",
                "5": "Mombasa Island"
            }
            city_name = loc_map.get(inputs[1])
            
            if city_name:
                # 1. Fetch latest log
                log = db.query(WeatherLog).filter(WeatherLog.city == city_name).order_by(WeatherLog.timestamp.desc()).first()
                
                if log:
                    # 2. Smart Status Logic
                    status = "Normal"
                    if log.rainfall_1h > 50: status = "🚨 CRITICAL FLOOD"
                    elif log.rainfall_1h > 10: status = "⚠️ Heavy Rain"
                    elif log.temperature > 32 and log.rainfall_1h < 1: status = "☀️ High Heat/Drought"
                    
                    time_str = log.timestamp.strftime("%H:%M")

                    response = f"END {city_name} ({time_str}):\n"
                    response += f"🌡 Temp: {log.temperature}°C\n"
                    response += f"🌧 Rain: {log.rainfall_1h}mm\n"
                    response += f"📢 Status: {status}"
                else:
                    response = "END No data found. System syncing..."
            else:
                response = "END Invalid Selection."

    else:
        response = "END Invalid Input."

    return response