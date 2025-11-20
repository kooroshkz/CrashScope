#!/usr/bin/env python3
"""
CrashScope - Live traffic incident analysis application.

Main entry point that performs comprehensive incident analysis across Netherlands
and generates detailed ML-ready feature data with complete API integration.
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from crashscope import CrashScopeFeatureEngine, TomTomClient


class CrashScopeApp:
    """Main CrashScope application with comprehensive analysis capabilities."""
    
    def __init__(self):
        """Initialize CrashScope application."""
        self.tomtom_client = TomTomClient()
        self.feature_engine = CrashScopeFeatureEngine()
        
        # Coverage boxes for complete Netherlands scanning
        self.coverage_boxes = [
            (3.2, 50.7, 4.0, 51.3), (4.0, 50.7, 4.8, 51.3),
            (4.8, 50.7, 5.6, 51.3), (5.6, 50.7, 6.1, 51.3),
            (3.2, 51.3, 4.0, 51.9), (4.0, 51.3, 4.8, 51.9),
            (4.8, 51.3, 5.6, 51.9), (5.6, 51.3, 6.1, 51.9),
            (3.2, 51.9, 4.0, 52.5), (4.0, 51.9, 4.8, 52.5),
            (4.8, 51.9, 5.6, 52.5), (5.6, 51.9, 6.1, 52.5),
            (3.2, 52.5, 4.0, 53.1), (4.0, 52.5, 4.8, 53.1),
            (4.8, 52.5, 5.6, 53.1), (5.6, 52.5, 6.1, 53.1),
        ]
        
        # Create output directory
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def run(self) -> None:
        """Run comprehensive incident analysis."""
        print("CrashScope Live Traffic Incident Analysis")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Scanning {len(self.coverage_boxes)} regions across Netherlands...")
        
        # Fetch incidents from all regions
        all_incidents = self._fetch_all_incidents()
        
        if not all_incidents:
            print("No live incidents found in any region")
            return
        
        # Remove duplicates
        unique_incidents = self._deduplicate_incidents(all_incidents)
        print(f"Processing {len(unique_incidents)} unique live incidents...")
        
        # Process each incident
        results = []
        for i, incident in enumerate(unique_incidents.values(), 1):
            print(f"Processing incident {i}/{len(unique_incidents)}...")
            result = self._process_incident(incident)
            if result:
                results.append(result)
                self._log_incident_summary(result, i)
        
        # Save results and generate summary
        if results:
            self._save_results(results)
            self._print_final_summary(results)
        else:
            print("No incidents could be processed successfully")
    
    def _fetch_all_incidents(self) -> List[Dict]:
        """Fetch incidents from all coverage regions."""
        all_incidents = []
        
        for i, box in enumerate(self.coverage_boxes, 1):
            minLon, minLat, maxLon, maxLat = box
            bbox_str = f"{minLon},{minLat},{maxLon},{maxLat}"
            
            print(f"Scanning region {i:2d}/{len(self.coverage_boxes)} "
                  f"({minLon:.1f},{minLat:.1f} to {maxLon:.1f},{maxLat:.1f})...", end=" ")
            
            incidents = self.tomtom_client.fetch_incidents(bbox=bbox_str)
            
            if incidents:
                print(f"Found {len(incidents)} incidents")
                for incident in incidents:
                    incident['source_region'] = i
                all_incidents.extend(incidents)
            else:
                print("No incidents")
        
        print(f"\nTotal incidents collected: {len(all_incidents)}")
        return all_incidents
    
    def _deduplicate_incidents(self, incidents: List[Dict]) -> Dict:
        """Remove duplicate incidents based on coordinates and properties."""
        unique_incidents = {}
        
        for incident in incidents:
            key = self._generate_incident_key(incident)
            if key not in unique_incidents:
                unique_incidents[key] = incident
        
        print(f"Unique incidents after deduplication: {len(unique_incidents)}")
        return unique_incidents
    
    def _generate_incident_key(self, incident: Dict) -> tuple:
        """Generate unique key for incident deduplication."""
        try:
            geometry = incident.get('geometry', {})
            coords = geometry.get('coordinates', [])
            
            if isinstance(coords, list) and coords and isinstance(coords[0], (float, int)):
                coords_key = (tuple(coords),)
            else:
                coords_key = tuple(tuple(c) for c in coords) if coords else ()
            
            icon_category = incident.get('properties', {}).get('iconCategory')
            return (coords_key, icon_category)
            
        except (KeyError, TypeError):
            return (str(incident),)
    
    def _process_incident(self, incident: Dict) -> Dict:
        """Process single incident with comprehensive feature extraction."""
        try:
            # Extract coordinates
            coordinates = self.tomtom_client.extract_coordinates(incident)
            if not coordinates:
                return None
            
            latitude, longitude = coordinates
            properties = incident.get('properties', {})
            geometry = incident.get('geometry', {})
            timestamp = properties.get('startTime')
            
            # Engineer features
            features = self.feature_engine.engineer_features(
                latitude=latitude,
                longitude=longitude,
                timestamp=timestamp,
                incident_data=incident
            )
            
            # Calculate risk assessment
            risk_score = self._calculate_risk_score(features)
            
            return {
                'incident_metadata': {
                    'incident_id': properties.get('id', f"incident_{latitude:.4f}_{longitude:.4f}"),
                    'source_region': incident.get('source_region', 'unknown'),
                    'coordinates_display': f"{latitude:.4f}N, {longitude:.4f}E",
                    'timestamp': timestamp,
                    'geometry_type': geometry.get('type'),
                    'geometry_points': len(geometry.get('coordinates', [])) if geometry.get('type') == 'LineString' else 1
                },
                'location_analysis': {
                    'coordinates': {'latitude': latitude, 'longitude': longitude},
                    'area_classification': features['area_type'],
                    'region': self._identify_region(latitude, longitude),
                    'road_infrastructure': {
                        'road_type': features['road_type'],
                        'speed_limit_kmh': features['speed_limit'],
                        'lanes': features['lanes'],
                        'surface_type': features['surface'],
                        'lighting_available': features['lit']
                    }
                },
                'environmental_conditions': {
                    'weather': {
                        'condition': features['weather_condition'],
                        'temperature_celsius': features['temperature'],
                        'precipitation_mm': features['precipitation'],
                        'wind_speed_kmh': features['wind_speed'],
                        'weather_code': features['weather_code'],
                        'is_wet_conditions': features['is_wet']
                    },
                    'temporal': {
                        'hour': features['hour'],
                        'day_of_week': features['day_of_week'],
                        'month': features['month'],
                        'year': features['year'],
                        'season': features['season'],
                        'time_period': features['time_period'],
                        'is_weekend': features['is_weekend'],
                        'is_rush_hour': features['is_rush_hour'],
                        'is_night_time': features['is_night']
                    }
                },
                'risk_assessment': {
                    'overall_risk_score': risk_score,
                    'risk_level': 'High' if risk_score >= 7 else 'Medium' if risk_score >= 4 else 'Low',
                    'estimated_parties_involved': features['aantal_partijen'],
                    'lighting_conditions': features['lichtgesteldheid'],
                    'risk_factors': {
                        'speed_risk': 'High' if features['speed_limit'] > 80 else 'Medium' if features['speed_limit'] > 50 else 'Low',
                        'weather_risk': 'High' if features['is_wet'] or features['temperature'] < 3 else 'Medium' if features['temperature'] < 10 else 'Low',
                        'temporal_risk': 'High' if features['is_night'] else 'Medium' if features['is_rush_hour'] else 'Low',
                        'location_risk': 'Medium' if features['area_type'] == 'Buiten' else 'Low',
                        'visibility_risk': 'High' if features['lichtgesteldheid'] == 'Duisternis' else 'Low'
                    }
                },
                'ml_ready_features': {
                    'lat': features['lat'],
                    'lon': features['lon'],
                    'aantal_partijen': features['aantal_partijen'],
                    'jaar': features['year'],
                    'snelheid': features['speed_limit'],
                    'gebied': features['area_type'],
                    'lichtgesteldheid': features['lichtgesteldheid'],
                    'wegsoort': features['road_type'],
                    'weather_condition': features['weather_condition'],
                    'temperature': features['temperature'],
                    'is_weekend': features['is_weekend'],
                    'is_rush_hour': features['is_rush_hour']
                },
                'complete_feature_set': features,
                'raw_incident_data': incident
            }
            
        except Exception as e:
            print(f"Error processing incident: {e}")
            return None
    
    def _calculate_risk_score(self, features: Dict) -> float:
        """Calculate composite risk score (0-10 scale)."""
        score = 0
        
        # Speed factor (0-3 points)
        if features['speed_limit'] > 100:
            score += 3
        elif features['speed_limit'] > 70:
            score += 2
        elif features['speed_limit'] > 50:
            score += 1
        
        # Weather factor (0-2 points)
        if features['is_wet'] or features['temperature'] < 3:
            score += 2
        elif features['temperature'] < 10:
            score += 1
        
        # Time factor (0-2 points)
        if features['is_night']:
            score += 2
        elif features['is_rush_hour']:
            score += 1
        
        # Location factor (0-2 points)
        if features['area_type'] == 'Buiten':
            score += 1
        if features['lit'] == 'no' or features['lit'] == 'unknown':
            score += 1
        
        # Parties factor (0-1 point)
        if features['aantal_partijen'] > 1:
            score += 1
        
        return min(score, 10)
    
    def _identify_region(self, lat: float, lon: float) -> str:
        """Identify Dutch region from coordinates."""
        if 52.3 <= lat <= 52.4 and 4.8 <= lon <= 5.0:
            return "Amsterdam"
        elif 52.0 <= lat <= 52.1 and 4.2 <= lon <= 4.4:
            return "Den Haag"
        elif 51.9 <= lat <= 52.0 and 4.4 <= lon <= 4.6:
            return "Rotterdam"
        elif 52.1 <= lat <= 52.2 and 5.1 <= lon <= 5.2:
            return "Utrecht"
        elif lat > 53.0:
            return "Noord-Nederland"
        elif lat < 51.5:
            return "Zuid-Nederland"
        else:
            return "Midden-Nederland"
    
    def _log_incident_summary(self, result: Dict, index: int) -> None:
        """Log summary of processed incident."""
        meta = result['incident_metadata']
        location = result['location_analysis']
        risk = result['risk_assessment']
        weather = result['environmental_conditions']['weather']
        
        print(f"  Incident {index}: {meta['coordinates_display']} in {location['region']}")
        print(f"    Risk Level: {risk['risk_level']} (Score: {risk['overall_risk_score']}/10)")
        print(f"    Road: {location['road_infrastructure']['road_type']} "
              f"({location['road_infrastructure']['speed_limit_kmh']} km/h)")
        print(f"    Weather: {weather['condition']} ({weather['temperature_celsius']:.1f}C)")
        print(f"    Parties: {risk['estimated_parties_involved']}")
    
    def _save_results(self, results: List[Dict]) -> None:
        """Save results to output directory."""
        try:
            output_file = self.output_dir / "results.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str, ensure_ascii=False)
            
            print(f"\nResults saved to: {output_file}")
            
        except IOError as e:
            print(f"Error saving results: {e}")
    
    def _print_final_summary(self, results: List[Dict]) -> None:
        """Print final analysis summary."""
        print(f"\nANALYSIS COMPLETE")
        print("=" * 60)
        print(f"Total incidents processed: {len(results)}")
        
        # Risk level distribution
        risk_levels = {'High': 0, 'Medium': 0, 'Low': 0}
        regions = {}
        
        for result in results:
            risk_level = result['risk_assessment']['risk_level']
            risk_levels[risk_level] += 1
            
            region = result['location_analysis']['region']
            regions[region] = regions.get(region, 0) + 1
        
        print("\nRisk Level Distribution:")
        for level, count in risk_levels.items():
            print(f"  {level} Risk: {count} incidents")
        
        print("\nRegional Distribution:")
        for region, count in sorted(regions.items()):
            print(f"  {region}: {count} incidents")
        
        print(f"\nDetailed results available in: output/results.json")


def main():
    """Main entry point."""
    try:
        app = CrashScopeApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()