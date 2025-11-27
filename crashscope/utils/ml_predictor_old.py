"""
ML Predictor module for CrashScope
Loads and uses trained ML models for accident predictions
"""

from pathlib import Path
import pickle
import pandas as pd
from typing import Dict, Any, Optional


class MLPredictor:
    """ML model predictor for crash analysis"""
    
    def __init__(self):
        """Initialize ML predictor and load models"""
        self.models_dir = Path(__file__).parent.parent.parent / 'models'
        self.models = {}
        self.indexers = {}
        self._load_models()
    
    def _load_models(self):
        """Load all available ML models"""
        try:
            # Load severity model
            severity_model_path = self.models_dir / 'severity_model' / 'model.pkl'
            if severity_model_path.exists():
                with open(severity_model_path, 'rb') as f:
                    self.models['severity'] = pickle.load(f)
                print("Loaded severity model")
            
            # Load severity indexer
            severity_indexer_path = self.models_dir / 'severity_indexer' / 'indexer.pkl'
            if severity_indexer_path.exists():
                with open(severity_indexer_path, 'rb') as f:
                    self.indexers['severity'] = pickle.load(f)
                print("Loaded severity indexer")
            
            # Load accident type model
            type_model_path = self.models_dir / 'accident_type_model' / 'model.pkl'
            if type_model_path.exists():
                with open(type_model_path, 'rb') as f:
                    self.models['type'] = pickle.load(f)
                print("Loaded accident type model")
            
            # Load type indexer
            type_indexer_path = self.models_dir / 'type_indexer' / 'indexer.pkl'
            if type_indexer_path.exists():
                with open(type_indexer_path, 'rb') as f:
                    self.indexers['type'] = pickle.load(f)
                print("Loaded type indexer")
            
            # Load location risk model
            location_risk_path = self.models_dir / 'location_risk_model' / 'model.pkl'
            if location_risk_path.exists():
                with open(location_risk_path, 'rb') as f:
                    self.models['location_risk'] = pickle.load(f)
                print("Loaded location risk model")
                
        except Exception as e:
            print(f"Warning: Error loading ML models: {e}")
    
    def is_loaded(self) -> bool:
        """Check if models are loaded"""
        return len(self.models) > 0
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Make predictions using loaded models"""
        predictions = {
            'severity': None,
            'severity_confidence': None,
            'accident_type': None,
            'type_confidence': None,
            'location_risk': None,
            'risk_confidence': None
        }
        
        if not self.is_loaded():
            return predictions
        
        try:
            # Prepare feature dataframe
            feature_cols = [
                'temperature', 'precipitation', 'wind_speed', 'weather_code',
                'hour', 'day_of_week', 'month', 'is_weekend', 'is_rush_hour', 
                'is_night', 'speed_limit', 'lanes', 'lat', 'lon'
            ]
            
            # Extract relevant features
            df_features = {}
            for col in feature_cols:
                df_features[col] = features.get(col, 0)
            
            df = pd.DataFrame([df_features])
            
            # Predict severity
            if 'severity' in self.models:
                try:
                    severity_pred = self.models['severity'].predict(df)
                    severity_proba = self.models['severity'].predict_proba(df)
                    
                    if 'severity' in self.indexers:
                        severity_label = self.indexers['severity'].inverse_transform(severity_pred)[0]
                        predictions['severity'] = severity_label
                        predictions['severity_confidence'] = float(max(severity_proba[0]))
                    else:
                        predictions['severity'] = int(severity_pred[0])
                        predictions['severity_confidence'] = float(max(severity_proba[0]))
                except Exception as e:
                    print(f"Severity prediction error: {e}")
            
            # Predict accident type
            if 'type' in self.models:
                try:
                    type_pred = self.models['type'].predict(df)
                    type_proba = self.models['type'].predict_proba(df)
                    
                    if 'type' in self.indexers:
                        type_label = self.indexers['type'].inverse_transform(type_pred)[0]
                        predictions['accident_type'] = type_label
                        predictions['type_confidence'] = float(max(type_proba[0]))
                    else:
                        predictions['accident_type'] = int(type_pred[0])
                        predictions['type_confidence'] = float(max(type_proba[0]))
                except Exception as e:
                    print(f"Type prediction error: {e}")
            
            # Predict location risk
            if 'location_risk' in self.models:
                try:
                    risk_pred = self.models['location_risk'].predict(df)
                    risk_proba = self.models['location_risk'].predict_proba(df)
                    
                    predictions['location_risk'] = float(risk_pred[0])
                    predictions['risk_confidence'] = float(max(risk_proba[0]))
                except Exception as e:
                    print(f"Location risk prediction error: {e}")
                    
        except Exception as e:
            print(f"Error making predictions: {e}")
        
        return predictions
