import pandas as pd
import requests
import time

CSV_PATH = "data/raw_sensor_dataset.csv"
BACKEND_URL = "https://oracle01.onrender.com/validate"

df = pd.read_csv(CSV_PATH)

for _, row in df.iterrows():
    payload = {
        "device_id": row["device_id"],
        "wind_pressure": float(row["wind_pressure"]),
        "tilt_angle": float(row["tilt_angle"]),
        "vibration": int(row["vibration"]),
        "internal_pressure": float(row["internal_pressure"]),
        "timestamp": row["timestamp"]
    }

    try:
        response = requests.post(BACKEND_URL, json=payload)
        print(f"Sent → {payload['device_id']}: {response.status_code} → {response.json()}")
    except Exception as e:
        print(f"Failed to send {payload['device_id']}: {str(e)}")

    time.sleep(1)  # Simulate 1-second delay
