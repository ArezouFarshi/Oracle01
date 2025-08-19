from fastapi import FastAPI, Request
from datetime import datetime, timedelta
import pandas as pd
import os

app = FastAPI()

# Ensure /data folder exists
os.makedirs("data", exist_ok=True)

@app.get("/")
def root():
    return {"message": "Oracle01 backend is live!"}

@app.post("/validate")
async def validate(request: Request):
    data = await request.json()
    required_fields = ["device_id", "wind_pressure", "tilt_angle", "vibration", "internal_pressure", "timestamp"]

    # Check required fields
    if not all(field in data for field in required_fields):
        return {"status": "error", "reason": "Missing fields", "received": data}

    # Validate timestamp (max 5 min old)
    try:
        ts = datetime.fromisoformat(data["timestamp"])
        if datetime.utcnow() - ts > timedelta(minutes=5):
            raise ValueError("Stale timestamp")
    except:
        return {"status": "rejected", "reason": "Invalid or stale timestamp", "row": data}

    # Validate ranges
    wind = float(data["wind_pressure"])
    tilt = float(data["tilt_angle"])
    vib = int(data["vibration"])
    pressure = float(data["internal_pressure"])

    if not (0 <= wind <= 30):
        return log_rejection(data, "wind_pressure out of range")
    if not (0 <= tilt <= 90):
        return log_rejection(data, "tilt_angle out of range")
    if vib not in [0, 1]:
        return log_rejection(data, "vibration not 0 or 1")
    if not (0.8 <= pressure <= 1.5):
        return log_rejection(data, "internal_pressure out of range")

    # If all checks passed → valid row
    df = pd.DataFrame([data])
    df.to_csv("data/TrustedSensorDataset.csv", mode='a', header=not os.path.exists("data/TrustedSensorDataset.csv"), index=False)
    return {"status": "accepted", "data_saved_to": "TrustedSensorDataset.csv"}

def log_rejection(row, reason):
    row["rejection_reason"] = reason
    df = pd.DataFrame([row])
    df.to_csv("data/RejectedSensorLog.csv", mode='a', header=not os.path.exists("data/RejectedSensorLog.csv"), index=False)
    return {"status": "rejected", "reason": reason, "row": row}
