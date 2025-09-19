import requests
import pandas as pd
import json

# Base URL for the API
BASE_URL = "http://localhost:5000/api/v1"

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check Response:")
    print(json.dumps(response.json(), indent=2))
    print()

def test_data_processing():
    """Test the data processing endpoint"""
    # Sample data
    sample_data = [
        {"name": "John", "age": 30, "salary": 50000},
        {"name": "Jane", "age": 25, "salary": 60000},
        {"name": "Bob", "age": 35, "salary": 70000},
        {"name": "Alice", "age": 28, "salary": 55000}
    ]
    
    payload = {
        "data": sample_data,
        "clean": True,
        "normalize": False,
        "encode_categorical": False
    }
    
    response = requests.post(f"{BASE_URL}/process-data", json=payload)
    print("Data Processing Response:")
    print(json.dumps(response.json(), indent=2))
    print()

def test_visualization():
    """Test the visualization endpoint"""
    # Sample data
    sample_data = [
        {"category": "A", "value": 10},
        {"category": "B", "value": 20},
        {"category": "C", "value": 15},
        {"category": "D", "value": 25}
    ]
    
    payload = {
        "data": sample_data,
        "chart_type": "bar",
        "x_column": "category",
        "y_column": "value",
        "title": "Sample Bar Chart"
    }
    
    response = requests.post(f"{BASE_URL}/visualize", json=payload)
    print("Visualization Response:")
    print(json.dumps(response.json(), indent=2))
    print()

if __name__ == "__main__":
    print("Testing Backend API Endpoints")
    print("=" * 40)
    
    try:
        test_health_check()
        test_data_processing()
        test_visualization()
        print("All tests completed successfully!")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the backend server. Make sure it's running at http://localhost:5000")
    except Exception as e:
        print(f"Error: {e}")