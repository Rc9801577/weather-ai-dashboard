from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "Weather AI Dashboard Running 🚀",
        "status": "live"
    }

@app.get("/weather")
def weather(city: str):
    return {
        "city": city,
        "temperature": 30
    }

@app.get("/history")
def history():
    return []