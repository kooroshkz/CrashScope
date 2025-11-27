"""
AI-powered incident report generator using OpenRouter LLM
"""

import requests
import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class AIReporter:
    """Generate AI-powered predictive reports for traffic incidents"""
    
    def __init__(self):
        """Initialize AI reporter with OpenRouter API"""
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "nvidia/nemotron-nano-9b-v2:free"
        
    def generate_report(self, incident_data: Dict[str, Any]) -> str:
        """Generate a predictive report for an incident
        
        Args:
            incident_data: Dictionary containing all incident information
            
        Returns:
            Generated report text
        """
        if not self.api_key:
            return self._get_fallback_report(incident_data)
        
        try:
            # Build comprehensive prompt
            prompt = self._build_prompt(incident_data)
            
            # Call OpenRouter API
            response = requests.post(
                url=self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/kooroshkz/CrashScope",
                    "X-Title": "CrashScope Live Traffic Analysis",
                },
                data=json.dumps({
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional traffic safety analyst. Generate a single concise paragraph (3-4 sentences, max 80 words) analyzing the incident. Focus on severity, key risk factors, and one actionable recommendation. Use simple markdown for emphasis (**bold** for key terms)."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 150
                }),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                report = result['choices'][0]['message']['content'].strip()
                logger.info("AI report generated successfully")
                return report
            else:
                logger.error(f"OpenRouter API error: {response.status_code}")
                return self._get_fallback_report(incident_data)
                
        except Exception as e:
            logger.error(f"Error generating AI report: {e}")
            return self._get_fallback_report(incident_data)
    
    def _build_prompt(self, data: Dict[str, Any]) -> str:
        """Build detailed prompt from incident data"""
        pred = data.get('predictions', {})
        
        prompt = f"""Analyze this traffic incident and provide a predictive report:

INCIDENT DETAILS:
- Location: {data.get('location', 'Unknown')}
- Risk Level: {data.get('risk_level', 'Unknown')} (Score: {data.get('risk_score', 'N/A')}/10)
- Road Type: {data.get('road_type', 'unknown')}
- Speed Limit: {data.get('speed_limit', 'N/A')} km/h

WEATHER CONDITIONS:
- Condition: {data.get('weather', 'Unknown')}
- Temperature: {data.get('temperature', 'N/A')}°C
- Precipitation: {data.get('precipitation', 0)} mm
- Wind Speed: {data.get('wind_speed', 'N/A')} km/h
- Lighting: {data.get('time_period', 'Unknown')} ({'Dark' if data.get('is_night') else 'Daylight'})

ML PREDICTIONS:
- Predicted Severity: {pred.get('severity', 'Unknown')} (Confidence: {pred.get('severity_confidence', 0)*100:.1f}%)
- Incident Type: {pred.get('accident_type', 'Unknown')} (Confidence: {pred.get('type_confidence', 0)*100:.1f}%)
- Location Risk: {pred.get('location_risk', 'Unknown')} (Confidence: {pred.get('risk_confidence', 0)*100:.1f}%)
- Estimated Clearance: {pred.get('estimated_clearance', 'Unknown')}
- Impact Radius: {pred.get('impact_radius_km', 'N/A')} km
- Traffic Flow: {pred.get('traffic_flow_impact', 'Unknown')}

In one concise paragraph (3-4 sentences, max 80 words), provide:
- Quick severity assessment and main risk factors
- How weather/time conditions impact safety
- One clear actionable recommendation
Use **bold** for key terms."""

        return prompt
    
    def _get_fallback_report(self, data: Dict[str, Any]) -> str:
        """Generate a fallback report when AI is unavailable"""
        pred = data.get('predictions', {})
        severity = pred.get('severity', 'Medium')
        incident_type = pred.get('accident_type', 'Traffic Incident')
        clearance = pred.get('estimated_clearance', '15-30 minutes')
        
        report = f"""**{severity} severity** {incident_type.lower()} detected in {data.get('location', 'the area')} with {data.get('weather', 'normal').lower()} conditions ({data.get('temperature', 'N/A')}°C). Expected clearance: **{clearance}**. Traffic impact radius: {pred.get('impact_radius_km', 1)} km. Recommendation: Consider alternative routes and adjust speed for conditions."""
        
        return report
