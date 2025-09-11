"""Data coordinator service for managing multi-source astronomical data."""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from .nasa_horizons import nasa_horizons_service
from .minor_planet_center import mpc_service
from .space_track import space_track_service
from .orbit_propagator import orbit_propagator_service

logger = logging.getLogger(__name__)

class DataCoordinatorService:
    """Coordinates data from multiple astronomical sources with fallback logic."""
    
    def __init__(self):
        self.services = {
            'nasa_horizons': nasa_horizons_service,
            'mpc': mpc_service,
            'space_track': space_track_service,
            'orbit_propagator': orbit_propagator_service
        }
        self.cache = {}
        
    def get_object_trajectory(
        self,
        object_id: str,
        start_date: datetime,
        end_date: datetime,
        step_size: str = "1d"
    ) -> Dict[str, Any]:
        """
        Get trajectory data with multi-source fallback.
        
        Args:
            object_id: Object identifier
            start_date: Start date for trajectory
            end_date: End date for trajectory
            step_size: Time step size
            
        Returns:
            Trajectory data with metadata about sources used
        """
        sources_tried = []
        errors = {}
        
        # Try NASA Horizons first (most reliable for solar system objects)
        try:
            logger.info(f"Attempting NASA Horizons for {object_id}")
            trajectory = self.services['nasa_horizons'].fetch_trajectory(
                object_id, start_date, end_date, step_size
            )
            
            if trajectory and len(trajectory) > 0:
                sources_tried.append('nasa_horizons')
                return {
                    'success': True,
                    'trajectory': trajectory,
                    'sources_used': ['nasa_horizons'],
                    'sources_tried': sources_tried,
                    'total_points': len(trajectory),
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'object_id': object_id
                }
                
        except Exception as e:
            sources_tried.append('nasa_horizons')
            errors['nasa_horizons'] = str(e)
            logger.warning(f"NASA Horizons failed for {object_id}: {str(e)}")
        
        # Try MPC for orbital elements and propagate
        try:
            logger.info(f"Attempting MPC + propagation for {object_id}")
            elements = self.services['mpc'].get_orbital_elements(object_id)
            
            if elements:
                trajectory = self.services['orbit_propagator'].propagate_from_elements(
                    elements, start_date, end_date, 
                    step_hours=24 if step_size == "1d" else 1
                )
                
                if trajectory and len(trajectory) > 0:
                    sources_tried.extend(['mpc', 'orbit_propagator'])
                    return {
                        'success': True,
                        'trajectory': trajectory,
                        'sources_used': ['mpc', 'orbit_propagator'],
                        'sources_tried': sources_tried,
                        'total_points': len(trajectory),
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'object_id': object_id,
                        'orbital_elements': elements
                    }
                    
        except Exception as e:
            sources_tried.extend(['mpc', 'orbit_propagator'])
            errors['mpc_propagation'] = str(e)
            logger.warning(f"MPC + propagation failed for {object_id}: {str(e)}")
        
        # Try Space-Track for satellites (if object_id looks like NORAD ID)
        if self._looks_like_norad_id(object_id):
            try:
                logger.info(f"Attempting Space-Track for {object_id}")
                norad_id = int(object_id)
                
                # Get TLE data
                tle_data = self.services['space_track'].get_tle_data(norad_id, days_back=30)
                
                if tle_data:
                    # Convert TLE to trajectory (simplified)
                    trajectory = self._tle_to_trajectory(tle_data[0], start_date, end_date)
                    
                    if trajectory:
                        sources_tried.append('space_track')
                        return {
                            'success': True,
                            'trajectory': trajectory,
                            'sources_used': ['space_track'],
                            'sources_tried': sources_tried,
                            'total_points': len(trajectory),
                            'start_date': start_date.isoformat(),
                            'end_date': end_date.isoformat(),
                            'object_id': object_id,
                            'tle_data': tle_data[0]
                        }
                        
            except Exception as e:
                sources_tried.append('space_track')
                errors['space_track'] = str(e)
                logger.warning(f"Space-Track failed for {object_id}: {str(e)}")
        
        # All sources failed
        return {
            'success': False,
            'trajectory': [],
            'sources_used': [],
            'sources_tried': sources_tried,
            'errors': errors,
            'object_id': object_id,
            'message': f"Failed to retrieve trajectory data for {object_id} from all available sources"
        }
    
    def search_objects(
        self,
        query: str,
        object_types: List[str] = ["all"]
    ) -> List[Dict[str, Any]]:
        """
        Search for objects across all data sources.
        
        Args:
            query: Search query
            object_types: Types of objects to search for
            
        Returns:
            Consolidated list of matching objects
        """
        all_results = []
        seen_objects = set()
        
        # Search NASA Horizons
        try:
            nasa_results = self.services['nasa_horizons'].search_objects(query)
            for obj in nasa_results:
                key = obj['id'].lower()
                if key not in seen_objects:
                    obj['source'] = 'nasa_horizons'
                    all_results.append(obj)
                    seen_objects.add(key)
        except Exception as e:
            logger.warning(f"NASA Horizons search failed: {str(e)}")
        
        # Search MPC
        try:
            for obj_type in object_types:
                mpc_results = self.services['mpc'].search_objects(query, obj_type)
                for obj in mpc_results:
                    key = obj['id'].lower()
                    if key not in seen_objects:
                        obj['source'] = 'mpc'
                        all_results.append(obj)
                        seen_objects.add(key)
        except Exception as e:
            logger.warning(f"MPC search failed: {str(e)}")
        
        # Search Space-Track if query looks like satellite name or NORAD ID
        if any(obj_type in ["satellite", "all"] for obj_type in object_types):
            try:
                spacetrack_results = self.services['space_track'].search_satellites(query)
                for obj in spacetrack_results:
                    key = str(obj['norad_id'])
                    if key not in seen_objects:
                        # Convert to standard format
                        standardized = {
                            'id': str(obj['norad_id']),
                            'name': obj['name'],
                            'type': 'satellite',
                            'source': 'space_track',
                            'available': True,
                            'details': obj
                        }
                        all_results.append(standardized)
                        seen_objects.add(key)
            except Exception as e:
                logger.warning(f"Space-Track search failed: {str(e)}")
        
        logger.info(f"Found {len(all_results)} total objects for query '{query}'")
        return all_results
    
    def get_object_info(self, object_id: str) -> Dict[str, Any]:
        """
        Get comprehensive information about an object from all sources.
        
        Args:
            object_id: Object identifier
            
        Returns:
            Combined object information
        """
        info = {
            'id': object_id,
            'sources': {},
            'available': False
        }
        
        # Try NASA Horizons
        try:
            nasa_info = self.services['nasa_horizons'].get_object_info(object_id)
            if nasa_info['available']:
                info['sources']['nasa_horizons'] = nasa_info
                info['available'] = True
                info['name'] = nasa_info.get('name', object_id)
                info['type'] = nasa_info.get('type', 'unknown')
        except Exception as e:
            logger.debug(f"NASA Horizons info failed for {object_id}: {str(e)}")
        
        # Try MPC
        try:
            elements = self.services['mpc'].get_orbital_elements(object_id)
            if elements:
                info['sources']['mpc'] = {
                    'orbital_elements': elements,
                    'available': True
                }
                info['available'] = True
                if 'type' not in info:
                    info['type'] = 'asteroid_or_comet'
        except Exception as e:
            logger.debug(f"MPC info failed for {object_id}: {str(e)}")
        
        # Try Space-Track if it looks like NORAD ID
        if self._looks_like_norad_id(object_id):
            try:
                norad_id = int(object_id)
                sat_info = self.services['space_track'].get_satellite_info(norad_id)
                if sat_info:
                    info['sources']['space_track'] = sat_info
                    info['available'] = True
                    info['name'] = sat_info.get('name', object_id)
                    info['type'] = 'satellite'
            except Exception as e:
                logger.debug(f"Space-Track info failed for {object_id}: {str(e)}")
        
        return info
    
    def simulate_intercept_mission(
        self,
        target_object: str,
        intercept_date: datetime,
        mission_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate an intercept mission using the best available data.
        
        Args:
            target_object: Target object identifier
            intercept_date: Desired intercept date
            mission_parameters: Mission configuration
            
        Returns:
            Mission simulation results
        """
        try:
            # Get target trajectory with extended window for mission planning
            start_date = intercept_date - timedelta(days=730)  # 2 years before
            end_date = intercept_date + timedelta(days=730)   # 2 years after
            
            trajectory_result = self.get_object_trajectory(
                target_object, start_date, end_date
            )
            
            if not trajectory_result['success']:
                return {
                    'success': False,
                    'error': 'Failed to get target trajectory',
                    'details': trajectory_result
                }
            
            target_trajectory = trajectory_result['trajectory']
            
            # Default interceptor parameters
            interceptor_elements = mission_parameters.get('interceptor_elements', {
                'semi_major_axis': 1.0,  # AU
                'eccentricity': 0.1,
                'inclination': 5.0,  # degrees
                'longitude_ascending_node': 0.0,
                'argument_periapsis': 0.0,
                'mean_anomaly': 0.0
            })
            
            # Compute intercept
            intercept_result = self.services['orbit_propagator'].compute_intercept_trajectory(
                interceptor_elements,
                target_trajectory,
                intercept_date
            )
            
            # Add metadata
            intercept_result['target_object'] = target_object
            intercept_result['data_sources'] = trajectory_result['sources_used']
            intercept_result['mission_parameters'] = mission_parameters
            
            return intercept_result
            
        except Exception as e:
            logger.error(f"Mission simulation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'target_object': target_object
            }
    
    def _looks_like_norad_id(self, object_id: str) -> bool:
        """Check if object_id looks like a NORAD catalog ID."""
        try:
            norad_id = int(object_id)
            return 1 <= norad_id <= 99999  # Reasonable NORAD ID range
        except ValueError:
            return False
    
    def _tle_to_trajectory(
        self,
        tle_data: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Convert TLE data to trajectory points (simplified).
        
        Args:
            tle_data: TLE data dictionary
            start_date: Start date
            end_date: End date
            
        Returns:
            List of trajectory points
        """
        # This is a very simplified conversion
        # In practice, you'd use SGP4 or similar orbital propagator
        
        try:
            # Extract orbital parameters from TLE
            elements = {
                'semi_major_axis': 6371 + 500,  # Approximate for LEO satellite (km -> rough AU conversion)
                'eccentricity': tle_data.get('eccentricity', 0.0),
                'inclination': tle_data.get('inclination', 0.0),
                'longitude_ascending_node': tle_data.get('raan', 0.0),
                'argument_periapsis': tle_data.get('arg_perigee', 0.0),
                'mean_anomaly': tle_data.get('mean_anomaly', 0.0)
            }
            
            # Use orbit propagator (this will be Earth-centric, not heliocentric)
            trajectory = self.services['orbit_propagator'].propagate_from_elements(
                elements, start_date, end_date, step_hours=1
            )
            
            # Mark as satellite trajectory
            for point in trajectory:
                point['object_type'] = 'satellite'
                point['source'] = 'tle_propagation'
            
            return trajectory
            
        except Exception as e:
            logger.error(f"TLE to trajectory conversion failed: {str(e)}")
            return []

# Global instance
data_coordinator = DataCoordinatorService()
