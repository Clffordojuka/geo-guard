# scripts/generate_history.py
import sys
import os
import pandas as pd
import numpy as np
import datetime

# Add parent directory to path to ensure we can find paths easily
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def generate_kenya_weather_history(years=10):
    print("⏳ Generating 10 years of historical weather data...")
    
    # Define file path using your structure
    output_path = os.path.join("data", "processed", "kenya_weather_history.csv")
    
    start_date = datetime.date(2015, 1, 1)
    end_date = datetime.date(2025, 1, 1)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    
    for date in dates:
        day_of_year = date.dayofyear
        
        # --- Simulate Seasonality (The "Signal") ---
        # 1. Long Rains (Peak ~April, Day 105)
        long_rain_prob = 18 * np.exp(-((day_of_year - 105)**2) / (2 * 25**2))
        
        # 2. Short Rains (Peak ~November, Day 320)
        short_rain_prob = 12 * np.exp(-((day_of_year - 320)**2) / (2 * 25**2))
        
        # Base trend + Random Noise (0 to 5mm variance)
        base_rain = long_rain_prob + short_rain_prob
        rainfall = max(0, base_rain + np.random.normal(0, 4)) 
        
        # Temperature is inverse to rain (Cooler when raining)
        temp = 29 - (rainfall * 0.15) + np.random.normal(0, 1.5)
        
        data.append({
            "date": date,
            "day_of_year": day_of_year,
            "rainfall_mm": round(rainfall, 2),
            "temperature_c": round(temp, 1)
        })
        
    df = pd.DataFrame(data)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"✅ Data saved to: {output_path} ({len(df)} rows)")

if __name__ == "__main__":
    generate_kenya_weather_history()