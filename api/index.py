from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import json

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load JSON telemetry
with open("telemetry.json") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: float

@app.post("/api")
def compute_metrics(body: RequestBody):
    result = {}

    for region in body.regions:
        region_df = df[df["region"] == region]

        if len(region_df) == 0:
            continue

        avg_latency = region_df["latency_ms"].mean()
        p95_latency = np.percentile(region_df["latency_ms"], 95)
        avg_uptime = region_df["uptime"].mean()
        breaches = (region_df["latency_ms"] > body.threshold_ms).sum()

        result[region] = {
            "avg_latency": round(float(avg_latency), 2),
            "p95_latency": round(float(p95_latency), 2),
            "avg_uptime": round(float(avg_uptime), 4),
            "breaches": int(breaches),
        }

    return result
