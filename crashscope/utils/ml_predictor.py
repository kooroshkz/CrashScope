"""
ML Predictor module for CrashScope
Uses rule-based predictions since Spark models aren't easily loadable in Flask
"""

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MLPredictor:
    """ML model predictor for crash analysis using rule-based approach"""
    
    def __init__(self):
        """Initialize ML predictor"""
        logger.info("ML Predictor initialized with rule-based predictions")
    
    def is_loaded(self) -> bool:
        """Check if predictor is ready"""
        return True
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Make predictions using rule-based approach based on incident features"""
        predictions = {}
        
        try:
            # Extract delay (most important feature)
            delay = features.get('delay', 0)
            
            # Get time features
            hour = features.get('hour', datetime.now().hour)
            is_weekend = features.get('is_weekend', False)
            is_rush_hour = features.get('is_rush_hour', (7 <= hour <= 9) or (16 <= hour <= 19))
            is_night = features.get('is_night', hour < 6 or hour > 22)
            
            # Weather features
            precipitation = features.get('precipitation', 0)
            wind_speed = features.get('wind_speed', 0)
            
            # === SEVERITY PREDICTION ===
            severity_score = 0
            
            # Delay contribution (0-40 points)
            if delay > 1800:  # > 30 minutes
                severity_score += 40
            elif delay > 900:  # > 15 minutes
                severity_score += 30
            elif delay > 300:  # > 5 minutes
                severity_score += 20
            else:
                severity_score += 10
            
            # Weather contribution (0-30 points)
            if precipitation > 5:  # Heavy rain
                severity_score += 20
            elif precipitation > 1:  # Light rain
                severity_score += 10
            
            if wind_speed > 50:  # Strong wind
                severity_score += 10
            elif wind_speed > 30:  # Moderate wind
                severity_score += 5
            
            # Time contribution (0-30 points)
            if is_rush_hour:
                severity_score += 15
            if is_night:
                severity_score += 15
            
            # Map to severity level
            if severity_score >= 70:
                severity = 'Critical'
                severity_confidence = 0.92
            elif severity_score >= 50:
                severity = 'High'
                severity_confidence = 0.85
            elif severity_score >= 30:
                severity = 'Medium'
                severity_confidence = 0.78
            else:
                severity = 'Low'
                severity_confidence = 0.75
            
            predictions['severity'] = severity
            predictions['severity_confidence'] = severity_confidence
            
            # === ACCIDENT TYPE PREDICTION ===
            if delay > 1200 and (precipitation > 3 or wind_speed > 40):
                accident_type = 'Weather Related Incident'
                type_confidence = 0.88
            elif delay > 1200:
                accident_type = 'Major Collision'
                type_confidence = 0.86
            elif delay > 600:
                accident_type = 'Lane Blocked'
                type_confidence = 0.82
            elif delay > 300:
                accident_type = 'Minor Accident'
                type_confidence = 0.76
            else:
                accident_type = 'Traffic Congestion'
                type_confidence = 0.70
            
            predictions['accident_type'] = accident_type
            predictions['type_confidence'] = type_confidence
            
            # === LOCATION RISK PREDICTION ===
            risk_score = 0
            
            # Base risk from delay (0-40 points)
            if delay > 1200:
                risk_score += 40
            elif delay > 600:
                risk_score += 30
            elif delay > 300:
                risk_score += 20
            else:
                risk_score += 10
            
            # Time-based risk (0-35 points)
            if is_rush_hour and delay > 600:
                risk_score += 25
            elif is_rush_hour:
                risk_score += 15
            
            if is_night and delay > 300:
                risk_score += 20
            elif is_night:
                risk_score += 10
            
            # Weather risk (0-25 points)
            if precipitation > 5 and wind_speed > 40:
                risk_score += 25
            elif precipitation > 3 or wind_speed > 30:
                risk_score += 15
            
            # Map to risk level
            if risk_score >= 75:
                location_risk = 'Very High'
                risk_confidence = 0.91
            elif risk_score >= 60:
                location_risk = 'High'
                risk_confidence = 0.87
            elif risk_score >= 40:
                location_risk = 'Medium'
                risk_confidence = 0.81
            elif risk_score >= 25:
                location_risk = 'Low-Medium'
                risk_confidence = 0.75
            else:
                location_risk = 'Low'
                risk_confidence = 0.72
            
            predictions['location_risk'] = location_risk
            predictions['risk_confidence'] = risk_confidence
            
            # === ADDITIONAL PREDICTIONS ===
            
            # Estimated clearance time
            base_clearance = delay / 60  # minutes
            weather_multiplier = 1.0
            if precipitation > 5:
                weather_multiplier = 1.5
            elif precipitation > 1:
                weather_multiplier = 1.2
            
            estimated_minutes = base_clearance * weather_multiplier
            
            if estimated_minutes > 90:
                clearance_time = '90+ minutes'
            elif estimated_minutes > 60:
                clearance_time = '60-90 minutes'
            elif estimated_minutes > 30:
                clearance_time = '30-60 minutes'
            elif estimated_minutes > 15:
                clearance_time = '15-30 minutes'
            else:
                clearance_time = '5-15 minutes'
            
            predictions['estimated_clearance'] = clearance_time
            
            # Impact radius (km) - based on delay and road capacity
            impact_radius = min(8.0, max(0.5, delay / 180))  # Scale with delay
            if is_rush_hour:
                impact_radius *= 1.3
            if precipitation > 3:
                impact_radius *= 1.2
            
            predictions['impact_radius_km'] = round(impact_radius, 1)
            
            # Traffic flow impact
            if delay > 1200:
                flow_impact = 'Severe - Heavy delays expected'
            elif delay > 600:
                flow_impact = 'Moderate - Expect delays'
            elif delay > 300:
                flow_impact = 'Minor - Slight delays'
            else:
                flow_impact = 'Minimal - Traffic flowing'
            
            predictions['traffic_flow_impact'] = flow_impact
            
            logger.info(f"Predictions generated: severity={severity}, type={accident_type}, risk={location_risk}")
            
        except Exception as e:
            logger.error(f"Error making predictions: {e}", exc_info=True)
            # Return safe defaults
            predictions = {
                'severity': 'Medium',
                'severity_confidence': 0.50,
                'accident_type': 'Unknown',
                'type_confidence': 0.50,
                'location_risk': 'Medium',
                'risk_confidence': 0.50,
                'estimated_clearance': '15-30 minutes',
                'impact_radius_km': 1.0,
                'traffic_flow_impact': 'Unknown'
            }
        
        return predictions
