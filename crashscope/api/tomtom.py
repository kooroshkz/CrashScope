"""
TomTom API client for traffic incident data.
"""

import os
import requests
from typing import List, Dict, Optional
from ..utils.config import Config


class TomTomClient:
    """Client for TomTom Traffic Incidents API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize TomTom client.
        
        Args:
            api_key: TomTom API key. If None, loads from environment.
        """
        self.api_key = api_key or Config.get_tomtom_api_key()
        self.base_url = "https://api.tomtom.com/traffic/services/5/incidentDetails"
        self.geocoding_url = "https://api.tomtom.com/search/2/reverseGeocode"
    
    def fetch_incidents(self, bbox: str, 
                       language: str = "en-GB", 
                       timeout: int = 15) -> List[Dict]:
        """Fetch traffic incidents from TomTom API.
        
        Args:
            bbox: Bounding box for incidents (required)
            language: Response language
            timeout: Request timeout in seconds
            
        Returns:
            List of incident dictionaries
        """
        if not bbox:
            raise ValueError("bbox parameter is required")
        
        # Build URL manually to avoid double encoding of fields parameter
        fields_encoded = "%7Bincidents%7Btype%2Cgeometry%7Btype%2Ccoordinates%7D%2Cproperties%7BiconCategory%7D%7D%7D"
        
        url = (
            f"{self.base_url}?"
            f"key={self.api_key}&"
            f"bbox={bbox}&"
            f"fields={fields_encoded}&"
            f"language={language}&"
            f"categoryFilter=Accident&"
            f"timeValidityFilter=present"
        )
        
        try:
            response = requests.get(url, timeout=timeout)
            
            if response.status_code != 200:
                return []
                
            data = response.json()
            incidents = data.get('incidents', [])
            return incidents
            
        except (requests.RequestException, ValueError):
            return []
    
    def extract_coordinates(self, incident: Dict) -> Optional[tuple]:
        """Extract coordinates from incident geometry.
        
        Args:
            incident: Incident dictionary from TomTom API
            
        Returns:
            Tuple of (latitude, longitude) or None if invalid
        """
        try:
            geometry = incident['geometry']
            coords = geometry['coordinates']
            
            if geometry['type'] == 'Point':
                longitude, latitude = coords[0], coords[1]
            elif geometry['type'] == 'LineString':
                longitude, latitude = coords[0][0], coords[0][1]
            else:
                return None
                
            return latitude, longitude
            
        except (KeyError, IndexError, TypeError):
            return None
    
    def reverse_geocode(self, lat: float, lon: float, timeout: int = 10) -> str:
        """Convert coordinates to readable address using TomTom Reverse Geocoding.
        
        Args:
            lat: Latitude
            lon: Longitude
            timeout: Request timeout in seconds
            
        Returns:
            Formatted address string or "Unknown" if not found
        """
        url = f"{self.geocoding_url}/{lat},{lon}.json"
        
        params = {
            'key': self.api_key,
            'language': 'en-GB'
        }
        
        try:
            response = requests.get(url, params=params, timeout=timeout)
            
            if response.status_code != 200:
                return "Unknown"
            
            data = response.json()
            results = data.get('addresses', [])
            
            if not results:
                return "Unknown"
            
            address = results[0].get('address', {})
            
            # Build formatted address
            parts = []
            if address.get('streetName'):
                street = address.get('streetName')
                if address.get('streetNumber'):
                    street = f"{address.get('streetNumber')} {street}"
                parts.append(street)
            
            if address.get('municipality'):
                parts.append(address.get('municipality'))
            
            if address.get('countrySubdivision'):
                parts.append(address.get('countrySubdivision'))
            
            return ', '.join(parts) if parts else address.get('freeformAddress', 'Unknown')
            
        except (requests.RequestException, ValueError, KeyError):
            return "Unknown"