"""Minor Planet Center (MPC) service for asteroid and comet data."""
import requests
# import pandas as pd  # Not needed for this implementation
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
import json

logger = logging.getLogger(__name__)

class MinorPlanetCenterService:
    """Service for fetching data from the Minor Planet Center."""
    
    def __init__(self):
        self.base_url = "https://www.minorplanetcenter.net/web_service"
        self.cache = {}
        
    def search_objects(self, query: str, object_type: str = "all") -> List[Dict[str, Any]]:
        """
        Search for objects in the MPC database.
        
        Args:
            query: Search query (name, designation, etc.)
            object_type: Type filter ("asteroid", "comet", "all")
            
        Returns:
            List of matching objects
        """
        try:
            # MPC web service endpoint for search
            url = f"{self.base_url}/search_objects"
            params = {
                'query': query,
                'limit': 50,
                'format': 'json'
            }
            
            if object_type != "all":
                params['type'] = object_type
            
            cache_key = f"search_{query}_{object_type}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            objects = []
            
            for obj in data.get('objects', []):
                objects.append({
                    'id': obj.get('designation', obj.get('name', 'Unknown')),
                    'name': obj.get('name', obj.get('designation', 'Unknown')),
                    'type': obj.get('object_type', 'unknown'),
                    'designation': obj.get('designation', ''),
                    'discovery_date': obj.get('discovery_date', ''),
                    'magnitude': obj.get('absolute_magnitude', None),
                    'period': obj.get('orbital_period', None),
                    'available': True,
                    'source': 'MPC'
                })
            
            self.cache[cache_key] = objects
            logger.info(f"Found {len(objects)} objects for query '{query}'")
            return objects
            
        except Exception as e:
            logger.error(f"MPC search failed for '{query}': {str(e)}")
            # Return empty list on failure rather than raising
            return []
    
    def get_orbital_elements(self, object_id: str) -> Optional[Dict[str, Any]]:
        """
        Get orbital elements for an object from MPC.
        
        Args:
            object_id: Object identifier
            
        Returns:
            Dictionary with orbital elements or None
        """
        try:
            cache_key = f"elements_{object_id}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            url = f"{self.base_url}/orbital_elements"
            params = {
                'designation': object_id,
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                elem = data[0]  # Take first result
                elements = {
                    'semi_major_axis': elem.get('a', None),  # AU
                    'eccentricity': elem.get('e', None),
                    'inclination': elem.get('i', None),  # degrees
                    'longitude_ascending_node': elem.get('Om', None),  # degrees
                    'argument_periapsis': elem.get('w', None),  # degrees
                    'mean_anomaly': elem.get('M', None),  # degrees
                    'epoch': elem.get('epoch', None),  # JD
                    'absolute_magnitude': elem.get('H', None),
                    'slope_parameter': elem.get('G', None),
                    'source': 'MPC'
                }
                
                self.cache[cache_key] = elements
                return elements
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get orbital elements for {object_id}: {str(e)}")
            return None
    
    def get_recent_discoveries(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get recently discovered objects from MPC.
        
        Args:
            days: Number of days back to search
            
        Returns:
            List of recently discovered objects  
        """
        try:
            cache_key = f"recent_{days}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            url = f"{self.base_url}/recent_discoveries"
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'format': 'json',
                'limit': 100
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            discoveries = []
            
            for obj in data.get('discoveries', []):
                discoveries.append({
                    'id': obj.get('designation', 'Unknown'),
                    'name': obj.get('name', obj.get('designation', 'Unknown')),
                    'discovery_date': obj.get('discovery_date', ''),
                    'discoverer': obj.get('discoverer', ''),
                    'magnitude': obj.get('magnitude', None),
                    'type': obj.get('object_type', 'unknown'),
                    'source': 'MPC'
                })
            
            self.cache[cache_key] = discoveries
            return discoveries
            
        except Exception as e:
            logger.error(f"Failed to get recent discoveries: {str(e)}")
            return []
    
    def validate_object_id(self, object_id: str) -> bool:
        """
        Check if an object exists in MPC database.
        
        Args:
            object_id: Object identifier to validate
            
        Returns:
            True if object exists
        """
        elements = self.get_orbital_elements(object_id)
        return elements is not None
    
    def get_observation_count(self, object_id: str) -> int:
        """
        Get the number of observations for an object.
        
        Args:
            object_id: Object identifier
            
        Returns:
            Number of observations
        """
        try:
            url = f"{self.base_url}/observations"
            params = {
                'designation': object_id,
                'count_only': True
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('count', 0)
            
        except Exception as e:
            logger.error(f"Failed to get observation count for {object_id}: {str(e)}")
            return 0

# Global instance
mpc_service = MinorPlanetCenterService()
