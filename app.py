#!/usr/bin/env python3
"""
CrashScope Web Application - Flask Backend API
Provides REST endpoints for live accident data with ML predictions
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import sys
from pathlib import Path
from dotenv import load_dotenv

from crashscope import CrashScopeFeatureEngine, TomTomClient
from crashscope.utils.ml_predictor import MLPredictor
from crashscope.utils.ai_reporter import AIReporter

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Initialize clients and ML predictor
tomtom_client = TomTomClient()
feature_engine = CrashScopeFeatureEngine()
ml_predictor = MLPredictor()
ai_reporter = AIReporter()

COVERAGE_BOXES = [
    # Row 1: 51.3 → 51.9
    (3.2, 51.3, 4.0, 51.9),
    (4.0, 51.3, 4.8, 51.9),
    (4.8, 51.3, 5.6, 51.9),
    (5.6, 51.3, 6.1, 51.9),

    # Row 2: 51.9 → 52.5
    (3.2, 51.9, 4.0, 52.5),
    (4.0, 51.9, 4.8, 52.5),
    (4.8, 51.9, 5.6, 52.5),
    (5.6, 51.9, 6.1, 52.5),

    # Row 3: 52.5 → 53.1
    (3.2, 52.5, 4.0, 53.1),
    (4.0, 52.5, 4.8, 53.1),
    (4.8, 52.5, 5.6, 53.1),
    (5.6, 52.5, 6.1, 53.1),
]



@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('static', 'index.html')


@app.route('/api/fetch-incidents', methods=['GET'])
def fetch_incidents():
    """Fetch live incidents - returns basic coordinates immediately"""
    try:
        print("Fetching incidents from all regions...")
        
        # Collect incidents from all regions
        all_incidents = []
        seen_coordinates = set()
        
        for idx, bbox in enumerate(COVERAGE_BOXES, 1):
            bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
            incidents = tomtom_client.fetch_incidents(bbox_str)
            
            for incident in incidents:
                coords = incident['geometry']['coordinates']
                if incident['geometry']['type'] == 'Point':
                    lat, lon = coords[1], coords[0]
                else:  # LineString
                    lat, lon = coords[0][1], coords[0][0]
                
                coord_key = f"{lat:.4f},{lon:.4f}"
                
                if coord_key not in seen_coordinates:
                    seen_coordinates.add(coord_key)
                    incident['source_region'] = idx
                    all_incidents.append(incident)
        
        print(f"Found {len(all_incidents)} unique incidents")
        
        # Return ONLY basic coordinates and IDs for instant display
        basic_incidents = []
        for incident in all_incidents:
            coords = incident['geometry']['coordinates']
            if incident['geometry']['type'] == 'Point':
                lat, lon = coords[1], coords[0]
            else:  # LineString
                lat, lon = coords[0][1], coords[0][0]
            
            basic_incidents.append({
                'id': f"incident_{lat:.4f}_{lon:.4f}",
                'coordinates': {'lat': lat, 'lon': lon},
                'raw_data': incident  # Keep for enrichment
            })
        
        return jsonify({
            'success': True,
            'count': len(basic_incidents),
            'incidents': basic_incidents
        })
        
    except Exception as e:
        print(f"Error fetching incidents: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/enrich-incident/<incident_id>', methods=['POST'])
def enrich_incident(incident_id):
    """Enrich incident with weather, geocoding, and ML predictions"""
    try:
        from flask import request
        incident_data = request.json
        
        if not incident_data:
            return jsonify({'success': False, 'error': 'No incident data'}), 400
        
        lat = incident_data['coordinates']['lat']
        lon = incident_data['coordinates']['lon']
        raw_data = incident_data.get('raw_data', {})
        
        # Get ML-ready features (includes weather, road data)
        features = feature_engine.engineer_features(lat, lon, incident_data=raw_data)
        
        if not features:
            return jsonify({'success': False, 'error': 'Could not extract features'}), 500
        
        # Get ML predictions
        predictions = ml_predictor.predict(features)
        
        # Get readable address using reverse geocoding
        location = tomtom_client.reverse_geocode(lat, lon)
        
        # Calculate risk score based on features
        risk_score = 5
        if features.get('is_night', False):
            risk_score += 2
        if features.get('speed_limit', 50) > 70:
            risk_score += 1
        if features.get('precipitation', 0) > 0:
            risk_score += 1
        if features.get('temperature', 10) < 5:
            risk_score += 1
        risk_score = min(risk_score, 10)
        
        # Determine risk level
        if risk_score >= 7:
            risk_level = "High"
        elif risk_score >= 4:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        enriched_data = {
            'id': incident_id,
            'coordinates': {'lat': lat, 'lon': lon},
            'location': location,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'road_type': features.get('road_type', 'unknown'),
            'speed_limit': features.get('speed_limit', 50),
            'weather': features.get('weather_condition', 'Unknown'),
            'temperature': features.get('temperature', 0),
            'precipitation': features.get('precipitation', 0),
            'wind_speed': features.get('wind_speed', 0),
            'time_period': features.get('time_period', 'Unknown'),
            'is_night': features.get('is_night', False),
            'parties_involved': features.get('aantal_partijen', 2),
            'predictions': predictions,
            'features': features
        }
        
        return jsonify({
            'success': True,
            'incident': enriched_data
        })
        
    except Exception as e:
        print(f"Error enriching incident {incident_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-report/<incident_id>', methods=['POST'])
def generate_report(incident_id):
    """Generate AI report for a specific incident"""
    try:
        from flask import request
        incident_data = request.json
        
        if not incident_data:
            return jsonify({
                'success': False,
                'error': 'No incident data provided'
            }), 400
        
        # Generate AI-powered predictive report
        try:
            ai_report = ai_reporter.generate_report(incident_data)
            return jsonify({
                'success': True,
                'incident_id': incident_id,
                'ai_report': ai_report
            })
        except Exception as e:
            print(f"Error generating AI report for {incident_id}: {e}")
            return jsonify({
                'success': False,
                'incident_id': incident_id,
                'error': str(e)
            }), 500
            
    except Exception as e:
        print(f"Error in generate_report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ml_models_loaded': ml_predictor.is_loaded()
    })


@app.route('/api/config', methods=['GET'])
def config():
    """Provide frontend configuration"""
    import os
    return jsonify({
        'tomtomApiKey': os.getenv('TOMTOM_API_KEY', '')
    })


if __name__ == '__main__':
    print("Starting CrashScope Web Application...")
    print("ML Models loaded:", ml_predictor.is_loaded())
    print("Server running at http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
