from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry relative to file location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, "telemetry.json")) as f:
    data = json.load(f)

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

        result[region] = {
            "avg_latency": float(region_df["latency_ms"].mean()),
            "p95_latency": float(np.percentile(region_df["latency_ms"], 95)),
            "avg_uptime": float(region_df["uptime"].mean()),
            "breaches": int((region_df["latency_ms"] > body.threshold_ms).sum())
        }

    return result
