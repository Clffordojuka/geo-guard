# 🌍 GeoGuard Kenya: National Climate Monitor

**GeoGuard** is a hybrid early-warning system that creates a "Digital Twin" of Kenya's climate risks. It bridges the gap between modern science, traditional wisdom, and the digital divide by combining satellite data, **Machine Learning**, **Indigenous Knowledge (IK)**, **USSD**, and **AI Vision** to predict and visualize climate disasters (Floods, Droughts, Landslides) across 47 counties.

![Streamlit Badge](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![FastAPI Badge](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostGIS Badge](https://img.shields.io/badge/PostGIS-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Python Badge](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Scikit-Learn Badge](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![AfricasTalking Badge](https://img.shields.io/badge/Africa's%20Talking-USSD-orange?style=for-the-badge)
![Twilio Badge](https://img.shields.io/badge/Twilio-WhatsApp-red?style=for-the-badge&logo=twilio)
![Gemini Badge](https://img.shields.io/badge/Google%20Gemini-AI%20Vision-8E75B2?style=for-the-badge&logo=google)

---

## 📸 System Previews

**1. The Live Dashboard**
*Real-time monitoring of 26 Risk Zones using OpenWeatherMap & PostGIS.*
![Dashboard Main View](screenshots/dashboard_main.png)
![Dashboard Risk Map](screenshots/dashboard_map.png)

---

## 🚀 The Problem
National weather forecasts are too broad and often disconnected from local realities.
1.  **The Scientific Gap:** Telling a farmer "Heavy Rain in Nakuru" is insufficient; they need to know **"Flash Flood risk in Mai Mahiu Gully in 30 minutes."**
2.  **The Cultural Gap:** Satellite data often ignores the ground-level biological signs (bio-indicators) that indigenous communities have relied on for centuries.
3.  **The Digital Gap:** Many farmers cannot access complex web dashboards but use WhatsApp or Feature Phones daily.

**GeoGuard bridges this gap by:**
* **Real-Time Monitoring:** Tracking **26 Critical Risk Zones** 24/7 via OpenWeatherMap API.
* **Cultural Integration:** Validating **Indigenous Knowledge** (e.g., behavior of Safari Ants) against sensor data.
* **AI Vision:** Allowing citizens to snap photos of disasters for instant analysis via **Google Gemini**.
* **Inclusivity:** Providing a **USSD Interface** for offline users and a **WhatsApp Bot** for smartphone users.

---

## 🛠️ Tech Stack & Architecture

| Component | Technology | Function |
| :--- | :--- | :--- |
| **The Brain** | **FastAPI** + **APScheduler** | Automates data fetching and handles API logic. |
| **The Vision** | **Google Gemini 2.0 Flash** | AI Model that analyzes photos for disaster risks. |
| **The Oracle** | **Scikit-Learn** + **Random Forest** | ML Model predicting seasonal rainfall onset. |
| **The Messenger** | **Twilio (WhatsApp)** | Chatbot interface for submitting photos/reports. |
| **The Reach** | **Africa's Talking** + **Ngrok** | USSD interface for offline feature phone users. |
| **The Memory** | **PostgreSQL** + **PostGIS** | Stores complex risk polygons (Spatial Data). |
| **The Face** | **Streamlit** + **Folium** | Live interactive dashboard for visualization. |
| **Manager** | **uv** + **Docker** | Dependency management and database containerization. |

---

## 🤖 GeoGuard AI Bot (WhatsApp)
**"AI Vision for Everyone"**

We turned every smartphone into a remote sensor.
* **Visual Analysis:** A user sends a photo of a rising river or cracked wall.
* **The AI:** Google Gemini (Flash 2.0) analyzes the image for risks (Flood, Drought, Landslide).
* **The Response:** The bot replies with a risk assessment and immediate safety advice.

![WhatsApp Bot Demo](screenshots/whatsapp_bot.png)
![WhatsApp Bot Demo](screenshots/whatsapp_bot_alert.png)

---

## 🔮 New Feature: AI Seasonal Predictor
**"From Reactive to Proactive"**

We moved beyond just *monitoring* disasters to *predicting* them.
* **The Model:** A **Random Forest Regressor** trained on 10 years of historical Kenyan weather data.
* **The Output:** A 90-day forecast graph that identifies the onset of "Long Rains" vs "Short Rains."
* **The Impact:** Helps farmers decide exactly when to plant (e.g., "Wait 2 weeks, rain peak is approaching").

---

## 🌿 Asili Smart (Web, USSD & WhatsApp)
**"Connecting Tradition with Technology"**

Asili Smart is a dedicated module that validates indigenous bio-indicators.
1.  **Observation:** A user reports a sign (e.g., *"Frogs croaking loudly"* or *"Goat Intestines Clear"*).
2.  **Geolocation:** The system detects location via Menu Selection (USSD) or NLP (WhatsApp).
3.  **Validation:** The engine cross-references the sign with live satellite sensors:
    * *If Signs Match Sensors:* **"✅ VALIDATED"** (High Confidence Alert).
    * *If Signs Conflict:* **"⚠️ CAUTION"** (Discrepancy Detected).

---

## 📞 USSD "Last Mile" Interface
**"No Smartphone? No Problem."**

We integrated **Africa's Talking API** to bring GeoGuard to feature phones.
* **How it works:** Farmers dial a code (e.g., `*384*...`) to access the system.
* **Features:**
    1.  **Report Signs:** Submit Asili Smart observations (Ants, Intestines, etc.).
    2.  **Get Warnings:** Drill-down menu to check status for specific zones (e.g., *North -> Turkana -> Kibish*).

**USSD Interaction Flow:**
![USSD Main Menu](screenshots/ussd_menu.png)
![USSD Region Selection](screenshots/ussd_regions.png)
![USSD Alert Message](screenshots/ussd_alert.png)

---

## 📦 Setup Guide (For Teammates)

Follow these steps to get the system running on your local machine.

### 1. Prerequisites
* **Docker Desktop** (Must be running for the database).
* **uv** (An extremely fast Python package manager).
* **Ngrok** (For USSD/WhatsApp tunneling).

### 2. Clone & Install
```bash
# Clone the repository
git clone [https://github.com/Clffordojuka/geo-guard.git](https://github.com/Clffordojuka/geo-guard.git)
cd geo-guard

# Install dependencies (FastAPI, Streamlit, Scikit-Learn, Twilio, Google GenAI)
uv sync

```

### 3. Start the Database (Docker)

We use a Docker container for PostGIS so you don't have to install Postgres locally.

```bash
# Spin up the database container
docker run --name geoguard-db -e POSTGRES_PASSWORD=hackathon -p 5432:5432 -d postgis/postgis

```

### 4. Configuration

Create a `.env` file in the root folder with your keys:

```env
# Database
DATABASE_URL=postgresql://postgres:hackathon@localhost:5432/geoguard

# APIs
OPENWEATHER_API_KEY=your_openweather_key
GEMINI_API_KEY=your_google_ai_studio_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token

```

### 5. Seed the Data & Train the AI

Populate the database and train the machine learning model:

```bash
# 1. Create Risk Zones
uv run python -m scripts.seed_db

# 2. Generate Historical Data & Train Model
uv run python -m scripts.generate_history
uv run python -m scripts.train_model

```

### 6. Run Tunnels (Optional)

If testing USSD or WhatsApp locally:

```bash
# Expose your local API to the internet
ngrok http 8000
# Copy the URL to Africa's Talking (USSD) or Twilio Console (WhatsApp)

```

---

## 🖥️ How to Run the App

Open **two separate terminals** to run the full stack:

**Terminal 1: The Backend (Brain)**
*Starts the API, USSD/WhatsApp Listeners, and automated weather scheduler.*

```bash
uv run uvicorn backend.app:app --reload

```

*> Look for "✅ System Online: Weather Scheduler Started."*

**Terminal 2: The Frontend (Face)**
*Launches the interactive dashboard.*

```bash
uv run streamlit run frontend/dashboard.py

```

---

## 🌍 Hybrid Hazard Logic

The system uses a "Multi-Source" decision engine:

### 1. Scientific Thresholds

* **🌊 Flood Risk:** Rainfall > **50mm/hr** in Urban/Riverine zones.
* **🍂 Drought Risk:** Temp > **32°C** AND Rainfall < **1mm** in ASAL counties.
* **⛰️ Landslide Risk:** Rainfall > **30mm/hr** in Steep Slope zones.

### 2. Indigenous Validation Logic

* **Sign:** *Safari Ants moving in lines* (Indicates Rain).
* *Validation:* Checks if Barometric Pressure is dropping + Humidity > 60%.

---

## 🤝 Contributing

1. **Pull** the latest changes: `git pull origin main`
2. **Make changes** and test locally.
3. **Push:** `git push origin main`

*Built for the International Energy and Sustainability Summit (IESS) Hackathon 2026.*