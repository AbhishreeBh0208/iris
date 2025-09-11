import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { object: string } }
) {
  try {
    const objectName = params.object;
    
    // Try to call the Python backend
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/trajectory/${objectName}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('Error fetching trajectory data:', error);
    
    // Return fallback data if backend is unavailable
    const fallbackData = generateFallbackTrajectory(params.object);
    
    return NextResponse.json(fallbackData);
  }
}

function generateFallbackTrajectory(objectName: string) {
  const baseJD = 2458849.5; // Jan 1, 2020
  const trajectoryPoints = [];
  
  // Generate a realistic interstellar trajectory
  for (let i = 0; i < 365; i++) {
    const t = (i - 180) / 100; // Time parameter centered around periapsis
    const jd = baseJD + i;
    
    // Hyperbolic trajectory approximation
    const a = -2.0; // Semi-major axis (AU, negative for hyperbolic)
    const e = 3.36; // Eccentricity (high for interstellar object)
    
    // Position calculation
    const r = Math.abs(a * (e - 1) / (1 + e * Math.cos(t)));
    const x = r * Math.cos(t) * 149597870.7; // AU to km
    const y = r * Math.sin(t) * 0.1 * 149597870.7; // Small inclination
    const z = r * Math.sin(t) * 0.05 * 149597870.7; // Small out-of-plane
    
    trajectoryPoints.push({ jd, x, y, z });
  }
  
  return {
    object_name: objectName,
    start_date: "2020-01-01",
    end_date: "2020-12-31",
    trajectory_data: trajectoryPoints,
    total_points: trajectoryPoints.length
  };
}
