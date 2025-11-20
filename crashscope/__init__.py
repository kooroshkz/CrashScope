"""
CrashScope: Live traffic incident analysis and crash prediction system.

This package provides tools for:
- Real-time traffic incident data collection from TomTom API
- Feature engineering from GPS coordinates using weather and road data
- Machine learning-ready feature extraction for crash prediction
"""

__version__ = "1.0.0"
__author__ = "CrashScope Team"

from .features.engine import CrashScopeFeatureEngine
from .api.tomtom import TomTomClient

__all__ = ["CrashScopeFeatureEngine", "TomTomClient"]