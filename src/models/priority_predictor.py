"""Severity prediction model - Production Implementation"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Optional, List
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import xgboost as xgb
import pickle
from pathlib import Path


class PriorityPredictor:
    """
    Predicts record severity (Critical, High, Medium, Low)
    
    Uses severity-specific features and priority score predictions
    Implements both classification and regression approaches
    """
    
    def __init__(self, model_type: str = 'xgboost', random_state: int = 42):
        self.model_type = model_type
        self.random_state = random_state
        self.model = None
        self.priority_regressor = None
        self.severity_classes = ['critical', 'high', 'medium', 'low', 'none']
        self.feature_importance = {}
        self.is_trained = False
    
    def build_model(self):
        """Build severity prediction model"""
        
        print(f"Building {self.model_type} severity predictor...")
        
        if self.model_type == 'xgboost':
            # XGBoost for multi-class classification
            self.model = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                gamma=0.1,
                reg_alpha=0.1,
                reg_lambda=1.0,
                objective='multi:softprob',
                random_state=self.random_state,
                n_jobs=-1,
                verbosity=0
            )
            
            # XGBoost regressor for priority score
            self.priority_regressor = xgb.XGBRegressor(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                gamma=0.1,
                reg_alpha=0.1,
                reg_lambda=1.0,
                objective='reg:squarederror',
                random_state=self.random_state,
                n_jobs=-1,
                verbosity=0
            )
            
        elif self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=12,
                min_samples_split=5,
                min_samples_leaf=2,
                class_weight='balanced',
                random_state=self.random_state,
                n_jobs=-1,
                verbose=0
            )
            
            # Random Forest regressor for priority
            from sklearn.ensemble import RandomForestRegressor
            self.priority_regressor = RandomForestRegressor(
                n_estimators=200,
                max_depth=12,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=self.random_state,
                n_jobs=-1,
                verbose=0
            )
        
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        print(f"✓ Built {self.model_type} models")
    
    def train(self, X: pd.DataFrame, y_severity: pd.Series, 
              y_priority: Optional[pd.Series] = None,
              test_size: float = 0.2,
              perform_cv: bool = True) -> Dict:
        """
        Train severity prediction models
        
        Args:
            X: Feature dataframe
            y_severity: Severity labels (critical, high, medium, low, none)
            y_priority: priority scores (optional, for regression)
            test_size: Test set proportion
            perform_cv: Whether to perform cross-validation
            
        Returns:
            Dictionary with training metrics
        """
        
        print(f"\nTraining PriorityPredictor on {len(X)} samples...")
        
        # Build model if not built
        if self.model is None:
            self.build_model()
        
        # Split data
        if y_priority is not None:
            X_train, X_test, y_sev_train, y_sev_test, y_priority_train, y_priority_test = train_test_split(
                X, y_severity, y_priority,
                test_size=test_size,
                random_state=self.random_state,
                stratify=y_severity
            )
        else:
            X_train, X_test, y_sev_train, y_sev_test = train_test_split(
                X, y_severity,
                test_size=test_size,
                random_state=self.random_state,
                stratify=y_severity
            )
            y_priority_train = None
            y_priority_test = None
        
        print(f"Train set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        results = {}
        
        # Train severity classifier
        print("\n" + "="*60)
        print("Training Severity Classifier...")
        print("="*60)
        
        self.model.fit(X_train, y_sev_train)
        
        # Predictions
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)
        
        # Scores
        train_acc = accuracy_score(y_sev_train, y_train_pred)
        test_acc = accuracy_score(y_sev_test, y_test_pred)
        train_f1 = f1_score(y_sev_train, y_train_pred, average='weighted')
        test_f1 = f1_score(y_sev_test, y_test_pred, average='weighted')
        
        print(f"Train Accuracy: {train_acc:.4f} | F1: {train_f1:.4f}")
        print(f"Test Accuracy:  {test_acc:.4f} | F1: {test_f1:.4f}")
        
        # Cross-validation
        cv_scores = None
        if perform_cv:
            print("Performing 5-fold cross-validation...")
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=self.random_state)
            cv_scores = cross_val_score(
                self.model, X_train, y_sev_train,
                cv=cv,
                scoring='f1_weighted',
                n_jobs=-1
            )
            print(f"CV F1 Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # Classification report
        report = classification_report(
            y_sev_test, y_test_pred,
            output_dict=True
        )
        
        # Confusion matrix
        conf_matrix = confusion_matrix(y_sev_test, y_test_pred)
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance['severity_classifier'] = dict(zip(
                X.columns,
                self.model.feature_importances_
            ))
        
        results['severity_classifier'] = {
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'train_f1': train_f1,
            'test_f1': test_f1,
            'cv_scores': cv_scores.tolist() if cv_scores is not None else None,
            'cv_mean': cv_scores.mean() if cv_scores is not None else None,
            'cv_std': cv_scores.std() if cv_scores is not None else None,
            'classification_report': report,
            'confusion_matrix': conf_matrix.tolist()
        }
        
        # Train priority regressor if priority scores provided
        if y_priority_train is not None and self.priority_regressor is not None:
            print("\n" + "="*60)
            print("Training priority Score Regressor...")
            print("="*60)
            
            self.priority_regressor.fit(X_train, y_priority_train)
            
            # Predictions
            y_priority_train_pred = self.priority_regressor.predict(X_train)
            y_priority_test_pred = self.priority_regressor.predict(X_test)
            
            # Metrics
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            
            train_mse = mean_squared_error(y_priority_train, y_priority_train_pred)
            test_mse = mean_squared_error(y_priority_test, y_priority_test_pred)
            train_mae = mean_absolute_error(y_priority_train, y_priority_train_pred)
            test_mae = mean_absolute_error(y_priority_test, y_priority_test_pred)
            train_r2 = r2_score(y_priority_train, y_priority_train_pred)
            test_r2 = r2_score(y_priority_test, y_priority_test_pred)
            
            print(f"Train MSE: {train_mse:.4f} | MAE: {train_mae:.4f} | R²: {train_r2:.4f}")
            print(f"Test MSE:  {test_mse:.4f} | MAE: {test_mae:.4f} | R²: {test_r2:.4f}")
            
            # Feature importance
            if hasattr(self.priority_regressor, 'feature_importances_'):
                self.feature_importance['priority_regressor'] = dict(zip(
                    X.columns,
                    self.priority_regressor.feature_importances_
                ))
            
            results['priority_regressor'] = {
                'train_mse': train_mse,
                'test_mse': test_mse,
                'train_mae': train_mae,
                'test_mae': test_mae,
                'train_r2': train_r2,
                'test_r2': test_r2
            }
        
        self.is_trained = True
        
        print("\n✓ PriorityPredictor training complete")
        
        return results
    
    def predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict severity and confidence
        
        Args:
            X: Feature dataframe
            
        Returns:
            Tuple of (severity_predictions, probabilities)
        """
        
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        
        return predictions, probabilities
    
    def predict_priority(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict priority scores
        
        Args:
            X: Feature dataframe
            
        Returns:
            Predicted priority scores (0-10 scale)
        """
        
        if not self.is_trained or self.priority_regressor is None:
            raise ValueError("priority regressor must be trained before prediction")
        
        predictions = self.priority_regressor.predict(X)
        
        # Clip to valid priority range
        predictions = np.clip(predictions, 0.0, 10.0)
        
        return predictions
    
    def predict_with_confidence(self, X: pd.DataFrame) -> List[Dict]:
        """
        Predict severity with detailed confidence information
        
        Args:
            X: Feature dataframe
            
        Returns:
            List of dictionaries with predictions and confidence
        """
        
        severities, probabilities = self.predict(X)
        
        results = []
        
        for i, (severity, probs) in enumerate(zip(severities, probabilities)):
            # Get confidence (max probability)
            confidence = float(np.max(probs))
            
            # Get priority if available
            priority = None
            if self.priority_regressor is not None:
                priority = float(self.predict_priority(X.iloc[[i]])[0])
            
            # Create severity distribution
            severity_dist = dict(zip(
                self.model.classes_,
                [float(p) for p in probs]
            ))
            
            result = {
                'severity': severity,
                'confidence': confidence,
                'priority_score': priority,
                'severity_distribution': severity_dist,
                'confidence_level': self._categorize_confidence(confidence)
            }
            
            results.append(result)
        
        return results
    
    def _categorize_confidence(self, confidence: float) -> str:
        """Categorize confidence level"""
        
        if confidence >= 0.9:
            return 'very_high'
        elif confidence >= 0.7:
            return 'high'
        elif confidence >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    def predict_severity_from_priority(self, priority_score: float) -> str:
        """
        Map priority score to severity category
        
        Args:
            priority_score: priority score (0-10)
            
        Returns:
            Severity category
        """
        
        if priority_score >= 9.0:
            return 'critical'
        elif priority_score >= 7.0:
            return 'high'
        elif priority_score >= 4.0:
            return 'medium'
        elif priority_score > 0.0:
            return 'low'
        else:
            return 'none'
    
    def get_feature_importance(self, top_n: int = 20, 
                               model_name: str = 'severity_classifier') -> pd.DataFrame:
        """
        Get top N most important features
        
        Args:
            top_n: Number of top features
            model_name: 'severity_classifier' or 'priority_regressor'
            
        Returns:
            DataFrame with features and importance
        """
        
        if model_name not in self.feature_importance:
            raise ValueError(f"Feature importance not available for {model_name}")
        
        importance_dict = self.feature_importance[model_name]
        
        sorted_features = sorted(
            importance_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        return pd.DataFrame(sorted_features, columns=['Feature', 'Importance'])
    
    def save(self, filepath: str):
        """Save trained model"""
        
        save_path = Path(filepath)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            'model': self.model,
            'priority_regressor': self.priority_regressor,
            'feature_importance': self.feature_importance,
            'severity_classes': self.severity_classes,
            'is_trained': self.is_trained,
            'model_type': self.model_type,
            'random_state': self.random_state
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(state, f)
        
        print(f"Saved PriorityPredictor to {filepath}")
    
    @classmethod
    def load(cls, filepath: str):
        """Load trained model"""
        
        with open(filepath, 'rb') as f:
            state = pickle.load(f)
        
        predictor = cls(
            model_type=state['model_type'],
            random_state=state['random_state']
        )
        
        predictor.model = state['model']
        predictor.priority_regressor = state['priority_regressor']
        predictor.feature_importance = state['feature_importance']
        predictor.severity_classes = state['severity_classes']
        predictor.is_trained = state['is_trained']
        
        print(f"Loaded PriorityPredictor from {filepath}")
        
        return predictor
