from fastapi import FastAPI
from .database import engine, Base
from .models import WeatherLog, RiskZone

# CREATE TABLES ON STARTUP
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"status": "GeoGuard Backend Online"}