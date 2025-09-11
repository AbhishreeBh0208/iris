"""
Backend Data Structures for Interstellar Object Intercept Mission
================================================================

This file defines the exact data structures your FastAPI backend should use
to communicate with the frontend, matching the trajectory flowchart workflow.

Author: Mission Control System
Date: September 11, 2025
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# 1. TRAJECTORY DATA STRUCTURES
# ============================================================================

class TrajectoryPoint(BaseModel):
    """A single point in the interstellar object's trajectory."""
    jd: float = Field(..., description="Julian Date")
    x: float = Field(..., description="X coordinate in km (heliocentric ecliptic)")
    y: float = Field(..., description="Y coordinate in km (heliocentric ecliptic)")
    z: float = Field(..., description="Z coordinate in km (heliocentric ecliptic)")


class TrajectoryResponse(BaseModel):
    """Response for GET /api/trajectory/{object_name}"""
    object_name: str = Field(..., description="Name of the interstellar object")
    trajectory_data: List[TrajectoryPoint] = Field(..., description="Array of trajectory points")
    start_date: str = Field(..., description="Start date of trajectory (ISO format)")
    end_date: str = Field(..., description="End date of trajectory (ISO format)")
    total_points: int = Field(..., description="Total number of trajectory points")
    uncertainty_level: float = Field(..., description="Trajectory uncertainty factor (0-1)")


# ============================================================================
# 2. MISSION SIMULATION STRUCTURES
# ============================================================================

class MissionParameters(BaseModel):
    """Input parameters for mission simulation."""
    swarm_size: int = Field(..., ge=5, le=50, description="Number of nanosatellites")
    role_split: str = Field(..., description="Mission configuration: imaging, science, balanced")
    propulsion_type: str = Field(..., description="Propulsion system: chemical, advanced")
    target_epoch: str = Field(..., description="Target intercept time (ISO format)")
    target_position: Dict[str, float] = Field(..., description="Target position {x, y, z} in km")


class InterceptTrajectoryPoint(BaseModel):
    """A point in the swarm's intercept trajectory."""
    x: float = Field(..., description="X coordinate in km")
    y: float = Field(..., description="Y coordinate in km") 
    z: float = Field(..., description="Z coordinate in km")
    t: Optional[float] = Field(None, description="Time offset from launch (days)")


class MissionResults(BaseModel):
    """Response for POST /simulate/ - Complete mission simulation results."""
    status: str = Field(..., description="Mission outcome: success, failure, partial")
    delta_v: float = Field(..., description="Total delta-V required (km/s)")
    
    # Optional detailed results
    flight_time_days: Optional[float] = Field(None, description="Time of flight (days)")
    fuel_consumed: Optional[float] = Field(None, description="Fuel consumption fraction (0-1)")
    success_probability: Optional[float] = Field(None, description="Mission success probability (0-1)")
    
    # Data collection results
    data_captured: Optional[List[str]] = Field(None, description="List of data types captured")
    
    # Trajectory visualization data
    intercept_trajectory: Optional[List[InterceptTrajectoryPoint]] = Field(
        None, description="Points for drawing the swarm's path"
    )
    
    # Additional mission details
    launch_window: Optional[Dict[str, str]] = Field(None, description="Optimal launch window")
    uncertainty_penalty: Optional[float] = Field(None, description="Uncertainty-based penalty applied")


# ============================================================================
# 3. UNCERTAINTY CALCULATION STRUCTURES
# ============================================================================

class UncertaintyFactors(BaseModel):
    """Factors affecting trajectory uncertainty."""
    observation_arc_days: float = Field(..., description="Length of observation arc")
    time_since_discovery: float = Field(..., description="Days since discovery")
    distance_from_earth: float = Field(..., description="Distance from Earth (AU)")
    relative_velocity: float = Field(..., description="Relative velocity (km/s)")


class UncertaintyEnvelope(BaseModel):
    """Uncertainty envelope around trajectory."""
    sigma_position: float = Field(..., description="Position uncertainty (km)")
    sigma_velocity: float = Field(..., description="Velocity uncertainty (km/s)")
    correlation_factor: float = Field(..., description="Position-velocity correlation")


# ============================================================================
# 4. API ENDPOINT SCHEMAS
# ============================================================================

# GET /api/objects - List available interstellar objects
class ObjectInfo(BaseModel):
    name: str = Field(..., description="Object designation")
    discovery_date: str = Field(..., description="Discovery date")
    available_data_range: Dict[str, str] = Field(..., description="Start/end dates of available data")
    object_type: str = Field(..., description="Type: asteroid, comet, unknown")


class ObjectListResponse(BaseModel):
    objects: List[ObjectInfo]
    total_count: int


# GET /api/trajectory/{object_name}?start_jd={jd}&end_jd={jd}&step_days={days}
# Returns: TrajectoryResponse

# POST /simulate/
# Input: MissionParameters
# Returns: MissionResults


# ============================================================================
# 5. EXAMPLE API RESPONSES
# ============================================================================

EXAMPLE_TRAJECTORY_RESPONSE = {
    "object_name": "2I/Borisov",
    "trajectory_data": [
        {"jd": 2458750.5, "x": 4.56e8, "y": 1.23e9, "z": 5.21e7},
        {"jd": 2458751.5, "x": 4.55e8, "y": 1.22e9, "z": 5.20e7},
        # ... hundreds more points
    ],
    "start_date": "2019-10-01T00:00:00Z",
    "end_date": "2020-12-31T00:00:00Z", 
    "total_points": 457,
    "uncertainty_level": 0.15
}

