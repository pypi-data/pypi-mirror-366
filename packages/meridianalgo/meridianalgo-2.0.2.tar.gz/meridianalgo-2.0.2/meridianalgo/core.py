"""
Core Ara AI functionality - main prediction engine with ensemble ML system
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from pathlib import Path

from .models import EnsembleMLSystem
from .data import MarketDataManager, TechnicalIndicators
from .utils import GPUManager, CacheManager, AccuracyTracker
from .console import ConsoleManager

class AraAI:
    """
    Main Ara AI class with enhanced ensemble ML system and intelligent caching
    """
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.console = ConsoleManager(verbose=verbose)
        self.gpu_manager = GPUManager()
        self.cache_manager = CacheManager()
        self.accuracy_tracker = AccuracyTracker()
        self.data_manager = MarketDataManager()
        self.indicators = TechnicalIndicators()
        self.ml_system = EnsembleMLSystem(device=self.gpu_manager.get_device())
        
        # Initialize system
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the Ara AI system"""
        if self.verbose:
            self.console.print_system_info()
            self.console.print_gpu_info(self.gpu_manager.detect_gpu_vendor())
    
    def predict(self, symbol, days=5, use_cache=True):
        """
        Main prediction function with intelligent caching
        
        Args:
            symbol (str): Stock symbol
            days (int): Number of days to predict
            use_cache (bool): Whether to use cached predictions
            
        Returns:
            dict: Prediction results
        """
        try:
            # Check for existing predictions
            if use_cache:
                cached_result = self.cache_manager.check_cached_predictions(symbol, days)
                if cached_result:
                    choice = self.cache_manager.ask_user_choice(symbol, cached_result)
                    if choice == "use_cached":
                        return self._format_cached_result(cached_result)
            
            # Generate new predictions
            return self._generate_new_predictions(symbol, days)
            
        except Exception as e:
            self.console.print_error(f"Prediction failed for {symbol}: {e}")
            return None
    
    def _generate_new_predictions(self, symbol, days):
        """Generate new predictions using ensemble ML system"""
        try:
            # Get market data
            data = self.data_manager.get_stock_data(symbol)
            if data is None or data.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Calculate technical indicators
            enhanced_data = self.indicators.calculate_all_indicators(data)
            
            # Prepare features for ML models
            features = self._prepare_features(enhanced_data)
            
            # Generate predictions using ensemble system
            predictions = self.ml_system.predict(features, days=days)
            
            # Save predictions to cache
            result = self._format_prediction_result(symbol, predictions, data)
            self.cache_manager.save_predictions(symbol, result)
            
            # Update online learning
            self._update_online_learning(symbol, predictions, data)
            
            return result
            
        except Exception as e:
            self.console.print_error(f"Error generating predictions: {e}")
            return None
    
    def _prepare_features(self, data):
        """Prepare features for ML models"""
        try:
            # Select relevant features for prediction
            feature_columns = [
                'Close', 'Volume', 'High', 'Low', 'Open',
                'SMA_20', 'SMA_50', 'EMA_12', 'EMA_26',
                'RSI', 'MACD', 'MACD_Signal', 'BB_Upper', 'BB_Lower',
                'Stoch_K', 'Stoch_D', 'Williams_R', 'CCI',
                'ATR', 'OBV', 'Price_Change', 'Volume_Change'
            ]
            
            # Filter available columns
            available_columns = [col for col in feature_columns if col in data.columns]
            features = data[available_columns].fillna(method='ffill').fillna(0)
            
            return features.values
            
        except Exception as e:
            self.console.print_error(f"Error preparing features: {e}")
            return None
    
    def _format_prediction_result(self, symbol, predictions, data):
        """Format prediction results"""
        try:
            current_price = data['Close'].iloc[-1]
            result = {
                'symbol': symbol,
                'current_price': current_price,
                'predictions': [],
                'timestamp': datetime.now().isoformat(),
                'model_info': self.ml_system.get_model_info()
            }
            
            for i, pred_price in enumerate(predictions):
                pred_date = datetime.now() + timedelta(days=i+1)
                change = pred_price - current_price
                change_pct = (change / current_price) * 100
                
                result['predictions'].append({
                    'day': i + 1,
                    'date': pred_date.isoformat(),
                    'predicted_price': float(pred_price),
                    'change': float(change),
                    'change_pct': float(change_pct)
                })
            
            return result
            
        except Exception as e:
            self.console.print_error(f"Error formatting results: {e}")
            return None
    
    def _format_cached_result(self, cached_data):
        """Format cached prediction results"""
        try:
            # Convert cached data to standard format
            return {
                'symbol': cached_data['symbol'],
                'current_price': cached_data.get('current_price', 0),
                'predictions': cached_data.get('predictions', []),
                'timestamp': cached_data.get('timestamp'),
                'cached': True,
                'cache_age': self._calculate_cache_age(cached_data.get('timestamp'))
            }
        except Exception as e:
            self.console.print_error(f"Error formatting cached result: {e}")
            return None
    
    def _calculate_cache_age(self, timestamp_str):
        """Calculate age of cached data"""
        try:
            if not timestamp_str:
                return "Unknown"
            
            timestamp = datetime.fromisoformat(timestamp_str)
            age = datetime.now() - timestamp
            
            if age.days > 0:
                return f"{age.days}d {age.seconds // 3600}h"
            else:
                return f"{age.seconds // 3600}h {(age.seconds % 3600) // 60}m"
                
        except Exception:
            return "Unknown"
    
    def _update_online_learning(self, symbol, predictions, data):
        """Update online learning system"""
        try:
            current_price = data['Close'].iloc[-1]
            validation_summary = self.accuracy_tracker.validate_predictions()
            
            learning_data = {
                'symbol': symbol,
                'prediction': predictions[0] if predictions else current_price,
                'actual_price': current_price,
                'timestamp': datetime.now().isoformat(),
                'validation_summary': validation_summary
            }
            
            # Update ML system with learning data
            self.ml_system.update_online_learning(learning_data)
            
        except Exception as e:
            if self.verbose:
                self.console.print_error(f"Online learning update failed: {e}")
    
    def analyze_accuracy(self, symbol=None):
        """Analyze prediction accuracy"""
        return self.accuracy_tracker.analyze_accuracy(symbol)
    
    def validate_predictions(self):
        """Validate and cleanup old predictions"""
        return self.accuracy_tracker.validate_predictions()
    
    def get_system_info(self):
        """Get system information"""
        return {
            'gpu_info': self.gpu_manager.detect_gpu_vendor(),
            'device': str(self.gpu_manager.get_device()),
            'model_info': self.ml_system.get_model_info(),
            'cache_stats': self.cache_manager.get_cache_stats(),
            'accuracy_stats': self.accuracy_tracker.get_accuracy_stats()
        }

class StockPredictor:
    """Simplified interface for stock prediction (backward compatibility)"""
    
    def __init__(self, verbose=False):
        self.ara = AraAI(verbose=verbose)
    
    def predict(self, symbol, days=5):
        """Predict stock prices"""
        return self.ara.predict(symbol, days=days)
    
    def analyze(self, symbol):
        """Analyze stock with technical indicators"""
        return self.ara.data_manager.get_stock_analysis(symbol)

# Convenience functions for backward compatibility
def predict_stock(symbol, days=5, verbose=False):
    """
    Predict stock prices using Ara AI ensemble system
    
    Args:
        symbol (str): Stock symbol
        days (int): Number of days to predict
        verbose (bool): Enable verbose output
        
    Returns:
        dict: Prediction results
    """
    ara = AraAI(verbose=verbose)
    return ara.predict(symbol, days=days)

def analyze_stock(symbol, verbose=False):
    """
    Analyze stock with technical indicators
    
    Args:
        symbol (str): Stock symbol
        verbose (bool): Enable verbose output
        
    Returns:
        dict: Analysis results
    """
    ara = AraAI(verbose=verbose)
    return ara.data_manager.get_stock_analysis(symbol)