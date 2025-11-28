"""
ML Predictor module for CrashScope
Uses trained scikit-learn models exclusively - NO fallback logic
"""

import logging
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MLPredictor:
    """ML model predictor for crash analysis using trained scikit-learn models"""
    
    def __init__(self, model_dir: Optional[str] = None):
        """
        Initialize ML predictor with trained models
        
        Args:
            model_dir: Path to directory containing trained models (defaults to models_sklearn/)
            
        Raises:
            FileNotFoundError: If model files are not found
            Exception: If models cannot be loaded
        """
        if model_dir is None:
            model_dir = Path(__file__).parent.parent.parent / "models_sklearn"
        else:
            model_dir = Path(model_dir)
            
        self.model_dir = model_dir
        
        # Load trained models (will raise exception if models don't exist)
        self._load_models()
        logger.info(f"✓ ML models loaded successfully from {model_dir}")
    
    def _load_models(self):
        """
        Load all trained models and encoders
        
        Raises:
            FileNotFoundError: If any model file is missing
        """
        model_files = {
            'severity_model': self.model_dir / "severity_model.pkl",
            'severity_encoder': self.model_dir / "severity_encoder.pkl",
            'accident_type_model': self.model_dir / "accident_type_model.pkl",
            'accident_type_encoder': self.model_dir / "accident_type_encoder.pkl",
            'location_risk_model': self.model_dir / "location_risk_model.pkl",
            'location_risk_encoder': self.model_dir / "location_risk_encoder.pkl",
            'feature_names': self.model_dir / "feature_names.pkl"
        }
        
        # Check all files exist
        missing_files = [name for name, path in model_files.items() if not path.exists()]
        if missing_files:
            raise FileNotFoundError(
                f"Missing model files: {missing_files}. "
                f"Please run notebooks/4-TrainSklearn.ipynb to train models."
            )
        
        # Load severity model
        self.severity_model = joblib.load(model_files['severity_model'])
        self.severity_encoder = joblib.load(model_files['severity_encoder'])
        
        # Load accident type model
        self.accident_type_model = joblib.load(model_files['accident_type_model'])
        self.accident_type_encoder = joblib.load(model_files['accident_type_encoder'])
        
        # Load location risk model
        self.location_risk_model = joblib.load(model_files['location_risk_model'])
        self.location_risk_encoder = joblib.load(model_files['location_risk_encoder'])
        
        # Load feature names
        self.feature_names = joblib.load(model_files['feature_names'])
        
        logger.info(f"Loaded models with {len(self.feature_names)} features")
        logger.info(f"Severity classes: {self.severity_encoder.classes_.tolist()}")
        logger.info(f"Accident type classes: {self.accident_type_encoder.classes_.tolist()}")
        logger.info(f"Location risk classes: {self.location_risk_encoder.classes_.tolist()}")
    
    def _prepare_features(self, features: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert feature dictionary to model input DataFrame
        
        Args:
            features: Dictionary of engineered features
            
        Returns:
            DataFrame with features in correct order and format
        """
        # Create feature dict matching training feature order
        feature_dict = {}
        for feature_name in self.feature_names:
            feature_dict[feature_name] = features.get(feature_name, 0)
        
        # Convert to DataFrame to preserve feature names
        return pd.DataFrame([feature_dict], columns=self.feature_names)
    
    def _translate_to_english(self, dutch_text: str, category: str) -> str:
        """
        Translate Dutch model outputs to English
        
        Args:
            dutch_text: Dutch text from model
            category: Type of prediction (severity, accident_type, location_risk)
            
        Returns:
            English translation
        """
        translations = {
            'severity': {
                'Dodelijk': 'Fatal',
                'Letsel': 'Injury',
                'Uitsluitend materiele schade': 'Property Damage Only'
            },
            'accident_type': {
                'Dier': 'Animal',
                'Eenzijdig': 'Single-vehicle',
                'Flank': 'Side collision',
                'Frontaal': 'Head-on',
                'Geparkeerd voertuig': 'Parked vehicle',
                'Kop/staart': 'Rear-end',
                'Los voorwerp': 'Loose object',
                'Onbekend': 'Unknown',
                'Vast voorwerp': 'Fixed object',
                'Voetganger': 'Pedestrian'
            },
            'location_risk': {
                'Binnen': 'Urban',
                'Buiten': 'Rural'
            }
        }
        
        return translations.get(category, {}).get(dutch_text, dutch_text)
    
    def is_loaded(self) -> bool:
        """Check if models are loaded (always True if constructor succeeded)"""
        return True
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make predictions using trained ML models
        
        Args:
            features: Dictionary of engineered features
            
        Returns:
            Dictionary with predictions and confidence scores:
            - severity: Predicted severity level
            - severity_confidence: Model confidence for severity
            - accident_type: Predicted accident type
            - type_confidence: Model confidence for accident type
            - location_risk: Predicted location risk level
            - risk_confidence: Model confidence for location risk
            
        Raises:
            Exception: If prediction fails
        """
        # Prepare features
        X = self._prepare_features(features)
        
        # Predict severity
        severity_pred = self.severity_model.predict(X)[0]
        severity_proba = self.severity_model.predict_proba(X)[0]
        severity_dutch = self.severity_encoder.inverse_transform([severity_pred])[0]
        severity = self._translate_to_english(severity_dutch, 'severity')
        severity_confidence = float(np.max(severity_proba))
        
        # Predict accident type
        type_pred = self.accident_type_model.predict(X)[0]
        type_proba = self.accident_type_model.predict_proba(X)[0]
        accident_type_dutch = self.accident_type_encoder.inverse_transform([type_pred])[0]
        accident_type = self._translate_to_english(accident_type_dutch, 'accident_type')
        type_confidence = float(np.max(type_proba))
        
        # Predict location risk
        risk_pred = self.location_risk_model.predict(X)[0]
        risk_proba = self.location_risk_model.predict_proba(X)[0]
        location_risk_dutch = self.location_risk_encoder.inverse_transform([risk_pred])[0]
        location_risk = self._translate_to_english(location_risk_dutch, 'location_risk')
        risk_confidence = float(np.max(risk_proba))
        
        logger.debug(f"ML Predictions - Severity: {severity} ({severity_confidence:.2%}), "
                    f"Type: {accident_type} ({type_confidence:.2%}), "
                    f"Risk: {location_risk} ({risk_confidence:.2%})")
        
        return {
            'severity': severity,
            'severity_confidence': severity_confidence,
            'accident_type': accident_type,
            'type_confidence': type_confidence,
            'location_risk': location_risk,
            'risk_confidence': risk_confidence
        }
