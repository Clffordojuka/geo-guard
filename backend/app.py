# backend/app.py
from fastapi import FastAPI, Form, Request, Response
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from .database import engine, Base, SessionLocal

# Uses the weather service (26 zones)
from .weather_service import fetch_live_weather 
from .ussd_service import handle_ussd_session 

# Create Tables
Base.metadata.create_all(bind=engine)

# --- THE AUTOMATION ENGINE ---
def scheduled_weather_task():
    """Runs automatically to update weather data."""
    print("⏰ AUTOMATION: Starting scheduled weather scan...")
    try:
        fetch_live_weather()
    except Exception as e:
        print(f"❌ AUTOMATION ERROR: {e}")

# Start the scheduler when the app starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    # Run immediately on startup
    scheduler.add_job(scheduled_weather_task, 'date', run_date=None) 
    # Then run every 1 hour
    scheduler.add_job(scheduled_weather_task, 'interval', minutes=60)
    scheduler.start()
    print("✅ System Online: Weather Scheduler Started.")
    yield
    # Shutdown
    scheduler.shutdown()

app = FastAPI(title="GeoGuard Kenya", lifespan=lifespan)

@app.get("/")
def home():
    return {"status": "GeoGuard National Monitor Online", "mode": "Automated"}

# --- NEW USSD ENDPOINT (Africa's Talking) ---
@app.post("/ussd")
async def ussd_callback(
    text: str = Form(default=""),
    sessionId: str = Form(default=""),
    serviceCode: str = Form(default=""),
    phoneNumber: str = Form(default="")
):
    """
    Receives the POST request from Africa's Talking when a farmer dials *384*...
    """
    db = SessionLocal()
    try:
        # Pass the text input to our logic engine
        response_text = handle_ussd_session(text, db)
        
        # <--- 2. THE FIX: Return raw text, NOT JSON
        return Response(content=response_text, media_type="text/plain")
        
    finally:
        db.close()