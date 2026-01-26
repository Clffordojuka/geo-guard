from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from .database import Base

class WeatherLog(Base):
    __tablename__ = "weather_logs"
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String)
    temperature = Column(Float)
    rainfall_1h = Column(Float)
    humidity = Column(Float)
    lat = Column(Float)
    lon = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class RiskZone(Base):
    __tablename__ = "risk_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)         
    county = Column(String)      
    risk_level = Column(String)   
    disaster_type = Column(String)
    description = Column(String)  
    
    # The Shape
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326))