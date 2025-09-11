import { NextRequest, NextResponse } from 'next/server';

interface MissionParameters {
  target_object: string;
  intercept_date: string;
  swarm_size: number;
  role_split: string;
  propulsion_type: string;
}

export async function POST(request: NextRequest) {
  try {
    const missionParams: MissionParameters = await request.json();
    
    // Try to call the Python backend first
    try {
      const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/simulate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(missionParams),
      });

      if (response.ok) {
        const result = await response.json();
        return NextResponse.json(result);
      }
    } catch (backendError) {
      console.log('Backend unavailable, using fallback simulation');
    }
    
    // Fallback simulation if backend is unavailable
    const result = simulateMissionFallback(missionParams);
    
    return NextResponse.json(result);
    
  } catch (error) {
    console.error('Error in mission simulation:', error);
    
    return NextResponse.json(
      { error: 'Mission simulation failed', details: (error as Error).message },
      { status: 500 }
    );
  }
}

function simulateMissionFallback(mission: MissionParameters) {
  // Parse target time
  const targetTime = new Date(mission.intercept_date);
  
  // Calculate target distance (fallback estimate)
  const targetDistanceKm = 1.5e8; // Approximate distance to asteroid in km
  
  // Base delta-V calculation (simplified orbital mechanics)
  const baseDeltaV = Math.min(15.0, targetDistanceKm / 1e8);
  
  // Propulsion efficiency factors
  const propulsionEfficiency: Record<string, number> = {
    'chemical': 1.0,
    'ion': 0.3,
    'nuclear': 0.1
  };
  
  const deltaV = baseDeltaV * (propulsionEfficiency[mission.propulsion_type] || 1.0);
  const flightTimeDays = targetDistanceKm / (50 * 86400); // Simplified
  
  // Success probability calculation
  const baseSuccess = 0.85;
  const swarmBonus = Math.min(0.1, (mission.swarm_size - 1) * 0.01);
  const deltaVPenalty = Math.max(0, (deltaV - 5.0) * 0.05);
  const successProbability = Math.max(0.1, baseSuccess + swarmBonus - deltaVPenalty);
  
  // Mission outcome
  const missionSuccess = successProbability > 0.6;
  const status = missionSuccess 
    ? "Mission successful - Target intercepted" 
    : "Mission failed - Intercept missed";
  
  // Data captured based on mission success
  const allDataTypes = [
    "High-resolution imagery",
    "Spectrographic analysis",
    "Magnetic field measurements", 
    "Dust particle samples",
    "Gas composition data",
    "Surface temperature mapping"
  ];
  
  const dataCaptured = missionSuccess 
    ? allDataTypes.slice(0, Math.min(Math.floor(mission.swarm_size / 2), allDataTypes.length))
    : [];
  
  // Generate intercept trajectory
  let interceptTrajectory = [];
  if (missionSuccess) {
    // Simple trajectory from Earth to target (fallback)
    const earthPos = [0, 0, 0];
    const targetPos = [1.2, 0.8, 0.1]; // Approximated target position in AU
    
    for (let i = 0; i < 10; i++) {
      const t = i / 9.0;
      interceptTrajectory.push({
        x: earthPos[0] + t * (targetPos[0] - earthPos[0]),
        y: earthPos[1] + t * (targetPos[1] - earthPos[1]),
        z: earthPos[2] + t * (targetPos[2] - earthPos[2])
      });
    }
  }
  
  return {
    success: missionSuccess,
    target_object: mission.target_object,
    intercept_date: mission.intercept_date,
    data_sources: ['fallback_simulation'],
    delta_v_required_km_s: Math.round(deltaV * 100) / 100,
    flight_time_days: Math.round(flightTimeDays * 10) / 10,
    fuel_consumed_percent: Math.round(deltaV * mission.swarm_size * 100 * 10) / 10,
    success_probability: Math.round(successProbability * 100) / 100,
    data_captured: dataCaptured,
    interceptor_trajectory: interceptTrajectory
  };
}
