from fastapi import FastAPI, Request
from datetime import datetime, timedelta
import pandas as pd
import os

app = FastAPI()

# File paths
os.makedirs("data", exist_ok=True)
CSV_VALIDATED = "data/TrustedSensorDataset.csv"
CSV_REJECTED = "data/RejectedSensorLog.csv"

# Whitelisted panels
TRUSTED_IDS = {"20-N-22", "15-N-10", "10-E-05", "19-E-12", "5-N-03"}

# Acceptable sensor ranges
LIMITS = {
    "wind_pressure": (0, 30),
    "tilt_angle": (0, 90),
    "vibration": (0, 5),
    "internal_pressure": (0.8, 1.5),
}

@app.post("/validate")
async def validate_sensor_data(request: Request):
    data = await request.json()
    device = data.get("device_id")
    timestamp = data.get("timestamp")
    reason = ""

    # Check device ID
    if device not in TRUSTED_IDS:
        reason = "untrusted device"

    # Check timestamp format and freshness
    if reason == "":
        try:
            dt = datetime.fromisoformat(timestamp)
            if datetime.utcnow() - dt > timedelta(minutes=5):
                reason = "timestamp too old"
        except:
            reason = "timestamp format error"

    # Check sensor ranges
    if reason == "":
        for sensor, (lo, hi) in LIMITS.items():
            value = data.get(sensor)
            if value is None or not (lo <= float(value) <= hi):
                reason = f"{sensor} out of bounds"
                break

    # Save to the appropriate file
    df = pd.DataFrame([data])
    if reason:
        df["reason"] = reason
        df.to_csv(CSV_REJECTED, mode="a", header=not os.path.exists(CSV_REJECTED), index=False)
        return {"status": "rejected", "reason": reason}
    else:
        df.to_csv(CSV_VALIDATED, mode="a", header=not os.path.exists(CSV_VALIDATED), index=False)
        return {"status": "accepted", "message": "validated"}
@app.get("/")
def read_root():
    return {"message": "Oracle01 backend is live!"}

