#!/usr/bin/env python3
"""
FastAPI backend for Interstellar Intercept Mission Simulator.
Multi-source astronomical data API with NO DEMO/SAMPLE DATA.
Only serves real data from NASA, MPC, Space-Track, and orbit propagation.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import logging
from datetime import datetime, timedelta

# Import our multi-source data coordinator
from services.data_coordinator import data_coordinator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Interstellar Intercept Mission API",
    version="2.0.0",
    description="Multi-source astronomical data API with NO demo data - only real data from NASA, MPC, Space-Track"
)

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
    sources_used: List[str]
    sources_tried: List[str]
    success: bool
    errors: Optional[Dict[str, str]] = None

class ObjectInfo(BaseModel):
    id: str
    name: str
    type: str
    source: str
    available: bool
    details: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    query: str
    results: List[ObjectInfo]
    total_found: int

class MissionParameters(BaseModel):
    target_object: str
    intercept_date: str  # ISO 8601 date
    swarm_size: int = 5
    role_split: str = 'balanced'  # 'balanced', 'science-heavy', 'comms-heavy'
    propulsion_type: str = 'ion'  # 'chemical', 'ion', 'nuclear'
    interceptor_elements: Optional[Dict[str, float]] = None

class MissionResult(BaseModel):
    success: bool
    target_object: str
    intercept_date: str
    data_sources: List[str]
    intercept_time: Optional[str] = None
    target_position: Optional[Dict[str, float]] = None
    interceptor_position: Optional[Dict[str, float]] = None
    miss_distance_au: Optional[float] = None
    miss_distance_km: Optional[float] = None
    relative_velocity_km_per_s: Optional[float] = None
    feasible: Optional[bool] = None
    interceptor_trajectory: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Interstellar Intercept Mission API v2.0.0 - Real Data Only",
        "features": [
            "NASA JPL Horizons integration",
            "Minor Planet Center (MPC) data",
            "Space-Track.org satellite data",
            "Orbit propagation and mission simulation",
            "NO demo/sample data"
        ],
        "status": "operational"
    }

@app.get("/api/search")
async def search_objects(
    query: str = Query(..., description="Search query for astronomical objects"),
    object_types: str = Query("all", description="Comma-separated object types (asteroid,comet,satellite,all)")
) -> SearchResponse:
    """
    Search for astronomical objects across all data sources.
    Returns only real objects from NASA, MPC, Space-Track.
    """
    try:
        logger.info(f"Searching for objects: '{query}' with types: {object_types}")
        
        # Parse object types
        types_list = [t.strip() for t in object_types.split(',')]
        
        # Search using data coordinator
        results = data_coordinator.search_objects(query, types_list)
        
        # Convert to response format
        object_infos = []
        for obj in results:
            object_infos.append(ObjectInfo(
                id=obj['id'],
                name=obj.get('name', obj['id']),
                type=obj.get('type', 'unknown'),
                source=obj.get('source', 'unknown'),
                available=obj.get('available', True),
                details=obj.get('details')
            ))
        
        logger.info(f"Found {len(object_infos)} objects for query '{query}'")
        
        return SearchResponse(
            query=query,
            results=object_infos,
            total_found=len(object_infos)
        )
        
    except Exception as e:
        logger.error(f"Search failed for '{query}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/trajectory/{object_name}", response_model=TrajectoryResponse)
async def get_trajectory(
    object_name: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    step_size: str = Query("1d", description="Time step (1d, 6h, 1h)")
):
    """
    Fetch real trajectory data for an astronomical object.
    NO DEMO DATA - Uses NASA Horizons, MPC orbital elements, or Space-Track TLEs.
    """
    try:
        logger.info(f"Fetching trajectory for {object_name}")
        
        # Set default date range if not provided
        if not start_date:
            start_dt = datetime.now() - timedelta(days=365)
            start_date = start_dt.strftime('%Y-%m-%d')
        else:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            
        if not end_date:
            end_dt = datetime.now() + timedelta(days=365)
            end_date = end_dt.strftime('%Y-%m-%d')
        else:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        logger.info(f"Date range: {start_date} to {end_date}")
        
        # Get trajectory using data coordinator
        result = data_coordinator.get_object_trajectory(
            object_name, start_dt, end_dt, step_size
        )
        
        if not result['success']:
            logger.error(f"All data sources failed for {object_name}")
            raise HTTPException(
                status_code=404,
                detail={
                    "message": f"Could not retrieve trajectory data for {object_name}",
                    "sources_tried": result.get('sources_tried', []),
                    "errors": result.get('errors', {})
                }
            )
        
        # Convert trajectory points to response format
        trajectory_points = []
        for point in result['trajectory']:
            # Convert datetime to Julian Date
            dt = point['datetime']
            jd = (dt - datetime(1858, 11, 17)).total_seconds() / 86400.0 + 2400000.5
            
            # Convert AU to km
            AU_TO_KM = 149597870.7
            trajectory_points.append(TrajectoryPoint(
                jd=jd,
                x=point['x'] * AU_TO_KM,
                y=point['y'] * AU_TO_KM,
                z=point['z'] * AU_TO_KM
            ))
        
        logger.info(f"✅ Retrieved {len(trajectory_points)} real data points for {object_name} from {result['sources_used']}")
        
        return TrajectoryResponse(
            object_name=object_name,
            start_date=start_date,
            end_date=end_date,
            trajectory_data=trajectory_points,
            total_points=len(trajectory_points),
            sources_used=result['sources_used'],
            sources_tried=result['sources_tried'],
            success=True
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Trajectory fetch failed for {object_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trajectory: {str(e)}")

@app.get("/api/object/{object_id}")
async def get_object_info(object_id: str):
    """
    Get comprehensive information about an astronomical object from all sources.
    """
    try:
        logger.info(f"Getting info for object {object_id}")
        
        info = data_coordinator.get_object_info(object_id)
        
        if not info['available']:
            raise HTTPException(
                status_code=404,
                detail=f"Object {object_id} not found in any data source"
            )
        
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get object info for {object_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get object info: {str(e)}")

@app.post("/api/simulate", response_model=MissionResult)
async def simulate_mission(mission: MissionParameters):
    """
    Simulate an interstellar intercept mission using REAL trajectory data.
    NO DEMO DATA - Uses actual orbital mechanics and real object trajectories.
    """
    try:
        logger.info(f"Simulating intercept mission for {mission.target_object}")
        
        # Parse intercept date
        intercept_date = datetime.fromisoformat(mission.intercept_date.replace('Z', '+00:00'))
        
        # Default mission parameters
        mission_params = {
            'swarm_size': mission.swarm_size,
            'role_split': mission.role_split,
            'propulsion_type': mission.propulsion_type,
        }
        
        # Set interceptor orbital elements if provided
        if mission.interceptor_elements:
            mission_params['interceptor_elements'] = mission.interceptor_elements
        
        # Run simulation using data coordinator
        result = data_coordinator.simulate_intercept_mission(
            mission.target_object,
            intercept_date,
            mission_params
        )
        
        if not result['success']:
            logger.error(f"Mission simulation failed: {result.get('error', 'Unknown error')}")
            return MissionResult(
                success=False,
                target_object=mission.target_object,
                intercept_date=mission.intercept_date,
                data_sources=[],
                error=result.get('error', 'Mission simulation failed')
            )
        
        # Format response
        mission_result = MissionResult(
            success=result['success'],
            target_object=mission.target_object,
            intercept_date=mission.intercept_date,
            data_sources=result.get('data_sources', []),
            intercept_time=result.get('intercept_time', {}).get('isoformat', '') if result.get('intercept_time') else None,
            target_position=result.get('target_position'),
            interceptor_position=result.get('interceptor_position'),
            miss_distance_au=result.get('miss_distance_au'),
            miss_distance_km=result.get('miss_distance_km'),
            relative_velocity_km_per_s=result.get('relative_velocity_km_per_s'),
            feasible=result.get('feasible'),
            interceptor_trajectory=result.get('interceptor_trajectory', [])[:50]  # Limit size
        )
        
        logger.info(f"✅ Mission simulation completed - Feasible: {result.get('feasible', False)}")
        return mission_result
        
    except Exception as e:
        logger.error(f"Mission simulation failed: {str(e)}")
        return MissionResult(
            success=False,
            target_object=mission.target_object,
            intercept_date=mission.intercept_date,
            data_sources=[],
            error=str(e)
        )

@app.get("/api/status")
async def get_status():
    """
    Get status of all data sources and services.
    """
    status = {
        "api_version": "2.0.0",
        "data_sources": {
            "nasa_horizons": {"available": True, "description": "NASA JPL Horizons ephemeris service"},
            "minor_planet_center": {"available": True, "description": "MPC orbital elements and discoveries"},
            "space_track": {"available": True, "description": "Space-Track.org satellite catalog"},
            "orbit_propagator": {"available": True, "description": "Orbital mechanics and propagation"}
        },
        "features": {
            "real_data_only": True,
            "demo_data": False,
            "multi_source_fallback": True,
            "mission_simulation": True,
            "object_search": True
        },
        "uptime": "operational"
    }
    
    return status

if __name__ == "__main__":
    logger.info("🚀 Starting Interstellar Intercept Mission API v2.0.0")
    logger.info("📡 Real data sources enabled - NO demo data")
    
    uvicorn.run(
        "backend_api_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
