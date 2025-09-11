# Interstellar Intercept Mission Simulator Backend v2.0.0

## Real Data Integration - NO DEMO DATA

This backend now integrates with multiple real astronomical data sources and serves **only real data**. All demo/sample data has been removed.

## Data Sources

### 1. NASA JPL Horizons
- **Service**: `services/nasa_horizons.py`
- **API**: Uses `astroquery.jplhorizons.Horizons`
- **Provides**: Real ephemeris data for solar system objects
- **Format**: Position/velocity vectors in heliocentric coordinates
- **Objects**: Planets, asteroids, comets, spacecraft

### 2. Minor Planet Center (MPC)
- **Service**: `services/minor_planet_center.py`
- **API**: MPC web services
- **Provides**: Orbital elements for asteroids and comets
- **Format**: Classical orbital elements (a, e, i, Ω, ω, M)
- **Fallback**: When NASA Horizons is unavailable

### 3. Space-Track.org
- **Service**: `services/space_track.py`
- **API**: Space-Track.org REST API
- **Provides**: TLE data for satellites
- **Format**: Two-Line Element sets and orbital parameters
- **Requires**: Credentials (SPACETRACK_USERNAME, SPACETRACK_PASSWORD)

### 4. Orbit Propagation
- **Service**: `services/orbit_propagator.py`
- **Libraries**: `poliastro`, `astropy`, fallback Keplerian mechanics
- **Provides**: Trajectory propagation from orbital elements
- **Capabilities**: Mission simulation, intercept calculations

## API Endpoints

### GET `/api/trajectory/{object_name}`
- **Real Data Only**: Fetches actual trajectory from NASA, MPC, or Space-Track
- **Multi-source Fallback**: Tries NASA Horizons → MPC+propagation → Space-Track
- **Parameters**:
  - `start_date`: YYYY-MM-DD format
  - `end_date`: YYYY-MM-DD format  
  - `step_size`: Time step (1d, 6h, 1h)
- **Response**: Real trajectory points with source information

### GET `/api/search`
- **Query**: Search across NASA, MPC, Space-Track databases
- **Parameters**:
  - `query`: Object name or identifier
  - `object_types`: asteroid,comet,satellite,all
- **Response**: List of real objects from multiple sources

### POST `/api/simulate`
- **Mission Planning**: Uses real trajectory data for intercept calculations
- **Parameters**: Target object, intercept date, mission parameters
- **Response**: Real orbital mechanics calculations

### GET `/api/status`
- **Health Check**: Shows status of all data sources
- **Info**: API version, available features, no demo data confirmation

## Examples

### Real Asteroid Data (Ceres)
```bash
curl "http://localhost:8000/api/trajectory/Ceres?start_date=2024-01-01&end_date=2024-01-31&step_size=7d"
```

### Real Comet Data (Halley)
```bash
curl "http://localhost:8000/api/trajectory/1P/Halley?start_date=2024-01-01&end_date=2025-01-01&step_size=30d"
```

### Search Real Objects
```bash
curl "http://localhost:8000/api/search?query=asteroid&object_types=asteroid"
```

### Mission Simulation with Real Data
```bash
curl -X POST "http://localhost:8000/api/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "target_object": "Ceres",
    "intercept_date": "2024-06-01T00:00:00Z",
    "swarm_size": 5,
    "propulsion_type": "ion"
  }'
```

## Data Flow

1. **Primary**: NASA JPL Horizons (most reliable)
2. **Fallback 1**: Minor Planet Center → Orbit Propagation
3. **Fallback 2**: Space-Track.org (for satellites)
4. **No Fallback**: No demo/sample data served

## Configuration

### Environment Variables
```bash
# Optional: For Space-Track.org satellite data
SPACETRACK_USERNAME=your_username
SPACETRACK_PASSWORD=your_password
```

### Dependencies
- `astroquery` - NASA JPL Horizons
- `requests` - Web API access
- `numpy` - Numerical calculations
- `poliastro` - Advanced orbital mechanics (optional)
- `fastapi` - Web API framework

## Changes from v1.0.0

### ✅ Added
- Multi-source data integration
- Real NASA JPL Horizons data
- Minor Planet Center integration
- Space-Track.org satellite data
- Advanced orbit propagation
- Mission simulation with real trajectories
- Comprehensive search across databases


### 🔄 Updated
- API responses include data source information
- Error handling shows which sources were tried
- Trajectory format standardized across sources
- Mission simulation uses real orbital mechanics

## Status

**✅ REAL DATA ONLY - NO DEMO DATA**

The backend now serves exclusively real astronomical data from authoritative sources. All demo data has been removed to ensure mission-critical accuracy.
