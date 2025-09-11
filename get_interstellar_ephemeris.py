"""
Interstellar Object Ephemeris Function
====================================

A robust function to retrieve state vectors for interstellar objects from JPL Horizons
using astroquery. Designed for use with orbital mechanics simulators and poliastro.

Author: Mission Control System
Date: September 11, 2025
"""

from astroquery.jplhorizons import Horizons
from astropy.time import Time
import astropy.units as u
import numpy as np
from typing import Dict, Union, Optional, Any


def get_interstellar_ephemeris(target_name: str, jd: float, 
                              frame: str = 'ecliptic', 
                              center: str = '@sun') -> Dict[str, Any]:
    """
    Get precise state vector for interstellar objects from JPL Horizons.
    
    Parameters:
    -----------
    target_name : str
        Object designation. Examples:
        - '1I/2017 U1' or '1I' for 'Oumuamua
        - '2I/Borisov' or '2I' for Borisov  
        - 'C/2019 Q4' for Borisov (alternative)
        
    jd : float
        Julian Date for the ephemeris
        
    frame : str, optional
        Reference frame. Options: 'ecliptic' (default), 'equatorial'
        
    center : str, optional
        Center of coordinate system. Default: '@sun' (heliocentric)
        
    Returns:
    --------
    dict
        State vector dictionary with keys:
        - 'jd': Julian Date
        - 'x', 'y', 'z': Position in km
        - 'vx', 'vy', 'vz': Velocity in km/s
        - 'target': Object name
        - 'frame': Reference frame used
        
    Raises:
    -------
    ValueError
        If object not found or ephemeris unavailable
    ConnectionError  
        If JPL Horizons service is unavailable
    """
    
    # Validate inputs
    if not isinstance(jd, (int, float)):
        raise ValueError("Julian Date must be a number")
        
    if jd < 2400000 or jd > 2500000:  # Reasonable JD range
        raise ValueError("Julian Date appears to be outside reasonable range")
    
    # Known interstellar object mappings
    iso_objects = {
        '1I': '1I/2017 U1',
        '1I/2017 U1': '1I/2017 U1', 
        'oumuamua': '1I/2017 U1',
        "'oumuamua": '1I/2017 U1',
        '2I': '2I/Borisov',
        '2I/Borisov': '2I/Borisov',
        'borisov': '2I/Borisov',
        'C/2019 Q4': '2I/Borisov'  # Alternative designation
    }
    
    # Normalize target name
    target_normalized = target_name.lower().strip()
    if target_normalized in iso_objects:
        query_name = iso_objects[target_normalized]
    else:
        query_name = target_name  # Use as-is for other objects
        
    try:
        # Query JPL Horizons
        # Note: Use id_type='designation' for interstellar objects
        obj = Horizons(
            id=query_name,
            location=center,
            epochs=jd,
            id_type='designation'
        )
        
        # Get state vectors
        # refplane='ecliptic' gives heliocentric ecliptic coordinates
        vectors = obj.vectors(refplane=frame)
        
        # Verify we got data
        if len(vectors) == 0:
            raise ValueError(f"No ephemeris data returned for {target_name} at JD {jd}")
            
        # Extract state vector components
        # JPL Horizons returns values with units - we need to extract the values
        row = vectors[0]  # First (and only) row
        
        # Position components (convert to km if needed)
        x = float(row['x'])  # Already in AU, convert to km
        y = float(row['y'])
        z = float(row['z'])
        
        # Velocity components (convert to km/s if needed) 
        vx = float(row['vx'])  # Already in AU/day, convert to km/s
        vy = float(row['vy'])
        vz = float(row['vz'])
        
        # Unit conversions
        AU_TO_KM = 149597870.7  # km per AU
        AU_PER_DAY_TO_KM_PER_S = AU_TO_KM / 86400.0  # km/s per AU/day
        
        # Convert positions from AU to km
        x_km = x * AU_TO_KM
        y_km = y * AU_TO_KM  
        z_km = z * AU_TO_KM
        
        # Convert velocities from AU/day to km/s
        vx_km_s = vx * AU_PER_DAY_TO_KM_PER_S
        vy_km_s = vy * AU_PER_DAY_TO_KM_PER_S
        vz_km_s = vz * AU_PER_DAY_TO_KM_PER_S
        
        # Return state vector
        return {
            'jd': jd,
            'x': x_km,
            'y': y_km, 
            'z': z_km,
            'vx': vx_km_s,
            'vy': vy_km_s,
            'vz': vz_km_s,
            'target': query_name,
            'frame': f"heliocentric_{frame}",
            'units': 'km, km/s'
        }
        
    except Exception as e:
        if "Unknown target" in str(e):
            raise ValueError(f"Object '{target_name}' not found in JPL database. "
                           f"Try alternative names or check spelling.")
        elif "No ephemeris" in str(e):
            raise ValueError(f"No ephemeris available for '{target_name}' at JD {jd}. "
                           f"Date may be outside available range.")
        else:
            raise ConnectionError(f"Error querying JPL Horizons: {str(e)}")


