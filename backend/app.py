# backend/app.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from .database import engine, Base, SessionLocal
from .logic import fetch_national_weather

# Create Tables
Base.metadata.create_all(bind=engine)

# --- THE AUTOMATION ENGINE ---
def scheduled_weather_task():
    """Runs automatically to update weather data."""
    print("⏰ AUTOMATION: Starting scheduled weather scan...")
    db = SessionLocal()
    try:
        fetch_national_weather(db)
    except Exception as e:
        print(f"❌ AUTOMATION ERROR: {e}")
    finally:
        db.close()

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