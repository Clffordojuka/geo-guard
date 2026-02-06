# backend/whatsapp_service.py
import os
import requests
from twilio.twiml.messaging_response import MessagingResponse
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

def handle_whatsapp_message(body: str, media_url: str, sender: str):
    """
    Decides if the user sent Text (Menu) or Image (Analysis).
    """
    response = MessagingResponse()
    msg = response.message()

    # --- SCENARIO 1: USER SENDS AN IMAGE ---
    if media_url:
        print(f"📸 Image received from {sender}! Analyzing...")
        try:
            # 1. Download the image from WhatsApp/Twilio
            img_data = requests.get(
                media_url, 
                auth=(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
            ).content
            
            # 2. Convert raw bytes to a proper Image object
            image = Image.open(BytesIO(img_data))
            
            # 3. Initialize Client with Explicit v1beta (CRITICAL FIX)
            client = genai.Client(
                api_key=os.getenv("GEMINI_API_KEY"),
                http_options={'api_version': 'v1beta'}
            )
            
            prompt = """
            You are a disaster expert. Analyze this image.
            1. Is there a disaster risk (Flood, Drought, Landslide)?
            2. If yes, how severe is it (Low, Medium, Critical)?
            3. Give 1 sentence of safety advice.
            If it's just a random photo, say "I don't see any climate risks here."
            """
            
            # 4. Use the Newer Model ID
            ai_response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=[image, prompt]
            )
            
            # 5. Reply to User
            msg.body(f"🤖 *GeoGuard AI Vision*\n\n{ai_response.text}")
            
        except Exception as e:
            print(f"❌ Vision Error: {e}")
            msg.body("⚠️ Sorry, the AI is having a nap. Please try again in 1 minute.")

    # --- SCENARIO 2: USER SENDS TEXT ---
    else:
        user_input = body.lower().strip()
        
        if "hello" in user_input or "hi" in user_input or "start" in user_input:
            msg.body("🌍 *Welcome to GeoGuard Bot*\n\n"
                     "I can help you analyze risks.\n"
                     "📸 *Send me a photo* of a river, farm, or crack to analyze flood/drought risk.\n\n"
                     "Or type:\n"
                     "1️⃣ for Weather Forecast\n"
                     "2️⃣ for Asili Smart Info")
        
        elif "1" in user_input:
             msg.body("🌦 *Nairobi Forecast:*\nTemp: 24°C | Rain: Light\nStatus: Normal")
             
        elif "2" in user_input:
             msg.body("🌿 *Asili Smart*\nLook for:\n- Safari Ants (Rain)\n- Croaking Frogs (Rain)\n- Clear Intestines (Drought)")
             
        else:
             msg.body("I didn't catch that. Type *Hello* to start or send a Photo! 📸")

    return str(response)