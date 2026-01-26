# 🌍 GeoGuard Kenya: National Climate Monitor

**GeoGuard** is a hyperlocal early-warning system that creates a "Digital Twin" of Kenya's climate risks. It combines real-time satellite weather data with static risk profiles to predict and visualize climate disasters (Floods, Droughts, Landslides) across 47 counties.

![Streamlit Badge](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![FastAPI Badge](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostGIS Badge](https://img.shields.io/badge/PostGIS-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Python Badge](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)

---

## 🚀 The Problem
National weather forecasts are too broad. Telling a farmer "Heavy Rain in Nakuru" is insufficient; they need to know **"Flash Flood risk in Mai Mahiu Gully in 30 minutes."**

**GeoGuard bridges this gap by:**
1.  Mapping **38 Critical Risk Zones** (informal settlements, steep slopes, arid lands).
2.  Monitoring them **24/7** using automated satellite data fetchers.
3.  Applying specific **Hazard Logic** (e.g., Drought = Heat > 32°C + Dry Soil).

---

## 🛠️ Tech Stack & Architecture

| Component | Technology | Function |
| :--- | :--- | :--- |
| **The Brain** | **FastAPI** + **APScheduler** | Automates data fetching every 60 mins. |
| **The Memory** | **PostgreSQL** + **PostGIS** | Stores complex risk polygons (Spatial Data). |
| **The Face** | **Streamlit** + **Folium** | Live interactive dashboard for visualization. |
| **Manager** | **uv** + **Docker** | Dependency management and database containerization. |

---

## 📦 Setup Guide (For Teammates)

Follow these steps to get the system running on your local machine.

### 1. Prerequisites
* **Docker Desktop** (Must be running for the database).
* **uv** (An extremely fast Python package manager).
  * *Install uv:* `pip install uv` (or `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### 2. Clone & Install
```bash
# Clone the repository
git clone [https://github.com/Clffordojuka/geo-guard.git](https://github.com/Clffordojuka/geo-guard.git)
cd geo-guard

# Install dependencies (This replaces pip install -r requirements.txt)
uv sync

```

### 3. Start the Database (Docker)

We use a Docker container for PostGIS so you don't have to install Postgres locally.

```bash
# Spin up the database container
docker run --name geoguard-db -e POSTGRES_PASSWORD=hackathon -p 5432:5432 -d postgis/postgis

```

### 4. Configuration

Create a `.env` file in the root folder:

```env
# .env
DATABASE_URL=postgresql://postgres:hackathon@localhost:5432/geoguard
OPENWEATHER_API_KEY=your_openweather_api_key_here

```

### 5. Seed the Data

Populate the database with the 30+ risk zones (Mathare, Mandera, West Pokot, etc.):

```bash
uv run python -m scripts.seed_db

```

---

## 🖥️ How to Run the App

Open **two separate terminals** to run the full stack:

**Terminal 1: The Backend (Brain)**
*Starts the API and the automated weather scheduler.*

```bash
uv run uvicorn backend.app:app --reload

```

*> Look for "⏰ AUTOMATION: Starting scheduled weather scan..."*

**Terminal 2: The Frontend (Face)**
*Launches the interactive dashboard.*

```bash
uv run streamlit run frontend/dashboard.py

```

---

## 🎮 Simulation Mode (Hackathon Demo)

Since disasters don't happen on schedule, we built a **Simulation Engine** for the judges.

1. Open the Dashboard sidebar.
2. Check the box **`🚨 SIMULATE DISASTER`**.
3. **What happens:**
* The system injects fake "heavy rain" data (65mm/hr) into **Mathare** and **Mai Mahiu**.
* A **Pulsing Red Alert Banner** appears at the top.
* Map markers turn **RED** to indicate critical failure.



---

## 🌍 Monitored Logic

The system uses "Multi-Hazard Detection" logic:

* **🌊 Flood Risk:** Triggered if Rainfall > **50mm/hr** in Urban/Riverine zones.
* **🍂 Drought Risk:** Triggered if Temp > **32°C** AND Rainfall < **1mm** in ASAL counties (Mandera, Wajir, etc.).
* **⛰️ Landslide Risk:** Triggered if Rainfall > **30mm/hr** in Steep Slope zones (West Pokot, Murang'a).

---

## 🤝 Contributing

1. **Pull** the latest changes: `git pull origin main`
2. **Make changes** and test locally.
3. **Push:** `git push origin main`

*Built for the International Energy and Sustainability Summit (IESS) Hackathon 2026.*