EXAMPLE_MISSION_RESULTS = {
    "status": "success",
    "delta_v": 12.34,
    "flight_time_days": 245.6,
    "fuel_consumed": 0.73,
    "success_probability": 0.87,
    "data_captured": [
        "124 High-Resolution Images",
        "Spectral Analysis Complete",
        "Magnetic Field Data Recorded",
        "Trajectory Refinement Data Collected"
    ],
    "intercept_trajectory": [
        {"x": 1.23e8, "y": 9.87e7, "z": 0.0, "t": 0.0},
        {"x": 2.34e8, "y": 8.76e7, "z": 1.01e6, "t": 50.5},
        # ... points from Earth to intercept
    ],
    "launch_window": {
        "start": "2024-03-15T00:00:00Z",
        "end": "2024-04-01T00:00:00Z"
    },
    "uncertainty_penalty": 0.08
}


# ============================================================================
# 6. IMPLEMENTATION GUIDANCE FOR BACKEND DEVELOPERS
# ============================================================================

"""
BACKEND IMPLEMENTATION CHECKLIST:
=================================

1. Trajectory Generation (/api/trajectory/{object_name}):
   ✅ Query NASA Horizons using astroquery for multiple Julian Dates
   ✅ Generate 200-500 points covering the object's observable period
   ✅ Convert coordinates to heliocentric ecliptic frame
   ✅ Calculate uncertainty level based on observation arc
   ✅ Return TrajectoryResponse structure

2. Mission Simulation (/simulate/):
   ✅ Parse MissionParameters from frontend
   ✅ Solve Lambert's Problem using poliastro
   ✅ Calculate delta-V requirements
   ✅ Generate intercept_trajectory points (20-50 points)
   ✅ Compute uncertainty penalty
   ✅ Return MissionResults structure

3. Uncertainty Modeling:
   ✅ Implement calculate_uncertainty_penalty()
   ✅ Factor in time since discovery
   ✅ Consider observation arc length
   ✅ Apply penalty to success probability

4. Data Validation:
   ✅ Use Pydantic models for request/response validation
   ✅ Validate coordinate ranges and physical constraints
   ✅ Handle edge cases (object not found, dates out of range)

FRONTEND INTEGRATION:
====================

The frontend expects these exact API endpoints:
- GET /api/objects
- GET /api/trajectory/2I/Borisov?start_jd=2458750&end_jd=2459000&step_days=1
- POST /simulate/

Response structures must match the Pydantic models above.
"""


# ============================================================================
# 7. UNCERTAINTY PENALTY CALCULATION EXAMPLE
# ============================================================================

def calculate_uncertainty_penalty(
    chosen_point: Dict[str, float],
    most_likely_point: Dict[str, float], 
    time_to_intercept_days: float,
    observation_arc_days: float
) -> float:
    """
    Example implementation of uncertainty penalty calculation.
    
    This is the "realism factor" that makes the simulation scientifically credible.
    """
    import math
    
    # Calculate spatial distance between chosen and most likely points
    dx = chosen_point['x'] - most_likely_point['x']
    dy = chosen_point['y'] - most_likely_point['y'] 
    dz = chosen_point['z'] - most_likely_point['z']
    distance_km = math.sqrt(dx**2 + dy**2 + dz**2)
    
    # Convert to more meaningful units (Earth radii)
    distance_earth_radii = distance_km / 6371.0
    
    # Penalty factors
    distance_penalty = min(0.3, distance_earth_radii / 100.0)  # Max 30% penalty
    time_penalty = min(0.2, time_to_intercept_days / 1000.0)   # Longer intercepts harder
    observation_penalty = max(0, (180 - observation_arc_days) / 180.0 * 0.15)  # Short arcs harder
    
    total_penalty = distance_penalty + time_penalty + observation_penalty
    return min(0.5, total_penalty)  # Cap at 50% penalty


# Example usage in FastAPI:
"""
@app.post("/simulate/", response_model=MissionResults)
async def simulate_mission(params: MissionParameters):
    # 1. Get ISO trajectory at target time
    iso_state = get_interstellar_ephemeris(
        target_name="2I/Borisov",
        jd=iso_string_to_jd(params.target_epoch)
    )
    
    # 2. Solve Lambert's problem
    delta_v, trajectory_points = solve_lambert_intercept(
        params.target_position, 
        iso_state,
        params.propulsion_type
    )
    
    # 3. Calculate uncertainty penalty
    uncertainty_penalty = calculate_uncertainty_penalty(
        params.target_position,
        iso_state,
        time_to_intercept=calculate_time_to_intercept(params),
        observation_arc_days=get_observation_arc("2I/Borisov")
    )
    
    # 4. Determine success probability
    base_probability = 0.95 if params.propulsion_type == "advanced" else 0.85
    success_prob = base_probability - uncertainty_penalty
    
    # 5. Return results
    return MissionResults(
        status="success" if success_prob > 0.7 else "failure",
        delta_v=delta_v,
        success_probability=success_prob,
        intercept_trajectory=trajectory_points,
        uncertainty_penalty=uncertainty_penalty,
        # ... other fields
    )
"""
