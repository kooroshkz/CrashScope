"""
Weather feature extraction using Open-Meteo API.
"""

import requests
from typing import Dict, Optional
from ..utils.config import Config
from ..utils.cache import CacheManager


class WeatherFeatureExtractor:
    """Extract weather features from GPS coordinates."""
    
    def __init__(self):
        """Initialize weather feature extractor."""
        self.cache = CacheManager(Config.get_cache_timeout())
        self.api_url = Config.get_weather_api_url()
        self.timeout = Config.get_request_timeout()
    
    def extract_features(self, lat: float, lon: float) -> Dict:
        """Extract weather features for given coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary of weather features
        """
        cache_key = f"weather_{lat:.4f}_{lon:.4f}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,precipitation,wind_speed_10m,weathercode"
            }
            
            response = requests.get(
                self.api_url,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                weather_data = response.json()
                features = self._process_weather_data(weather_data)
                self.cache.set(cache_key, features)
                return features
                
        except (requests.RequestException, ValueError):
            pass
        
        # Return default values if API fails
        return self._get_default_weather()
    
    def _process_weather_data(self, weather_data: Dict) -> Dict:
        """Process weather API response into features."""
        if 'current' not in weather_data:
            return self._get_default_weather()
        
        current = weather_data['current']
        features = {
            'temperature': current.get('temperature_2m', 10),
            'precipitation': current.get('precipitation', 0),
            'wind_speed': current.get('wind_speed_10m', 10),
            'weather_code': current.get('weathercode', 1)
        }
        
        features['weather_condition'] = self._map_weather_condition(
            features['weather_code']
        )
        features['is_wet'] = features['precipitation'] > 0.1
        
        return features
    
    def _map_weather_condition(self, weather_code: int) -> str:
        """Map weather code to Dutch weather conditions."""
        if weather_code in [61, 63, 65, 80, 81, 82]:  # Rain
            return 'Regen'
        elif weather_code in [45, 48]:  # Fog
            return 'Mist'
        elif weather_code in [71, 73, 75, 77, 85, 86]:  # Snow
            return 'Sneeuw'
        else:  # Clear/cloudy
            return 'Droog'
    
    def _get_default_weather(self) -> Dict:
        """Get default weather values when API fails."""
        return {
            'temperature': 10,
            'precipitation': 0,
            'wind_speed': 10,
            'weather_code': 1,
            'weather_condition': 'Droog',
            'is_wet': False
        }