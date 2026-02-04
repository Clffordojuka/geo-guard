# backend/ussd_service.py
from sqlalchemy.orm import Session
from backend.models import WeatherLog
import datetime

def handle_ussd_session(text: str, db: Session):
    """
    Parses the USSD 'text' string (e.g., "1*2") and returns the menu response.
    Africa's Talking appends inputs with '*': "1" -> "1*2" -> "1*2*1"
    """
    # Split text into a list of inputs. Empty string means start of session.
    inputs = text.split("*") if text else []
    
    response = ""

    # --- SCREEN 0: MAIN MENU ---
    if text == "":
        response = "CON Welcome to GeoGuard Kenya\n"
        response += "1. Report Sign (Asili Smart)\n"
        response += "2. Get Weather Forecast"

    # --- PATH 1: ASILI SMART (REPORTING) ---
    elif inputs[0] == "1":
        # Screen 1.1: Select Sign
        if len(inputs) == 1:
            response = "CON Select Observed Sign:\n"
            response += "1. Safari Ants (Rain)\n"
            response += "2. Frogs Croaking (Rain)\n"
            response += "3. Goat Intestines (Drought)"
        
        # Screen 1.2: Select Location (Simplified for USSD)
        elif len(inputs) == 2:
            response = "CON Select Your Region:\n"
            response += "1. Nairobi (Mathare)\n"
            response += "2. Kisumu\n"
            response += "3. Turkana"
            
        # Screen 1.3: Success Message
        elif len(inputs) == 3:
            # Parse inputs
            sign_map = {"1": "Safari Ants", "2": "Frogs", "3": "Goat Intestines"}
            loc_map = {"1": "Nairobi", "2": "Kisumu", "3": "Turkana"}
            
            chosen_sign = sign_map.get(inputs[1], "Unknown")
            chosen_loc = loc_map.get(inputs[2], "Unknown")
            
            # TODO: In production, save this "Asili Report" to a DB table here.
            
            response = f"END Thank you. We have received your report of '{chosen_sign}' in {chosen_loc}. \nValidation via satellite is in progress."

    # --- PATH 2: GET FORECAST ---
    elif inputs[0] == "2":
        # Screen 2.1: Select Location
        if len(inputs) == 1:
            response = "CON Select Location for Forecast:\n"
            response += "1. Nairobi (Mathare)\n"
            response += "2. Kisumu Central\n"
            response += "3. Turkana North\n"
            response += "4. Mombasa"

        # Screen 2.2: Show Data from DB
        elif len(inputs) == 2:
            # Exact mapping to 'RiskZone' names in your database
            loc_map = {
                "1": "Mathare Settlements", 
                "2": "Kisumu Central", 
                "3": "Turkana North (Kibish)",
                "4": "Mombasa Island"
            }
            city_name = loc_map.get(inputs[1])
            
            if city_name:
                # Query the Database for the latest log
                log = db.query(WeatherLog).filter(WeatherLog.city == city_name).order_by(WeatherLog.timestamp.desc()).first()
                
                if log:
                    # Smart Status Logic (Matches Dashboard Logic)
                    status = "Normal"
                    if log.rainfall_1h > 50:
                        status = "CRITICAL: FLOOD"
                    elif log.rainfall_1h > 10:
                        status = "Heavy Rain Alert"
                    elif log.temperature > 32 and log.rainfall_1h < 1:
                        status = "Heat/Drought Risk"

                    # Format Time (e.g. 10:30 AM)
                    time_str = log.timestamp.strftime("%I:%M%p")

                    response = f"END Forecast for {city_name} ({time_str}):\n"
                    response += f"Temp: {log.temperature}C\n"
                    response += f"Rain: {log.rainfall_1h}mm\n"
                    response += f"Status: {status}"
                else:
                    response = "END No recent data available. Please try syncing the live monitor."
            else:
                response = "END Invalid location selected."

    # --- FALLBACK ---
    else:
        response = "END Invalid input. Please dial again."

    return response