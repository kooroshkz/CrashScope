"""
Road feature extraction using OpenStreetMap data.
"""

import requests
from typing import Dict
from ..utils.config import Config
from ..utils.cache import CacheManager


class RoadFeatureExtractor:
    """Extract road infrastructure features from OpenStreetMap."""
    
    def __init__(self):
        """Initialize road feature extractor."""
        self.cache = CacheManager(Config.get_cache_timeout())
        self.overpass_url = Config.get_osm_overpass_url()
        self.timeout = Config.get_request_timeout()
    
    def extract_features(self, lat: float, lon: float) -> Dict:
        """Extract road features for given coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary of road infrastructure features
        """
        cache_key = f"road_{lat:.3f}_{lon:.3f}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        try:
            query = self._build_overpass_query(lat, lon)
            
            response = requests.post(
                self.overpass_url,
                data=query,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                osm_data = response.json()
                features = self._process_osm_data(osm_data)
                self.cache.set(cache_key, features)
                return features
                
        except (requests.RequestException, ValueError):
            pass
        
        return self._get_default_road_features()
    
    def classify_area(self, lat: float, lon: float) -> str:
        """Determine if area is urban or rural.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            'Binnen' for urban, 'Buiten' for rural
        """
        try:
            query = f"""
            [out:json][timeout:5];
            (
              rel(around:2000,{lat},{lon})["place"~"city|town"];
              way(around:2000,{lat},{lon})["place"~"city|town"];
            );
            out;
            """
            
            response = requests.post(
                self.overpass_url,
                data=query,
                timeout=5
            )
            
            if response.status_code == 200:
                place_data = response.json()
                if place_data.get('elements'):
                    return 'Binnen'  # Urban
                    
        except (requests.RequestException, ValueError):
            pass
        
        return 'Buiten'  # Default to rural
    
    def _build_overpass_query(self, lat: float, lon: float) -> str:
        """Build Overpass query for road data."""
        return f"""
        [out:json][timeout:10];
        (
          way(around:100,{lat},{lon})["highway"];
        );
        out geom;
        """
    
    def _process_osm_data(self, osm_data: Dict) -> Dict:
        """Process OSM data into road features."""
        features = self._get_default_road_features()
        
        if not osm_data.get('elements'):
            return features
        
        # Process first road element found
        road = osm_data['elements'][0]
        tags = road.get('tags', {})
        
        # Speed limit
        if 'maxspeed' in tags:
            try:
                speed_str = tags['maxspeed'].replace('mph', '').replace('kmh', '')
                features['speed_limit'] = int(speed_str)
            except ValueError:
                pass
        
        # Road type and default speeds
        if 'highway' in tags:
            highway_type = tags['highway']
            features['road_type'] = highway_type
            
            # Set default speeds based on road type if still default
            if features['speed_limit'] == 50:
                speed_defaults = {
                    'motorway': 130,
                    'trunk': 100,
                    'primary': 80,
                    'secondary': 80,
                    'tertiary': 60,
                    'residential': 30,
                    'living_street': 15
                }
                features['speed_limit'] = speed_defaults.get(highway_type, 50)
        
        # Number of lanes
        if 'lanes' in tags:
            try:
                features['lanes'] = int(tags['lanes'])
            except ValueError:
                pass
        
        # Surface type
        if 'surface' in tags:
            features['surface'] = tags['surface']
        
        # Lighting
        if 'lit' in tags:
            features['lit'] = 'yes' if tags['lit'] == 'yes' else 'no'
        
        return features
    
    def _get_default_road_features(self) -> Dict:
        """Get default road features when OSM data unavailable."""
        return {
            'speed_limit': 50,
            'road_type': 'residential',
            'lanes': 2,
            'surface': 'asphalt',
            'lit': 'unknown'
        }