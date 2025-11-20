"""
Temporal feature extraction from timestamps.
"""

from datetime import datetime
from typing import Dict, Optional


class TemporalFeatureExtractor:
    """Extract time-based features from timestamps."""
    
    def extract_features(self, timestamp: Optional[str] = None) -> Dict:
        """Extract temporal features from timestamp.
        
        Args:
            timestamp: ISO timestamp string (optional, uses current time if None)
            
        Returns:
            Dictionary of temporal features
        """
        if timestamp is None:
            dt = datetime.now()
        else:
            try:
                # Parse ISO timestamp from TomTom API
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                dt = datetime.now()
        
        return {
            'hour': dt.hour,
            'day_of_week': dt.weekday(),
            'month': dt.month,
            'year': dt.year,
            'is_weekend': dt.weekday() >= 5,
            'is_rush_hour': dt.hour in [7, 8, 9, 16, 17, 18, 19],
            'is_night': dt.hour < 6 or dt.hour > 22,
            'season': self._get_season(dt.month),
            'time_period': self._get_time_period(dt.hour)
        }
    
    def _get_season(self, month: int) -> str:
        """Get season from month."""
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:  # 9, 10, 11
            return 'Autumn'
    
    def _get_time_period(self, hour: int) -> str:
        """Get time period from hour."""
        if 6 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 18:
            return 'Afternoon'
        elif 18 <= hour < 22:
            return 'Evening'
        else:
            return 'Night'