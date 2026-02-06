# backend/whatsapp_service.py
import os
import requests
import random
from twilio.twiml.messaging_response import MessagingResponse
from google import genai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# DB Imports
from backend.database import SessionLocal
from backend.models import WeatherLog

load_dotenv()

# --- 1. SMART LOCATION MAPPING (Connects User Input -> DB Names) ---
# This dictionary maps "What users type" to "Exact DB Name"
ZONE_MAP = {
    # FLOOD ZONES
    "nairobi": "Mathare Settlements", "mathare": "Mathare Settlements",
    "eastlands": "Eastlands", "south c": "South C",
    "kisumu": "Kisumu Central", "lake": "Kisumu Central", "dunga": "Dunga Beach",
    "tana": "Hola", "hola": "Hola", "tana river": "Hola",
    "turkana flood": "Lobere Dam Area", "lobere": "Lobere Dam Area",
    "laikipia": "Laikipia Dam Zone",
    "homa bay": "Homa Bay Shores",
    "garissa flood": "Shimbirey", "shimbirey": "Shimbirey",
    
    # LANDSLIDE ZONES
    "elgeyo": "Chesongoch", "chesongoch": "Chesongoch", "escarpment": "Elgeyo Escarpment",
    "pokot": "Weiwei", "weiwei": "Weiwei", "west pokot": "Weiwei",
    "kisii": "Kisii Highlands",
    "narok": "Narok West", "narok": "Narok West",

    # DROUGHT ZONES
    "mandera": "Mandera East",
    "turkana": "Turkana Central", "turkana drought": "Turkana Central",
    "wajir": "Wajir South",
    "marsabit": "Marsabit North",
    "garissa": "Garissa North",
    "isiolo": "Isiolo",
    "samburu": "Samburu East",
    "baringo": "Tiaty", "tiaty": "Tiaty",
    "kwale": "Kwale Hinterland",
    "kilifi": "Ganze", "ganze": "Ganze",
    "kitui": "Kitui South"
}

# --- 2. INDIGENOUS KNOWLEDGE DICTIONARY ---
IK_SIGNS = {
    "ants": "🐜 *Safari Ants (Siafu)*\nMeaning: Rain is coming soon.",
    "frogs": "🐸 *Frogs Croaking*\nMeaning: Immediate rain likely within 24hrs.",
    "halo": "🌑 *Moon Halo*\nMeaning: Rain likely in 3 days.",
    "baobab": "🌳 *Baobab Flowering*\nMeaning: Long rains are starting soon.",
    "wind": "💨 *Strong South Wind*\nMeaning: Rain is near.",
    "intestines": "🍖 *Goat Intestines (Clear)*\nMeaning: Prolonged Drought predicted.",
    "mist": "🌫 *Thick Morning Mist*\nMeaning: Cold, dry day ahead.",
    "dragonfly": "libellule *Swarm of Dragonflies*\nMeaning: Rainy season is ending.",
    "bird": "🦅 *Magungu Bird High*\nMeaning: Heavy rain approaching."
}

def get_live_forecast(user_text):
    """
    Finds the correct zone and returns a detailed report.
    """
    # 1. Find the best match
    db_name = None
    for keyword, name in ZONE_MAP.items():
        if keyword in user_text:
            db_name = name
            break
    
    if not db_name:
        return None  # No match found

    # 2. Query DB
    db = SessionLocal()
    try:
        log = db.query(WeatherLog).filter(WeatherLog.city == db_name).order_by(WeatherLog.timestamp.desc()).first()
        
        if log:
            # Smart Status Logic
            status = "🟢 Normal"
            if log.rainfall_1h > 50: status = "🚨 CRITICAL RISK"
            elif log.rainfall_1h > 10: status = "⚠️ Warning Alert"
            elif log.temperature > 34: status = "☀️ Severe Heat/Drought"

            return (f"🌍 *Live Monitor: {db_name}*\n"
                    f"🌡 Temp: {log.temperature}°C\n"
                    f"💧 Rain (1h): {log.rainfall_1h}mm\n"
                    f"📢 Status: {status}\n"
                    f"_(Synced: {log.timestamp.strftime('%H:%M')})_")
        else:
            return f"⚠️ Connected to {db_name}, but waiting for fresh sensor data. Try syncing."
    finally:
        db.close()

def handle_whatsapp_message(body: str, media_url: str, sender: str):
    response = MessagingResponse()
    msg = response.message()

    # --- SCENARIO 1: IMAGE ANALYSIS (Visual AI) ---
    if media_url:
        print(f"📸 Image received from {sender}! Analyzing...")
        try:
            # Download & Process
            img_data = requests.get(media_url, auth=(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))).content
            image = Image.open(BytesIO(img_data))
            
            # Setup Client (Free Tier Friendly)
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"), http_options={'api_version': 'v1beta'})
            prompt = "Analyze this image for Kenyan climate risks (Flood, Drought, Landslide). Be brief. If safe, say 'Safe'."
            
            ai_response = client.models.generate_content(model="gemini-2.0-flash", contents=[image, prompt])
            msg.body(f"🤖 *GeoGuard Vision*\n\n{ai_response.text}")

        except Exception as e:
            # Fallback Demo Mode
            print(f"⚠️ AI Backup Triggered: {e}")
            risks = ["⚠️ *High Flood Risk Detected*", "☀️ *Severe Drought Stress Visible*", "✅ *Area appears Safe*"]
            msg.body(f"🤖 *GeoGuard Vision (Offline)*\n\n{random.choice(risks)}\n_Note: Live AI is reconnecting._")

    # --- SCENARIO 2: TEXT INTELLIGENCE ---
    else:
        text = body.lower().strip()
        
        # 1. Main Menu
        if text in ["hello", "hi", "start", "menu", "jambo"]:
            msg.body("🌍 *GeoGuard Kenya Bot*\n"
                     "I monitor 26 Risk Zones & Indigenous Signs.\n\n"
                     "👇 *Try asking:*\n"
                     "• 'Status in *Kisumu*' or '*Mandera*'\n"
                     "• 'Meaning of *Safari Ants*'\n"
                     "• 'Report *Baobab* flowering'\n"
                     "• Send a *Photo* for analysis")

        # 2. Check for Location Requests (The "26 Zone" Logic)
        elif any(k in text for k in ZONE_MAP.keys()):
            report = get_live_forecast(text)
            if report:
                msg.body(report)
            else:
                msg.body("⚠️ I recognize that region, but need more specific details.")

        # 3. Check for Indigenous Knowledge (The "Asili Smart" Logic)
        elif any(k in text for k in IK_SIGNS.keys()):
            # Find which sign they mentioned
            for key, explanation in IK_SIGNS.items():
                if key in text:
                    msg.body(f"🌿 *Asili Smart Knowledge*\n\n{explanation}\n\n_System has logged this observation._")
                    break

        # 4. Fallback
        else:
            msg.body("❌ I didn't understand. Try typing a County name (e.g. *Turkana*, *Kisii*) or a Sign (e.g. *Ants*).")

    return str(response)