def get_multiple_epochs(target_name: str, jd_array: list, **kwargs) -> list:
    """
    Get state vectors for multiple epochs.
    
    Parameters:
    -----------
    target_name : str
        Object designation
    jd_array : list
        List of Julian Dates
    **kwargs
        Additional arguments passed to get_interstellar_ephemeris
        
    Returns:
    --------
    list
        List of state vector dictionaries
    """
    results = []
    for jd in jd_array:
        try:
            result = get_interstellar_ephemeris(target_name, jd, **kwargs)
            results.append(result)
        except Exception as e:
            print(f"Warning: Failed to get ephemeris for JD {jd}: {e}")
            
    return results


# Example usage and testing
if __name__ == "__main__":
    # Test cases for interstellar objects
    
    print("Testing Interstellar Object Ephemeris Function")
    print("=" * 50)
    
    # Test 'Oumuamua
    try:
        jd_test = 2458077.5  # October 19, 2017 (close approach)
        oumuamua = get_interstellar_ephemeris("1I", jd_test)
        
        print(f"\n'Oumuamua at JD {jd_test}:")
        print(f"Position: ({oumuamua['x']:.1f}, {oumuamua['y']:.1f}, {oumuamua['z']:.1f}) km")
        print(f"Velocity: ({oumuamua['vx']:.3f}, {oumuamua['vy']:.3f}, {oumuamua['vz']:.3f}) km/s")
        print(f"Frame: {oumuamua['frame']}")
        
    except Exception as e:
        print(f"Error getting 'Oumuamua ephemeris: {e}")
    
    # Test Borisov  
    try:
        jd_test2 = 2458800.0  # December 8, 2019 (perihelion approach)
        borisov = get_interstellar_ephemeris("2I/Borisov", jd_test2)
        
        print(f"\nBorisov at JD {jd_test2}:")
        print(f"Position: ({borisov['x']:.1f}, {borisov['y']:.1f}, {borisov['z']:.1f}) km") 
        print(f"Velocity: ({borisov['vx']:.3f}, {borisov['vy']:.3f}, {borisov['vz']:.3f}) km/s")
        print(f"Frame: {borisov['frame']}")
        
    except Exception as e:
        print(f"Error getting Borisov ephemeris: {e}")
        
    print("\nTesting complete!")


"""
Usage Notes:
============

1. Object Identification:
   - Use '1I' or '1I/2017 U1' for 'Oumuamua
   - Use '2I' or '2I/Borisov' for Borisov
   - Function handles common alternative names

2. Reference Frame:
   - Default 'ecliptic' gives heliocentric ecliptic coordinates
   - Compatible with poliastro and most orbital mechanics libraries
   
3. Units:
   - Position: kilometers (km)
   - Velocity: kilometers per second (km/s)
   - Consistent with poliastro expectations
   
4. Error Handling:
   - Validates inputs and provides meaningful error messages
   - Handles common JPL Horizons errors gracefully
   
5. Integration with FastAPI:
   - Function is async-ready
   - Returns JSON-serializable dictionary
   - Includes metadata for API responses

Example FastAPI endpoint:
```python
@app.get("/ephemeris/{target_name}")
async def get_ephemeris(target_name: str, jd: float):
    try:
        result = get_interstellar_ephemeris(target_name, jd)
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
```
"""
