# main.py (FastAPI backend)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Allow CORS for frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
mock_data = [
    {"prefix": "216.103.180.0/22", "country": "US", "region": "US-AR", "city": "Fort Smith", "service": "AIA"},
    {"prefix": "198.51.100.0/24", "country": "US", "region": "US-TX", "city": "Dallas", "service": "ABC"},
    {"prefix": "203.0.113.0/24", "country": "US", "region": "US-CA", "city": "San Francisco", "service": "XYZ"}
]

class AlertRequest(BaseModel):
    city: str
    message: str

@app.post("/send-alert")
def send_alert(alert: AlertRequest):
    users_in_city = [item["prefix"] for item in mock_data if item["city"].lower() == alert.city.lower()]
    return {
        "message": f"Alert sent to {len(users_in_city)} user(s) in {alert.city}.",
        "users": users_in_city
    }

@app.get("/mock-alert")
def mock_alert():
    # Pick first mock item to return
    return {
        "city": mock_data[1]["city"],  # Dallas
        "message": f"Important update from service {mock_data[1]['service']} in {mock_data[1]['city']}."
    }
