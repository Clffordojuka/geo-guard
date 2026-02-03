# scripts/train_model.py
import sys
import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# Setup Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "kenya_weather_history.csv")
MODEL_PATH = os.path.join(BASE_DIR, "backend", "seasonal_model.pkl")

def train():
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: Data file not found at {DATA_PATH}")
        print("   -> Run 'python -m scripts.generate_history' first.")
        return

    print(f"🧠 Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # Features (X): Day of Year
    # Target (y): Rainfall
    X = df[["day_of_year"]]
    y = df["rainfall_mm"]
    
    # Split Data (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Random Forest
    print("🏋️  Training Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print(f"📊 Model Performance:")
    print(f"   - Mean Absolute Error: {mae:.2f} mm")
    print(f"   - Accuracy (R² Score): {r2:.2f}")
    
    # Save Model
    joblib.dump(model, MODEL_PATH)
    print(f"💾 Model saved to: {MODEL_PATH}")

if __name__ == "__main__":
    train()