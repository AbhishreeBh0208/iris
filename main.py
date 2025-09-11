from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from poliastro.bodies import Earth, Sun
from poliastro.twobody import Orbit
from poliastro.maneuver import Maneuver
from fastapi.middleware.cors import CORSMiddleware

# This creates your API server
app = FastAPI(title="IRIS Backend", description="The Brain of the Mission", version="1.0")

# This allows the frontend to talk to your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Your friend's Next.js URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This is the data your frontend will send you
class MissionParameters(BaseModel):
    target_epoch: float  # The chosen time for intercept
    propulsion_type: str # e.g., "chemical"

# This is a test endpoint to see if your server is working
@app.get("/")
def read_root():
    return {"message": "IRIS Backend is online! Hello from the brain!"}

# This is the MOST IMPORTANT endpoint - where the magic happens
@app.post("/simulate/")
def simulate_mission(mission_params: MissionParameters):
    # 1. Get the user's choices from the frontend
    print(f"Received a request to simulate a mission for time: {mission_params.target_epoch}")

    # 2. DO THE MATH (This is a placeholder for now)
    # You will replace this with real poliastro calculations later.
    delta_v = 5.5  # km/s, fake value
    travel_time = 180  # days, fake value

    # 3. Send the result back to the frontend
    return {
        "message": "Simulation successful!",
        "delta_v": delta_v,
        "travel_time": travel_time,
        "success": True
    }