"""
Test the main CrashScope feature engineering functionality.
"""

import pytest
from crashscope.features.engine import CrashScopeFeatureEngine


class TestCrashScopeFeatureEngine:
    """Test the main feature engineering engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = CrashScopeFeatureEngine()
        self.test_lat = 52.3676
        self.test_lon = 4.9041  # Amsterdam coordinates
    
    def test_feature_engineering_basic(self):
        """Test basic feature engineering functionality."""
        features = self.engine.engineer_features(
            latitude=self.test_lat,
            longitude=self.test_lon
        )
        
        # Check required features are present
        required_features = [
            'lat', 'lon', 'temperature', 'precipitation', 
            'weather_condition', 'speed_limit', 'road_type',
            'area_type', 'hour', 'year', 'aantal_partijen',
            'lichtgesteldheid'
        ]
        
        for feature in required_features:
            assert feature in features, f"Missing feature: {feature}"
        
        # Check coordinate accuracy
        assert abs(features['lat'] - self.test_lat) < 0.001
        assert abs(features['lon'] - self.test_lon) < 0.001
    
    def test_feature_engineering_with_timestamp(self):
        """Test feature engineering with timestamp."""
        timestamp = "2025-01-15T14:30:00Z"
        
        features = self.engine.engineer_features(
            latitude=self.test_lat,
            longitude=self.test_lon,
            timestamp=timestamp
        )
        
        assert features['hour'] == 14
        assert features['year'] == 2025
        assert features['is_rush_hour'] == False
    
    def test_feature_engineering_with_incident_data(self):
        """Test feature engineering with incident data."""
        incident_data = {
            'properties': {
                'iconCategory': 1,
                'startTime': '2025-01-15T08:00:00Z'
            }
        }
        
        features = self.engine.engineer_features(
            latitude=self.test_lat,
            longitude=self.test_lon,
            incident_data=incident_data
        )
        
        assert features['aantal_partijen'] == 2
        assert features['is_rush_hour'] == True


def test_coordinate_extraction():
    """Test coordinate extraction functionality."""
    from crashscope.api.tomtom import TomTomClient
    
    client = TomTomClient()
    
    # Test Point geometry
    point_incident = {
        'geometry': {
            'type': 'Point',
            'coordinates': [4.9041, 52.3676]
        }
    }
    
    coords = client.extract_coordinates(point_incident)
    assert coords is not None
    assert abs(coords[0] - 52.3676) < 0.001
    assert abs(coords[1] - 4.9041) < 0.001
    
    # Test LineString geometry
    line_incident = {
        'geometry': {
            'type': 'LineString',
            'coordinates': [[4.9041, 52.3676], [4.9050, 52.3680]]
        }
    }
    
    coords = client.extract_coordinates(line_incident)
    assert coords is not None
    assert abs(coords[0] - 52.3676) < 0.001
    assert abs(coords[1] - 4.9041) < 0.001


if __name__ == "__main__":
    pytest.main([__file__])