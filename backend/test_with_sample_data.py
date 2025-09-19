import requests
import json

# Load sample data
with open('sample_data.json', 'r') as f:
    sample_data = json.load(f)

# Base URL for the API
BASE_URL = "http://localhost:5000/api/v1"

def test_data_processing():
    """Test the data processing endpoint with sample data"""
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
    """Test the visualization endpoint with sample data"""
    payload = {
        "data": sample_data,
        "chart_type": "bar",
        "x_column": "department",
        "y_column": "salary",
        "title": "Average Salary by Department"
    }
    
    response = requests.post(f"{BASE_URL}/visualize", json=payload)
    print("Visualization Response:")
    print(json.dumps(response.json(), indent=2))
    print()

if __name__ == "__main__":
    print("Testing Backend API with Sample Data")
    print("=" * 40)
    
    try:
        test_data_processing()
        test_visualization()
        print("All tests completed successfully!")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the backend server. Make sure it's running at http://localhost:5000")
    except Exception as e:
        print(f"Error: {e}")