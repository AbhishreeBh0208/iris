#!/usr/bin/env python3
"""
DEMONSTRATION: Real NASA JPL Horizons Data Fetching
==================================================

This script shows exactly how the system fetches REAL trajectory data
from NASA JPL Horizons (not sample data).
"""

from astroquery.jplhorizons import Horizons
import json
import numpy as np
from datetime import datetime

def fetch_real_nasa_data():
    """Fetch real 2I/Borisov trajectory data from NASA JPL Horizons"""
    
    print("🛰️ FETCHING REAL NASA DATA (Not Sample Data)")
    print("=" * 50)
    
    try:
        # Create NASA Horizons query for 2I/Borisov
        print("📡 Connecting to NASA JPL Horizons database...")
        obj = Horizons(
            id='2I',                    # 2I/Borisov interstellar comet
            location='500@10',          # Heliocentric coordinates (Sun center)
            epochs={
                'start': '2019-01-01',  # Start date
                'stop': '2020-06-30',   # End date  
                'step': '7d'            # Weekly data points
            }
        )
        
        # Get state vectors (position and velocity)
        print("🔍 Querying NASA database for 2I/Borisov ephemeris...")
        vectors = obj.vectors(
            refplane='ecliptic',        # Ecliptic reference frame
            aberrations='none',         # No corrections
            delta_T=False              # Standard time
        )
        
        print(f"✅ SUCCESS: Fetched {len(vectors)} real data points from NASA!")
        print()
        
        # Process and display real NASA data
        trajectory_points = []
        print("📊 REAL NASA TRAJECTORY DATA:")
        print("-" * 40)
        
        for i, row in enumerate(vectors[:5]):  # Show first 5 points
            # Convert AU to kilometers
            x_km = row['x'] * 149597870.7
            y_km = row['y'] * 149597870.7  
            z_km = row['z'] * 149597870.7
            
            # Calculate distance from Sun
            distance_km = np.sqrt(x_km**2 + y_km**2 + z_km**2)
            distance_au = distance_km / 149597870.7
            
            # Store trajectory point
            trajectory_points.append({
                'jd': float(row['datetime_jd']),
                'x': float(x_km),
                'y': float(y_km), 
                'z': float(z_km)
            })
            
            print(f"Point {i+1}: JD {row['datetime_jd']:.2f}")
            print(f"  Position: ({x_km:.0f}, {y_km:.0f}, {z_km:.0f}) km")
            print(f"  Distance: {distance_au:.3f} AU ({distance_km/1e6:.1f} million km)")
            print()
        
        # Summary statistics
        distances_au = []
        for row in vectors:
            x, y, z = row['x'], row['y'], row['z']
            dist_au = np.sqrt(x**2 + y**2 + z**2)
            distances_au.append(dist_au)
        
        print("🎯 DATASET SUMMARY:")
        print(f"• Total data points: {len(vectors)}")
        print(f"• Date range: JD {vectors[0]['datetime_jd']:.1f} to {vectors[-1]['datetime_jd']:.1f}")
        print(f"• Distance range: {min(distances_au):.3f} to {max(distances_au):.3f} AU")
        print(f"• Object: 2I/Borisov (Interstellar Comet)")
        print(f"• Data source: NASA JPL Horizons System")
        
        # Save to file for frontend
        output_data = {
            'object_name': '2I/Borisov',
            'start_date': '2019-01-01',
            'end_date': '2020-06-30',
            'total_points': len(trajectory_points),
            'trajectory_data': trajectory_points
        }
        
        with open('real_nasa_data.json', 'w') as f:
            json.dump(output_data, f, indent=2)
            
        print(f"\n💾 Real NASA data saved to: real_nasa_data.json")
        print("🚀 This data can be used directly in the frontend!")
        
        return trajectory_points
        
    except Exception as e:
        print(f"❌ ERROR fetching real NASA data: {e}")
        print("\nThis could be due to:")
        print("• Internet connection issues")
        print("• NASA servers temporarily unavailable") 
        print("• astroquery installation problems")
        return None

if __name__ == "__main__":
    print("REAL NASA DATA FETCHING DEMONSTRATION")
    print("====================================")
    print()
    print("This script demonstrates fetching ACTUAL trajectory data")
    print("from NASA JPL Horizons (not sample/mock data).")
    print()
    
    # Fetch real data
    real_data = fetch_real_nasa_data()
    
    if real_data:
        print("\n✅ SUCCESS: Real NASA data fetched and processed!")
        print("This is the same data your frontend will receive.")
    else:
        print("\n⚠️  Could not fetch real NASA data.")
        print("Check your internet connection and try again.")
        
    print("\n" + "="*50)
    print("Frontend Integration:")
    print("The real_nasa_data.json file contains actual NASA trajectory data")
    print("that can be loaded directly into your Cesium 3D visualization!")
