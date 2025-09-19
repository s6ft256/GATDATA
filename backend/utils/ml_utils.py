import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import cross_val_score
import joblib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLModel:
    def __init__(self, model_type='regression', algorithm='random_forest'):
        self.model_type = model_type
        self.algorithm = algorithm
        self.model = None
        self.is_trained = False
        self.feature_names = None
        
    def _select_model(self):
        """Select the appropriate model based on type and algorithm"""
        if self.model_type == 'regression':
            if self.algorithm == 'random_forest':
                return RandomForestRegressor(n_estimators=100, random_state=42)
            elif self.algorithm == 'linear':
                return LinearRegression()
            else:
                return RandomForestRegressor(n_estimators=100, random_state=42)
        elif self.model_type == 'classification':
            if self.algorithm == 'random_forest':
                return RandomForestClassifier(n_estimators=100, random_state=42)
            elif self.algorithm == 'logistic':
                return LogisticRegression(random_state=42, max_iter=1000)
            else:
                return RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            raise ValueError("Model type must be 'regression' or 'classification'")
        
    def train(self, X, y, test_size=0.2):
        """
        Train the model
        """
        try:
            # Store feature names
            self.feature_names = list(X.columns) if hasattr(X, 'columns') else None
            
            # Split the data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
            
            # Scale the features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Choose model based on type and algorithm
            self.model = self._select_model()
            
            # Train the model
            self.model.fit(X_train_scaled, y_train)
            self.is_trained = True
            
            # Evaluate the model
            y_pred = self.model.predict(X_test_scaled)
            if self.model_type == 'regression':
                # For regression, calculate RMSE and R2 score
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                r2 = r2_score(y_test, y_pred)
                score = {'rmse': rmse, 'r2': r2}
            else:
                # For classification, calculate accuracy
                accuracy = accuracy_score(y_test, y_pred)
                score = {'accuracy': accuracy}
                
            return score
        except Exception as e:
            logger.error(f"Error in train: {str(e)}")
            raise Exception(f"Failed to train model: {str(e)}")
    
    def predict(self, X):
        """
        Make predictions
        """
        if not self.is_trained or self.model is None:
            raise ValueError("Model must be trained before making predictions")
            
        try:
            scaler = StandardScaler()
            # Note: In a real scenario, you would use the same scaler fitted during training
            X_scaled = scaler.fit_transform(X)
            predictions = self.model.predict(X_scaled)
            return predictions
        except Exception as e:
            logger.error(f"Error in predict: {str(e)}")
            raise Exception(f"Failed to make predictions: {str(e)}")
    
    def save_model(self, filepath):
        """
        Save the trained model
        """
        if not self.is_trained or self.model is None:
            raise ValueError("Model must be trained before saving")
            
        try:
            model_data = {
                'model': self.model,
                'model_type': self.model_type,
                'algorithm': self.algorithm,
                'feature_names': self.feature_names,
                'is_trained': self.is_trained
            }
            joblib.dump(model_data, filepath)
        except Exception as e:
            logger.error(f"Error in save_model: {str(e)}")
            raise Exception(f"Failed to save model: {str(e)}")
    
    def load_model(self, filepath):
        """
        Load a trained model
        """
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.model_type = model_data['model_type']
            self.algorithm = model_data['algorithm']
            self.feature_names = model_data['feature_names']
            self.is_trained = model_data['is_trained']
        except Exception as e:
            logger.error(f"Error in load_model: {str(e)}")
            raise Exception(f"Failed to load model: {str(e)}")

def evaluate_model(y_true, y_pred, model_type='regression'):
    """
    Evaluate model performance
    """
    try:
        if model_type == 'regression':
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_true, y_pred)
            return {'mse': mse, 'rmse': rmse, 'r2': r2}
        else:
            accuracy = accuracy_score(y_true, y_pred)
            return {'accuracy': accuracy}
    except Exception as e:
        logger.error(f"Error in evaluate_model: {str(e)}")
        raise Exception(f"Failed to evaluate model: {str(e)}")

def compare_models(X, y, model_type='regression'):
    """
    Compare different models and return the best one
    """
    try:
        models = []
        scores = []
        
        if model_type == 'regression':
            models.append(('Random Forest', RandomForestRegressor(n_estimators=100, random_state=42)))
            models.append(('Linear Regression', LinearRegression()))
        else:
            models.append(('Random Forest', RandomForestClassifier(n_estimators=100, random_state=42)))
            models.append(('Logistic Regression', LogisticRegression(random_state=42, max_iter=1000)))
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale the features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        best_score = -np.inf if model_type == 'regression' else 0
        best_model = None
        best_name = None
        
        for name, model in models:
            # Train the model
            model.fit(X_train_scaled, y_train)
            
            # Evaluate the model
            y_pred = model.predict(X_test_scaled)
            if model_type == 'regression':
                score = r2_score(y_test, y_pred)
            else:
                score = accuracy_score(y_test, y_pred)
            
            scores.append((name, score))
            
            # Update best model
            if (model_type == 'regression' and score > best_score) or (model_type == 'classification' and score > best_score):
                best_score = score
                best_model = model
                best_name = name
        
        return {
            'scores': scores,
            'best_model': best_name,
            'best_score': best_score
        }
    except Exception as e:
        logger.error(f"Error in compare_models: {str(e)}")
        raise Exception(f"Failed to compare models: {str(e)}")