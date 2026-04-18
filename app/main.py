from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.weather import get_weather
from app.database import SessionLocal, WeatherLog

app = FastAPI()

# CORS fix
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Weather API Running 🚀"}

@app.get("/weather")
def weather(city: str = "Pune"):
    try:
        data = get_weather(city)

        if data.get("cod") != 200:
            raise HTTPException(status_code=400, detail=data.get("message"))

        temp = data["main"]["temp"]

        db = SessionLocal()
        log = WeatherLog(city=data["name"], temperature=temp)
        db.add(log)
        db.commit()
        db.close()

        return {
            "city": data["name"],
            "temperature": temp
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
def get_history(city: str = None, limit: int = Query(default=10)):
    db = SessionLocal()
    query = db.query(WeatherLog)

    if city:
        query = query.filter(WeatherLog.city == city)

    logs = query.order_by(WeatherLog.timestamp.desc()).limit(limit).all()
    db.close()

    return [
        {
            "city": log.city,
            "temperature": log.temperature,
            "time": log.timestamp
        }
        for log in logs
    ]