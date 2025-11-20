"""
Main feature engineering engine that orchestrates all feature extractors.
"""

from typing import Dict, Optional
from .weather import WeatherFeatureExtractor
from .road import RoadFeatureExtractor
from .temporal import TemporalFeatureExtractor


class CrashScopeFeatureEngine:
    """Main feature engineering engine for crash prediction."""
    
    def __init__(self):
        """Initialize feature engine with all extractors."""
        self.weather_extractor = WeatherFeatureExtractor()
        self.road_extractor = RoadFeatureExtractor()
        self.temporal_extractor = TemporalFeatureExtractor()
    
    def engineer_features(self, 
                         latitude: float, 
                         longitude: float, 
                         timestamp: Optional[str] = None, 
                         incident_data: Optional[Dict] = None) -> Dict:
        """Extract all features for given location and time.
        
        Args:
            latitude: GPS latitude
            longitude: GPS longitude  
            timestamp: ISO timestamp string (optional)
            incident_data: Additional incident data (optional)
            
        Returns:
            Dictionary containing all engineered features
        """
        features = {}
        
        # Extract weather features
        weather_features = self.weather_extractor.extract_features(
            latitude, longitude
        )
        features.update(weather_features)
        
        # Extract temporal features
        temporal_features = self.temporal_extractor.extract_features(timestamp)
        features.update(temporal_features)
        
        # Extract road features
        road_features = self.road_extractor.extract_features(
            latitude, longitude
        )
        features.update(road_features)
        
        # Extract area classification
        features['area_type'] = self.road_extractor.classify_area(
            latitude, longitude
        )
        
        # Add coordinates
        features['lat'] = latitude
        features['lon'] = longitude
        
        # Extract incident-specific features
        if incident_data:
            features['aantal_partijen'] = self._estimate_parties(incident_data)
        else:
            features['aantal_partijen'] = 2  # Default assumption
        
        # Add lighting condition based on time and infrastructure
        features['lichtgesteldheid'] = self._determine_lighting(
            features['hour'], features['lit']
        )
        
        return features
    
    def _estimate_parties(self, incident_data: Dict) -> int:
        """Estimate number of parties involved in incident.
        
        Args:
            incident_data: Incident data from TomTom API
            
        Returns:
            Estimated number of parties
        """
        try:
            icon_category = incident_data.get('properties', {}).get('iconCategory')
            if icon_category == 1:
                return 2  # Typical accident involves 2 parties
            return 1  # Single vehicle incident
        except (KeyError, TypeError):
            return 2  # Default assumption
    
    def _determine_lighting(self, hour: int, road_lit: str) -> str:
        """Determine lighting conditions.
        
        Args:
            hour: Hour of day (0-23)
            road_lit: Road lighting status ('yes', 'no', 'unknown')
            
        Returns:
            Lighting condition in Dutch
        """
        if 6 <= hour <= 20:
            return 'Daglicht'
        elif road_lit == 'yes':
            return 'Kunstlicht'
        else:
            return 'Duisternis'