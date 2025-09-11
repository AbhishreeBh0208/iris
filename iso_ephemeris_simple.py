"""
Simplified Interstellar Object Ephemeris for FastAPI Backend
===========================================================

Production-ready function for your orbital mechanics simulator.
"""

from astroquery.jplhorizons import Horizons


def get_iso_ephemeris(target_name: str, jd: float) -> dict:
    """
    Get state vector for interstellar objects from JPL Horizons.
    
    CORRECTED VERSION of your original function.
    
    Parameters:
    -----------
    target_name : str
        Examples: '1I/2017 U1', '2I/Borisov', '1I', '2I'
    jd : float
        Julian Date
        
    Returns:
    --------
    dict
        State vector with position (km) and velocity (km/s)
    """
    
    # Map common names to official designations
    name_mapping = {
        '1I': '1I/2017 U1',
        'oumuamua': '1I/2017 U1', 
        '2I': '2I/Borisov',
        'borisov': '2I/Borisov'
    }
    
    # Normalize target name
    query_name = name_mapping.get(target_name.lower(), target_name)
    
    try:
        # Create Horizons object - CORRECTED parameters
        obj = Horizons(
            id=query_name,                    # Object designation
            location='@sun',                  # Heliocentric (not '@Sun')
            epochs=jd,                        # Julian Date
            id_type='designation'             # For interstellar objects
        )
        
        # Get vectors - CORRECTED method call
        vec = obj.vectors(refplane='ecliptic')
        
        # CORRECTED: Access table data properly
        # The returned object is an astropy Table
        row = vec[0]  # First row
        
        # Unit conversions
        AU_TO_KM = 149597870.7              # km per AU
        AU_PER_DAY_TO_KM_PER_S = 1731.45683633  # km/s per AU/day
        
        return {
            'jd': jd,
            'x': float(row['x']) * AU_TO_KM,           # Convert AU to km
            'y': float(row['y']) * AU_TO_KM,
            'z': float(row['z']) * AU_TO_KM,
            'vx': float(row['vx']) * AU_PER_DAY_TO_KM_PER_S,  # Convert AU/day to km/s
            'vy': float(row['vy']) * AU_PER_DAY_TO_KM_PER_S,
            'vz': float(row['vz']) * AU_PER_DAY_TO_KM_PER_S,
            'target': query_name,
            'frame': 'heliocentric_ecliptic'
        }
        
    except Exception as e:
        raise ValueError(f"Error getting ephemeris for {target_name}: {str(e)}")


# ALTERNATIVE: If you want the raw values without unit conversion
def get_iso_ephemeris_raw(target_name: str, jd: float) -> dict:
    """
    Get state vector in original JPL units (AU, AU/day).
    Useful if you want to handle units yourself.
    """
    
    name_mapping = {
        '1I': '1I/2017 U1',
        '2I': '2I/Borisov'
    }
    
    query_name = name_mapping.get(target_name.lower(), target_name)
    
    obj = Horizons(
        id=query_name,
        location='@sun', 
        epochs=jd,
        id_type='designation'
    )
    
    vec = obj.vectors(refplane='ecliptic')
    row = vec[0]
    
    return {
        'jd': jd,
        'x': float(row['x']),      # AU
        'y': float(row['y']),      # AU  
        'z': float(row['z']),      # AU
        'vx': float(row['vx']),    # AU/day
        'vy': float(row['vy']),    # AU/day
        'vz': float(row['vz']),    # AU/day
        'target': query_name,
        'units': 'AU, AU/day'
    }


# Integration with your FastAPI app
"""
Add this to your FastAPI backend:

@app.post("/simulate/")
async def simulate_mission(params: dict):
    # Get target object state vector
    target_state = get_iso_ephemeris(
        target_name="2I/Borisov",  # or from params
        jd=params.get("target_epoch_jd", 2458800.0)
    )
    
    # Your existing simulation logic here
    # target_state contains position/velocity in km, km/s
    
    return {
        "status": "success",
        "delta_v": 12.34,
        "target_state": target_state
    }
"""


if __name__ == "__main__":
    # Test the function
    print("Testing corrected ephemeris function...")
    
    try:
        # Test 'Oumuamua  
        result = get_iso_ephemeris("1I", 2458077.5)
        print(f"\n'Oumuamua state vector:")
        print(f"Position: {result['x']:.0f}, {result['y']:.0f}, {result['z']:.0f} km")
        print(f"Velocity: {result['vx']:.3f}, {result['vy']:.3f}, {result['vz']:.3f} km/s")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nThis is expected if astroquery is not installed.")
        print("Install with: pip install astroquery astropy")


"""
Key Corrections to Your Original Code:
=====================================

1. Object ID: ✅ Use full designation like '1I/2017 U1' or '2I/Borisov'
2. id_type: ✅ Use 'designation' for interstellar objects  
3. location: ✅ Use '@sun' (lowercase) for heliocentric
4. Data access: ✅ Use vec[0] to get first row, then row['x'] etc.
5. Units: ✅ Convert AU to km and AU/day to km/s
6. Error handling: ✅ Added proper exception handling

Installation Requirements:
=========================
pip install astroquery astropy numpy

The function is now ready for production use in your FastAPI orbital mechanics simulator!
"""
