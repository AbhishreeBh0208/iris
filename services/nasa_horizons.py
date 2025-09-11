"""NASA JPL Horizons service for real trajectory data."""
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from astroquery.jplhorizons import Horizons
import logging

logger = logging.getLogger(__name__)

class NASAHorizonsService:
    """Service for fetching real trajectory data from NASA JPL Horizons."""
    
    def __init__(self):
        self.cache = {}  # Simple cache for repeated queries
        
    def fetch_trajectory(
        self, 
        object_id: str, 
        start_date: datetime, 
        end_date: datetime, 
        step_size: str = "1d",
        observer_location: str = "500@10"  # Geocenter
    ) -> List[Dict[str, Any]]:
        """
        Fetch real trajectory data from NASA JPL Horizons.
        
        Args:
            object_id: NASA/JPL object identifier
            start_date: Start date for ephemeris
            end_date: End date for ephemeris
            step_size: Time step (e.g., '1d', '1h', '6h')
            observer_location: Observer location code
            
        Returns:
            List of trajectory points with position, velocity, and time data
        """
        try:
            # Create cache key
            cache_key = f"{object_id}_{start_date.isoformat()}_{end_date.isoformat()}_{step_size}"
            
            if cache_key in self.cache:
                logger.info(f"Returning cached data for {object_id}")
                return self.cache[cache_key]
            
            logger.info(f"Fetching trajectory for {object_id} from {start_date} to {end_date}")
            
            # Query JPL Horizons
            obj = Horizons(
                id=object_id,
                location=observer_location,
                epochs={
                    'start': start_date.strftime('%Y-%m-%d'),
                    'stop': end_date.strftime('%Y-%m-%d'),
                    'step': step_size
                }
            )
            
            # Get state vectors (position and velocity)
            vectors = obj.vectors(refplane='ecliptic')
            
            # Convert to our format
            trajectory_points = []
            for row in vectors:
                # Parse the datetime string
                dt_str = str(row['datetime_str'])
                try:
                    dt = datetime.strptime(dt_str, '%Y-%b-%d %H:%M')
                except:
                    # Try alternative format
                    try:
                        dt = datetime.strptime(dt_str.split()[0], '%Y-%b-%d')
                    except:
                        dt = datetime.now()  # Fallback
                
                point = {
                    'datetime': dt,
                    'x': float(row['x']),  # AU
                    'y': float(row['y']),  # AU  
                    'z': float(row['z']),  # AU
                    'vx': float(row['vx']),  # AU/day
                    'vy': float(row['vy']),  # AU/day
                    'vz': float(row['vz']),  # AU/day
                    'distance': float(row['range']),  # AU from observer
                    'range_rate': float(row['range_rate']),  # AU/day
                    'lighttime': float(row['lighttime']),  # Light time
                    'source': 'nasa_horizons'
                }
                trajectory_points.append(point)
            
            # Cache the result
            self.cache[cache_key] = trajectory_points
            
            logger.info(f"Successfully fetched {len(trajectory_points)} trajectory points for {object_id}")
            return trajectory_points
            
        except Exception as e:
            logger.error(f"Failed to fetch trajectory from NASA Horizons for {object_id}: {str(e)}")
            raise Exception(f"NASA Horizons query failed: {str(e)}")
    
    def get_object_info(self, object_id: str) -> Dict[str, Any]:
        """
        Get basic information about an object from NASA Horizons.
        
        Args:
            object_id: NASA/JPL object identifier
            
        Returns:
            Dictionary with object information
        """
        try:
            obj = Horizons(id=object_id, location='500@10')
            
            # Try to get some basic info - set epochs first
            obj.epochs = {'start': '2023-01-01', 'stop': '2023-01-02', 'step': '1d'}
            ephemeris = obj.ephemerides()
            
            if len(ephemeris) > 0:
                row = ephemeris[0]
                return {
                    'id': object_id,
                    'name': str(row.get('targetname', object_id)),
                    'type': 'unknown',  # JPL doesn't always provide type
                    'available': True
                }
            else:
                return {
                    'id': object_id,
                    'name': object_id,
                    'type': 'unknown',
                    'available': False
                }
                
        except Exception as e:
            logger.error(f"Failed to get object info for {object_id}: {str(e)}")
            return {
                'id': object_id,
                'name': object_id,
                'type': 'unknown',
                'available': False,
                'error': str(e)
            }
    
    def search_objects(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for objects in NASA Horizons.
        Note: This is limited - JPL Horizons doesn't have a great search API
        
        Args:
            query: Search query
            
        Returns:
            List of matching objects
        """
        # This is a basic implementation - JPL Horizons search is limited
        common_objects = {
            'borisov': '2I/Borisov',
            'oumuamua': '1I/Oumuamua',
            'halley': '1P/Halley',
            'encke': '2P/Encke',
            'ceres': '1',
            'pallas': '2',
            'juno': '3',
            'vesta': '4'
        }
        
        results = []
        query_lower = query.lower()
        
        for key, obj_id in common_objects.items():
            if query_lower in key or query_lower in obj_id.lower():
                info = self.get_object_info(obj_id)
                if info['available']:
                    results.append(info)
        
        return results
    
    def validate_object_id(self, object_id: str) -> bool:
        """
        Validate if an object ID exists in NASA Horizons.
        
        Args:
            object_id: Object identifier to validate
            
        Returns:
            True if object exists and is queryable
        """
        info = self.get_object_info(object_id)
        return info['available']

# Global instance
nasa_horizons_service = NASAHorizonsService()
