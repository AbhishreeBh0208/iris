"""Space-Track.org service for satellite tracking data."""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
import os

logger = logging.getLogger(__name__)

class SpaceTrackService:
    """Service for fetching satellite data from Space-Track.org."""
    
    def __init__(self):
        self.base_url = "https://www.space-track.org"
        self.session = requests.Session()
        self.cache = {}
        self.authenticated = False
        
        # These would normally come from environment variables
        self.username = os.getenv('SPACETRACK_USERNAME')
        self.password = os.getenv('SPACETRACK_PASSWORD')
        
    def _authenticate(self) -> bool:
        """Authenticate with Space-Track.org."""
        if self.authenticated:
            return True
            
        if not self.username or not self.password:
            logger.warning("Space-Track credentials not configured")
            return False
            
        try:
            # Login to Space-Track
            login_url = f"{self.base_url}/ajaxauth/login"
            login_data = {
                'identity': self.username,
                'password': self.password
            }
            
            response = self.session.post(login_url, data=login_data, timeout=10)
            response.raise_for_status()
            
            self.authenticated = True
            logger.info("Successfully authenticated with Space-Track.org")
            return True
            
        except Exception as e:
            logger.error(f"Space-Track authentication failed: {str(e)}")
            return False
    
    def search_satellites(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for satellites by name or NORAD ID.
        
        Args:
            query: Search query (satellite name or NORAD ID)
            limit: Maximum number of results
            
        Returns:
            List of matching satellites
        """
        if not self._authenticate():
            return []
            
        try:
            cache_key = f"search_{query}_{limit}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Search by name first
            search_url = f"{self.base_url}/basicspacedata/query/class/satcat"
            params = {
                'OBJECT_NAME': f'~~{query}',  # Contains query
                'orderby': 'OBJECT_NAME',
                'limit': limit,
                'format': 'json'
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            satellites = []
            
            for sat in data:
                satellites.append({
                    'norad_id': int(sat.get('NORAD_CAT_ID', 0)),
                    'name': sat.get('OBJECT_NAME', 'Unknown'),
                    'international_designator': sat.get('INTLDES', ''),
                    'launch_date': sat.get('LAUNCH_DATE', ''),
                    'decay_date': sat.get('DECAY_DATE', ''),
                    'object_type': sat.get('OBJECT_TYPE', 'unknown'),
                    'country': sat.get('COUNTRY_CODE', ''),
                    'rcs_size': sat.get('RCS_SIZE', ''),
                    'status': 'active' if not sat.get('DECAY_DATE') else 'decayed',
                    'source': 'Space-Track'
                })
            
            self.cache[cache_key] = satellites
            logger.info(f"Found {len(satellites)} satellites for query '{query}'")
            return satellites
            
        except Exception as e:
            logger.error(f"Space-Track search failed for '{query}': {str(e)}")
            return []
    
    def get_tle_data(self, norad_id: int, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Get TLE (Two-Line Element) data for a satellite.
        
        Args:
            norad_id: NORAD catalog ID
            days_back: How many days back to retrieve TLEs
            
        Returns:
            List of TLE data
        """
        if not self._authenticate():
            return []
            
        try:
            cache_key = f"tle_{norad_id}_{days_back}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            tle_url = f"{self.base_url}/basicspacedata/query/class/gp"
            params = {
                'NORAD_CAT_ID': norad_id,
                'EPOCH': f'{start_date.strftime("%Y-%m-%d")}--{end_date.strftime("%Y-%m-%d")}',
                'orderby': 'EPOCH desc',
                'format': 'json'
            }
            
            response = self.session.get(tle_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            tles = []
            
            for tle in data:
                tles.append({
                    'norad_id': int(tle.get('NORAD_CAT_ID', 0)),
                    'name': tle.get('OBJECT_NAME', 'Unknown'),
                    'epoch': tle.get('EPOCH', ''),
                    'mean_motion': float(tle.get('MEAN_MOTION', 0)),
                    'eccentricity': float(tle.get('ECCENTRICITY', 0)),
                    'inclination': float(tle.get('INCLINATION', 0)),
                    'raan': float(tle.get('RA_OF_ASC_NODE', 0)),
                    'arg_perigee': float(tle.get('ARG_OF_PERICENTER', 0)),
                    'mean_anomaly': float(tle.get('MEAN_ANOMALY', 0)),
                    'tle_line1': tle.get('TLE_LINE1', ''),
                    'tle_line2': tle.get('TLE_LINE2', ''),
                    'source': 'Space-Track'
                })
            
            self.cache[cache_key] = tles
            return tles
            
        except Exception as e:
            logger.error(f"Failed to get TLE data for NORAD ID {norad_id}: {str(e)}")
            return []
    
    def get_satellite_info(self, norad_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a satellite.
        
        Args:
            norad_id: NORAD catalog ID
            
        Returns:
            Satellite information or None
        """
        if not self._authenticate():
            return None
            
        try:
            cache_key = f"info_{norad_id}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            info_url = f"{self.base_url}/basicspacedata/query/class/satcat"
            params = {
                'NORAD_CAT_ID': norad_id,
                'format': 'json'
            }
            
            response = self.session.get(info_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                sat = data[0]
                info = {
                    'norad_id': int(sat.get('NORAD_CAT_ID', 0)),
                    'name': sat.get('OBJECT_NAME', 'Unknown'),
                    'international_designator': sat.get('INTLDES', ''),
                    'launch_date': sat.get('LAUNCH_DATE', ''),
                    'launch_site': sat.get('SITE', ''),
                    'decay_date': sat.get('DECAY_DATE', ''),
                    'period': float(sat.get('PERIOD', 0)) if sat.get('PERIOD') else None,
                    'inclination': float(sat.get('INCLINATION', 0)) if sat.get('INCLINATION') else None,
                    'apogee': float(sat.get('APOGEE', 0)) if sat.get('APOGEE') else None,
                    'perigee': float(sat.get('PERIGEE', 0)) if sat.get('PERIGEE') else None,
                    'object_type': sat.get('OBJECT_TYPE', 'unknown'),
                    'country': sat.get('COUNTRY_CODE', ''),
                    'owner': sat.get('OWNER', ''),
                    'rcs_size': sat.get('RCS_SIZE', ''),
                    'status': 'active' if not sat.get('DECAY_DATE') else 'decayed',
                    'source': 'Space-Track'
                }
                
                self.cache[cache_key] = info
                return info
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get satellite info for NORAD ID {norad_id}: {str(e)}")
            return None
    
    def validate_norad_id(self, norad_id: int) -> bool:
        """
        Check if a NORAD ID exists in the catalog.
        
        Args:
            norad_id: NORAD catalog ID to validate
            
        Returns:
            True if NORAD ID exists
        """
        info = self.get_satellite_info(norad_id)
        return info is not None
    
    def get_recent_launches(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get recently launched satellites.
        
        Args:
            days: Number of days back to search
            
        Returns:
            List of recently launched satellites
        """
        if not self._authenticate():
            return []
            
        try:
            cache_key = f"recent_launches_{days}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            launches_url = f"{self.base_url}/basicspacedata/query/class/launch"
            params = {
                'LAUNCH_DATE': f'{start_date.strftime("%Y-%m-%d")}--{end_date.strftime("%Y-%m-%d")}',
                'orderby': 'LAUNCH_DATE desc',
                'format': 'json'
            }
            
            response = self.session.get(launches_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            launches = []
            
            for launch in data:
                launches.append({
                    'launch_date': launch.get('LAUNCH_DATE', ''),
                    'launch_site': launch.get('SITE', ''),
                    'launch_vehicle': launch.get('LAUNCH_VEHICLE', ''),
                    'mission': launch.get('PAYLOAD', ''),
                    'country': launch.get('COUNTRY_CODE', ''),
                    'source': 'Space-Track'
                })
            
            self.cache[cache_key] = launches
            return launches
            
        except Exception as e:
            logger.error(f"Failed to get recent launches: {str(e)}")
            return []

# Global instance
space_track_service = SpaceTrackService()
