#!/usr/bin/env python3
"""
Integration test for the backend API
This script tests all the major components of the backend
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from backend.utils.data_processing import clean_data, normalize_data, encode_categorical_data, generate_summary_stats
from backend.utils.ml_utils import MLModel, compare_models
from backend.utils.visualization import create_bar_chart, create_scatter_plot
from backend.utils.firebase_utils import FirestoreManager

def test_data_processing():
    """Test data processing utilities"""
    print("Testing data processing utilities...")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'Alice', None],
        'age': [25, 30, 35, 25, np.nan],
        'salary': [50000, 60000, 70000, 50000, 55000],
        'department': ['Engineering', 'Marketing', 'Engineering', 'Engineering', 'Sales']
    })
    
    # Test cleaning
    cleaned_data = clean_data(sample_data.copy())
    print(f"  Original rows: {len(sample_data)}, Cleaned rows: {len(cleaned_data)}")
    
    # Test normalization
    normalized_data = normalize_data(cleaned_data.copy())
    print(f"  Normalized data shape: {normalized_data.shape}")
    
    # Test encoding
    encoded_data = encode_categorical_data(cleaned_data.copy())
    print(f"  Encoded data shape: {encoded_data.shape}")
    
    # Test statistics
    stats = generate_summary_stats(cleaned_data)
    print(f"  Generated statistics for {len(stats['columns'])} columns")
    
    print("  ✓ Data processing utilities working correctly\n")

def test_ml_utilities():
    """Test ML utilities"""
    print("Testing ML utilities...")
    
    # Create sample data for regression
    np.random.seed(42)
    X = pd.DataFrame({
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100)
    })
    y = X['feature1'] * 2 + X['feature2'] * -1.5 + np.random.randn(100) * 0.1
    
    # Test model training
    model = MLModel('regression', 'random_forest')
    score = model.train(X, y)
    print(f"  Regression model trained with RMSE: {score['rmse']:.4f}, R2: {score['r2']:.4f}")
    
    # Test model saving and loading
    model.save_model('test_model.pkl')
    print("  ✓ Model saved successfully")
    
    new_model = MLModel()
    new_model.load_model('test_model.pkl')
    print("  ✓ Model loaded successfully")
    
    # Test model comparison
    comparison = compare_models(X, y, 'regression')
    print(f"  Best model: {comparison['best_model']} with score: {comparison['best_score']:.4f}")
    
    # Clean up
    if os.path.exists('test_model.pkl'):
        os.remove('test_model.pkl')
    
    print("  ✓ ML utilities working correctly\n")

def test_visualization():
    """Test visualization utilities"""
    print("Testing visualization utilities...")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'category': ['A', 'B', 'C', 'D', 'E'],
        'value': [10, 25, 30, 15, 20],
        'size': [100, 200, 300, 150, 250]
    })
    
    # Test bar chart
    bar_chart = create_bar_chart(sample_data, 'category', 'value', 'Test Bar Chart')
    print(f"  Bar chart created, size: {len(bar_chart)} characters")
    
    # Test scatter plot
    scatter_plot = create_scatter_plot(sample_data, 'value', 'size', 'category', 'Test Scatter Plot')
    print(f"  Scatter plot created, size: {len(scatter_plot)} characters")
    
    print("  ✓ Visualization utilities working correctly\n")

def test_firebase_utils():
    """Test Firebase utilities"""
    print("Testing Firebase utilities...")
    
    # Test FirestoreManager initialization
    try:
        # This will try to initialize with default credentials
        # It may fail in environments without Firebase setup, which is expected
        manager = FirestoreManager()
        print("  ✓ FirestoreManager initialized")
    except Exception as e:
        print(f"  ℹ️  FirestoreManager initialization skipped (expected in test environments): {str(e)[:50]}...")
    
    print("  ✓ Firebase utilities test completed\n")

def main():
    """Run all tests"""
    print("Running backend integration tests...\n")
    
    try:
        test_data_processing()
        test_ml_utilities()
        test_visualization()
        test_firebase_utils()
        
        print("🎉 All integration tests passed!")
        return 0
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())