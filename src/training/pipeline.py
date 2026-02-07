"""Training pipeline for ML Pipeline Template models"""

import logging
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime

from ..collectors.data_sources import DataRecord
from ..preprocessing.normalizer import DataNormalizer
from ..preprocessing.deduplicator import Deduplicator
from ..preprocessing.enricher import Enricher
from ..features.feature_engineer import FeatureEngineer


class TrainingPipeline:
    """Complete training pipeline for prediction models"""
    
    def __init__(self, models_dir: str = "data/models"):
        """
        Initialize the training pipeline
        
        Args:
            models_dir: Directory to save trained models
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.normalizer = DataNormalizer()
        self.deduplicator = Deduplicator()
        self.enricher = Enricher()
        self.feature_engineer = FeatureEngineer()
        
        # Storage for processed data
        self.raw_reports = []
        self.processed_reports = []
        self.feature_data = None
        
        # Models
        self.record_model = None
        self.severity_model = None
        self.pattern_detector = None
        
        # Label encoders
        self.label_encoder = None
        self.severity_label_encoder = None
        
        # Setup logging
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # Console handler
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def load_data(self, data_path: str) -> List[DataRecord]:
        """
        Load data records from file
        
        Args:
            data_path: Path to the data file (pickle format)
            
        Returns:
            List of DataRecord objects
        """
        self.logger.info(f"Loading data from {data_path}...")
        
        with open(data_path, 'rb') as f:
            reports = pickle.load(f)
        
        self.raw_reports = reports
        self.logger.info(f"Loaded {len(reports)} reports")
        
        return reports
    
    def preprocess_data(self, reports: List[DataRecord]) -> List[DataRecord]:
        """
        Preprocess data records
        
        Args:
            reports: List of raw DataRecord objects
            
        Returns:
            List of preprocessed reports
        """
        self.logger.info("Preprocessing data...")
        
        # Normalize
        self.logger.info("Normalizing data...")
        normalized = self.normalizer.normalize_reports(reports)
        self.logger.info(f"  -> Normalized: {len(normalized)} reports")
        
        # Deduplicate
        self.logger.info("Removing duplicates...")
        deduplicated = self.deduplicator.remove_duplicates(normalized)
        self.logger.info(f"  -> Deduplicated: {len(deduplicated)} reports")
        
        # Enrich
        self.logger.info("Enriching data...")
        enriched = self.enricher.enrich_reports(deduplicated)
        self.logger.info(f"  -> Enriched: {len(enriched)} reports")
        
        # Filter low quality reports
        self.logger.info("Filtering reports with quality < 0.5...")
        filtered = [
            r for r in enriched 
            if getattr(r, 'quality_score', 1.0) >= 0.5
        ]
        self.logger.info(f"  -> Filtered: {len(filtered)} reports")
        
        self.processed_reports = filtered
        
        return filtered
    
    def engineer_features(self, reports: List[DataRecord]) -> pd.DataFrame:
        """
        Engineer features from preprocessed reports
        
        Args:
            reports: List of preprocessed reports
            
        Returns:
            DataFrame with engineered features
        """
        self.logger.info("Engineering features...")
        
        # Extract features
        feature_data = self.feature_engineer.fit_transform(reports)
        
        # Save feature engineer
        self.feature_engineer.save(self.models_dir / 'feature_engineer.pkl')
        
        self.feature_data = feature_data
        
        return feature_data
    
    def train_record_model(self, feature_data=None):
        """Train the record type classifier"""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report, accuracy_score
        
        self.logger.info("Training record classifier...")
        
        if feature_data is None:
            feature_data = self.feature_data
        
        # Prepare data
        X = feature_data.drop(columns=['record_type_encoded'], errors='ignore')
        
        # Get target from processed reports
        y = [getattr(r, 'record_type', 'Unknown') for r in self.processed_reports]
        
        # Encode target
        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42
        )
        
        # Train model
        self.record_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42,
            n_jobs=-1
        )
        
        self.record_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.record_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        self.logger.info(f"Record classifier accuracy: {accuracy:.3f}")
        
        # Store label encoder
        self.label_encoder = le
        
        return self.record_model
    
    def train_severity_model(self, feature_data=None):
        """Train the severity predictor"""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report, accuracy_score
        
        self.logger.info("Training severity predictor...")
        
        if feature_data is None:
            feature_data = self.feature_data
        
        # Prepare data
        X = feature_data.copy()
        
        # Get target from processed reports
        y = [getattr(r, 'severity', 'medium') for r in self.processed_reports]
        
        # Encode target
        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42
        )
        
        # Train model
        self.severity_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            random_state=42,
            n_jobs=-1
        )
        
        self.severity_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.severity_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        self.logger.info(f"Severity predictor accuracy: {accuracy:.3f}")
        
        # Store label encoder
        self.severity_label_encoder = le
        
        return self.severity_model
    
    def train_pattern_detector(self, reports=None):
        """Train the record chain detector"""
        self.logger.info("Training chain detector...")
        
        if reports is None:
            reports = self.processed_reports
        
        # For now, use a simple heuristic-based detector
        # In production, this would be a more sophisticated model
        
        try:
            from ..models.pattern_detector import PatternDetector
            self.pattern_detector = PatternDetector()
            
            # Train on reports (if the detector has a train method)
            if hasattr(self.pattern_detector, 'train'):
                self.pattern_detector.train(reports)
        except ImportError:
            self.logger.warning("PatternDetector not found, creating placeholder")
            # Create a simple placeholder
            class SimplePatternDetector:
                def detect_chains(self, reports):
                    return []
            
            self.pattern_detector = SimplePatternDetector()
        
        self.logger.info("Chain detector ready")
        
        return self.pattern_detector
    
    def save_models(self):
        """Save all trained models"""
        import pickle
        from pathlib import Path
        
        self.logger.info("Saving models...")
        
        models_dir = Path(self.models_dir)
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Save record classifier
        if hasattr(self, 'record_model') and self.record_model is not None:
            with open(models_dir / 'classifier.pkl', 'wb') as f:
                pickle.dump({
                    'model': self.record_model,
                    'label_encoder': self.label_encoder
                }, f)
            self.logger.info("  -> Saved classifier.pkl")
        
        # Save severity predictor
        if hasattr(self, 'severity_model') and self.severity_model is not None:
            with open(models_dir / 'priority_predictor.pkl', 'wb') as f:
                pickle.dump({
                    'model': self.severity_model,
                    'label_encoder': self.severity_label_encoder
                }, f)
            self.logger.info("  -> Saved priority_predictor.pkl")
        
        # Save chain detector
        if hasattr(self, 'pattern_detector') and self.pattern_detector is not None:
            with open(models_dir / 'pattern_detector.pkl', 'wb') as f:
                pickle.dump(self.pattern_detector, f)
            self.logger.info("  -> Saved pattern_detector.pkl")
        
        self.logger.info(f"All models saved to: {models_dir}")
    
    def train_all(self, reports: List[DataRecord]):
        """
        Complete training pipeline
        
        Args:
            reports: List of raw data records
        """
        # Preprocess
        self.processed_reports = self.preprocess_data(reports)
        
        # Engineer features
        self.feature_data = self.engineer_features(self.processed_reports)
        
        # Train models
        self.train_record_model()
        self.train_severity_model()
        self.train_pattern_detector()
        
        # Save everything
        self.save_models()
        
        self.logger.info("Training complete!")
