from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

app = FastAPI()

API_KEY = os.getenv("API_KEY")

# DB setup
engine = create_engine("sqlite:///weather.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Weather(Base):
    __tablename__ = "weather"
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String)
    temperature = Column(Float)
    time = Column(String)

Base.metadata.create_all(bind=engine)

# ---------------- FRONTEND ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# ---------------- WEATHER API ----------------
@app.get("/weather")
def get_weather(city: str):
    if not API_KEY:
        return {"error": "API key missing"}

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return {"error": "Failed to fetch weather", "details": data}

    temp = data["main"]["temp"]

    # save to DB
    db = SessionLocal()
    record = Weather(
        city=city,
        temperature=temp,
        time=str(datetime.now())
    )
    db.add(record)
    db.commit()
    db.close()

    return {"city": city, "temperature": temp}

# ---------------- HISTORY API ----------------
@app.get("/history")
def history():
    db = SessionLocal()
    data = db.query(Weather).all()
    db.close()

    return [
        {
            "city": d.city,
            "temperature": d.temperature,
            "time": d.time
        }
        for d in data
    ]

# ---------------- HEALTH CHECK ----------------
@app.get("/health")
def health():
    return {"message": "Weather API Running 🚀"}