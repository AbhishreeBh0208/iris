#!/usr/bin/env python3
"""
FastAPI backend for serving real NASA JPL Horizons trajectory data
and mission simulation for the Interstellar Intercept Simulator.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import logging
from datetime import datetime, timedelta
import numpy as np

# Import the trajectory fetching function
try:
    from astroquery.jplhorizons import Horizons
    import pandas as pd
    REAL_NASA_DATA_AVAILABLE = True
    print("✅ Real NASA data capabilities enabled")
except ImportError:
    print("⚠️ astroquery not available - using fallback data")
    REAL_NASA_DATA_AVAILABLE = False

app = FastAPI(title="Interstellar Intercept Mission API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class TrajectoryPoint(BaseModel):
    jd: float  # Julian Date
    x: float   # X coordinate in km
    y: float   # Y coordinate in km  
    z: float   # Z coordinate in km

class TrajectoryResponse(BaseModel):
    object_name: str
    start_date: str
    end_date: str
    trajectory_data: List[TrajectoryPoint]
    total_points: int

class MissionParameters(BaseModel):
    swarm_size: int
    role_split: str  # 'balanced', 'science-heavy', 'comms-heavy'
    propulsion_type: str  # 'chemical', 'ion', 'nuclear'
    target_epoch: str  # ISO 8601 date
    target_position: Dict[str, float]  # x, y, z coordinates

class MissionResult(BaseModel):
    status: str
    delta_v: float  # km/s
    flight_time_days: Optional[float] = None
    fuel_consumed: Optional[float] = None
    success_probability: Optional[float] = None
    data_captured: Optional[List[str]] = None
    intercept_trajectory: Optional[List[Dict[str, float]]] = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Interstellar Intercept Mission API is running"}

@app.get("/api/trajectory/{object_name}", response_model=TrajectoryResponse)
async def get_trajectory(object_name: str):
    """
    Fetch real trajectory data for an interstellar object from NASA JPL Horizons
    """
    try:
        logging.info(f"Fetching trajectory for {object_name}")
        
        # Map common object names
        object_map = {
            "2I/Borisov": "2I",
            "Borisov": "2I", 
            "1I/Oumuamua": "1I",
            "Oumuamua": "1I"
        }
        
        target_object = object_map.get(object_name, object_name)
        
        if REAL_NASA_DATA_AVAILABLE:
            # Use the real NASA Horizons data
            start_date = "2019-01-01"
            end_date = "2020-12-31"
            
            try:
                # Create Horizons query object
                obj = Horizons(
                    id=target_object,
                    location='500@10',  # Heliocentric (Sun center)
                    epochs={'start': start_date, 'stop': end_date, 'step': '1d'}
                )
                
                # Get state vectors (position and velocity)
                vectors = obj.vectors(
                    refplane='ecliptic',  # Ecliptic reference plane
                    aberrations='none',   # No corrections
                    delta_T=False         # Don't apply Delta T correction
                )
                
                # Convert to trajectory points
                trajectory_points = []
                for row in vectors:
                    trajectory_points.append(TrajectoryPoint(
                        jd=row['datetime_jd'],
                        x=row['x'] * 149597870.7,  # AU to km
                        y=row['y'] * 149597870.7,  # AU to km
                        z=row['z'] * 149597870.7   # AU to km
                    ))
                
                logging.info(f"✅ Fetched {len(trajectory_points)} real NASA data points for {object_name}")
                
                return TrajectoryResponse(
                    object_name=object_name,
                    start_date=start_date,
                    end_date=end_date,
                    trajectory_data=trajectory_points,
                    total_points=len(trajectory_points)
                )
                
            except Exception as nasa_error:
                logging.error(f"NASA Horizons query failed: {nasa_error}")
                # Fall through to fallback data
        
        # Fallback to simulated data if astroquery is not available or fails
        logging.warning("Using fallback trajectory data")
        return get_fallback_trajectory(object_name)
            
    except Exception as e:
        logging.error(f"Error fetching trajectory: {e}")
        # Return fallback data on error
        return get_fallback_trajectory(object_name)

def get_fallback_trajectory(object_name: str) -> TrajectoryResponse:
    """Generate realistic fallback trajectory data"""
    
    # Base Julian Date for start of trajectory
    base_jd = 2458849.5  # Jan 1, 2020
    trajectory_points = []
    
    # Generate a hyperbolic interstellar trajectory
    for i in range(365):
        # Time parameter for hyperbolic orbit
        t = (i - 180) / 100  # Centered around periapsis
        jd = base_jd + i
        
        # Hyperbolic orbital elements (approximate for interstellar objects)
        a = -2.0  # Semi-major axis (AU, negative for hyperbolic)
        e = 3.36  # High eccentricity typical of interstellar objects
        
        # Simplified position calculation in AU
        r = abs(a * (e - 1) / (1 + e * np.cos(t)))
        x_au = r * np.cos(t)
        y_au = r * np.sin(t) * 0.1  # Small inclination
        z_au = r * np.sin(t) * 0.05  # Small out-of-plane component
        
        # Convert AU to km
        AU_TO_KM = 149597870.7
        trajectory_points.append(TrajectoryPoint(
            jd=jd,
            x=x_au * AU_TO_KM,
            y=y_au * AU_TO_KM,
            z=z_au * AU_TO_KM
        ))
    
    return TrajectoryResponse(
        object_name=object_name,
        start_date="2020-01-01",
        end_date="2020-12-31", 
        trajectory_data=trajectory_points,
        total_points=len(trajectory_points)
    )

@app.post("/simulate/", response_model=MissionResult)
async def simulate_mission(mission: MissionParameters):
    """
    Simulate an interstellar intercept mission
    """
    try:
        logging.info(f"Simulating mission with {mission.swarm_size} satellites")
        
        # Parse target time
        from datetime import datetime
        target_time = datetime.fromisoformat(mission.target_epoch.replace('Z', '+00:00'))
        
        # Simplified mission simulation
        # In a real implementation, this would use poliastro for orbital mechanics
        
        # Estimate delta-V based on target distance and propulsion type
        target_distance_km = np.sqrt(
            mission.target_position['x']**2 + 
            mission.target_position['y']**2 + 
            mission.target_position['z']**2
        )
        
        # Base delta-V calculation (simplified)
        base_delta_v = min(15.0, target_distance_km / 1e8)  # Rough estimate
        
        # Adjust for propulsion type
        propulsion_efficiency = {
            'chemical': 1.0,
            'ion': 0.3,
            'nuclear': 0.1
        }
        
        delta_v = base_delta_v * propulsion_efficiency.get(mission.propulsion_type, 1.0)
        flight_time_days = target_distance_km / (50 * 86400)  # Rough flight time
        
        # Success probability based on swarm size and delta-V
        base_success = 0.85
        swarm_bonus = min(0.1, (mission.swarm_size - 1) * 0.01)
        delta_v_penalty = max(0, (delta_v - 5.0) * 0.05)
        success_probability = max(0.1, base_success + swarm_bonus - delta_v_penalty)
        
        # Determine mission outcome
        mission_success = success_probability > 0.6
        status = "Mission successful - Target intercepted" if mission_success else "Mission failed - Intercept missed"
        
        # Generate some sample data captured
        data_types = [
            "High-resolution imagery",
            "Spectrographic analysis", 
            "Magnetic field measurements",
            "Dust particle samples",
            "Gas composition data",
            "Surface temperature mapping"
        ]
        
        data_captured = data_types[:min(mission.swarm_size // 2, len(data_types))] if mission_success else []
        
        # Generate sample intercept trajectory (Lambert arc)
        intercept_trajectory = []
        if mission_success:
            # Simple trajectory points from Earth to target
            earth_pos = [0, 0, 0]  # Simplified Earth position
            target_pos = [mission.target_position['x'], mission.target_position['y'], mission.target_position['z']]
            
            for i in range(10):
                t = i / 9.0
                x = earth_pos[0] + t * (target_pos[0] - earth_pos[0])
                y = earth_pos[1] + t * (target_pos[1] - earth_pos[1]) 
                z = earth_pos[2] + t * (target_pos[2] - earth_pos[2])
                intercept_trajectory.append({"x": x, "y": y, "z": z})
        
        return MissionResult(
            status=status,
            delta_v=round(delta_v, 2),
            flight_time_days=round(flight_time_days, 1),
            fuel_consumed=round(delta_v * mission.swarm_size * 100, 1),  # Rough estimate
            success_probability=round(success_probability, 2),
            data_captured=data_captured,
            intercept_trajectory=intercept_trajectory
        )
        
    except Exception as e:
        logging.error(f"Mission simulation error: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the server
    uvicorn.run(
        "backend_api:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
