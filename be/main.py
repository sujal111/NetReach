# from fastapi import FastAPI, HTTPException

# from pydantic import BaseModel

# from utils import lookup_ip

 

# app = FastAPI()

 

# class IPRequest(BaseModel):

#     ip: str

 

# class AlertRequest(BaseModel):

#     message: str

#     city: str

 

# # Simulated in-memory user list (you’d use a DB in production)

# user_sessions = [

#     {"user_id": 1, "ip": "216.103.180.25"},  # Fort Smith

#     {"user_id": 2, "ip": "198.51.100.20"},   # Dallas

#     {"user_id": 3, "ip": "203.0.113.10"}     # San Francisco

# ]

 

# @app.post("/lookup")

# def lookup(request: IPRequest):

#     result = lookup_ip(request.ip)

#     if not result:

#         raise HTTPException(status_code=404, detail="IP not found")

#     return result

 

# @app.post("/send-alert")

# def send_alert(alert: AlertRequest):

#     notified_users = []

#     for user in user_sessions:

#         info = lookup_ip(user["ip"])

#         if info and info["city"].lower() == alert.city.lower():

#             # Simulated alert

#             notified_users.append(user["user_id"])

#     return {"message": f"Alert sent to {len(notified_users)} users", "users": notified_users}

 

 

 

 

 

 

#New Code

 

import json

import traceback

from fastapi import FastAPI, HTTPException

from fastapi.responses import JSONResponse

from pydantic import BaseModel

from typing import Optional, List

import openai

import httpx

 

 

client = httpx.Client(verify=False)

 

 

app = FastAPI()

 

# ==================== OpenAI Azure GenAI Setup ====================

openai.api_type = "azure"

api_version = "2023-07-01-preview"

base_url = https://cast-southcentral-nprd-apim.azure-api.net/AITCSG

# base_url = http://localhost:8001/AITCSG

api_key = "f1719a4af60d45ada4097b9570a2c5d0"

model_name = "gpt-4-32k"

 

# ==================== Data Models ====================

 

class IPRequest(BaseModel):

    ip: str

 

class AlertRequest(BaseModel):

    message: str

    city: str

 

class AlertGenerationRequest(BaseModel):

    source: str

    hazard: str

    location: str

    guidance: str

    timing: str

    languages: Optional[List[str]] = ["en"]

 

class OfferGenerationRequest(BaseModel):

    city: str

    user_preferences: List[str]

    purchase_history: List[str]

    event: Optional[str] = None

    weather: Optional[str] = None

    language: Optional[str] = "en"

 

# ==================== Dummy Data ====================

users = {

    1: {"phone": "+11234567890", "city": "Fort Smith"},

    2: {"phone": "+11234567891", "city": "Dallas"},

    3: {"phone": "+11234567892", "city": "Austin"},

}

 

ip_to_location = {

    "216.103.180.25": {"prefix": "216.103.180.0/22", "country": "US", "region": "US-AR", "city": "Fort Smith", "service": "AIA"},

    "10.0.0.1": None

}

 

# ==================== Existing APIs ====================

 

@app.post("/lookup")

def lookup_ip(req: IPRequest):

    location = ip_to_location.get(req.ip)

    if not location:

        raise HTTPException(status_code=404, detail="IP not found")

    return {

        "ip": req.ip,

        **location

    }

 

# @app.post("/send-alert")

# def send_alert(req: AlertRequest):

#     recipients = [uid for uid, u in users.items() if u["city"].lower() == req.city.lower()]

#     return {"message": f"Alert sent to {len(recipients)} users", "users": recipients}

 
 @app.post("/send-personalized-alert")
def send_personalized_alert(req: AlertRequest):
    recipients = [uid for uid, u in users.items() if u["city"].lower() == req.city.lower()]
    
    personalized_alerts = {}
    for uid in recipients:
        user = users[uid]
        prompt = f"""
        You are a government alert system. Generate a short emergency alert message (under 160 characters) for a user in {req.city}.
        The context is: "{req.message}".
        Make it direct, clear, and suitable for SMS.
        """
        try:
            response = openai.AzureOpenAI(
                azure_endpoint=base_url,
                api_key=api_key,
                api_version=api_version,
                http_client=client
            ).chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            personalized_alerts[uid] = response.choices[0].message.content.strip()
        except Exception as e:
            personalized_alerts[uid] = f"Error generating message: {str(e)}"

    return {
        "message": f"Personalized alerts generated for {len(recipients)} users",
        "alerts": personalized_alerts
    }




# ==================== Feature 3: AI Emergency Message ====================

 

@app.post("/generate-alert")

def generate_alert(req: AlertGenerationRequest):

    prompt = f"""

Generate an emergency alert with the following details:

- Source: {req.source}

- Hazard: {req.hazard}

- Location: {req.location}

- Guidance: {req.guidance}

- Timing: {req.timing}

Create the message in structured and concise format, keeping it under 160 characters. Also translate the message into: {', '.join(req.languages)}.

Return as JSON with keys: 'original', and one per language.

"""

 

    try:

        response = openai.AzureOpenAI(azure_endpoint=base_url, api_key=api_key, api_version=api_version,http_client=client).chat.completions.create(

            model=model_name,

            messages=[{"role": "user", "content": prompt}],

            temperature=0.5,

        )

        return JSONResponse(json.loads(response.choices[0].message.content))

    except Exception as e:

        print(traceback.format_exc())

        raise HTTPException(status_code=500, detail=str(e))

 

# ==================== Feature 4: Localized Offer Generator ====================

 

@app.post("/generate-offer")

def generate_offer(req: OfferGenerationRequest):

    prompt = f"""

You are a marketing assistant. Generate a localized and culturally relevant marketing message for users in {req.city}.

They have shown preferences for: {', '.join(req.user_preferences)}.

Their purchase history includes: {', '.join(req.purchase_history)}.

Current event (optional): {req.event or "None"}

Current weather (optional): {req.weather or "None"}

Preferred language: {req.language}

 

Make the offer compelling, concise, and appropriate for the region.

"""

 

    try:

        response = openai.AzureOpenAI(azure_endpoint=base_url, api_key=api_key, api_version=api_version,http_client=client).chat.completions.create(

            model=model_name,

            messages=[{"role": "user", "content": prompt}],

            temperature=0.7

        )

        return {

            "city": req.city,

            "offer": response.choices[0].message.content,

        }

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))