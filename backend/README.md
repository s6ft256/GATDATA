# Backend API

This directory contains the backend API for the Data Ingest Dashboard, providing advanced data processing, machine learning predictions, and API endpoints.

## Tech Stack

- **Flask** for the web server
- **Pandas/Numpy** for data processing
- **Scikit-learn** for machine learning
- **Matplotlib/Seaborn/Plotly** for visualizations
- **Firebase Admin SDK** for Firestore access

## API Endpoints

### Health Check
- `GET /api/v1/health` - Check if the API is running

### Data Processing
- `POST /api/v1/process-data` - Clean and process data
- `POST /api/v1/visualize` - Create visualizations from data

### Machine Learning
- `POST /api/v1/train-model` - Train a machine learning model
- `POST /api/v1/compare-models` - Compare different machine learning models
- `POST /api/v1/predict` - Make predictions using a trained model

### Firebase Integration
- `POST /api/v1/upload-to-firestore` - Upload data to Firestore

For detailed API documentation, see [API_DOCS.md](API_DOCS.md)

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in a `.env` file:
   ```env
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   FIREBASE_CREDENTIALS_PATH=path/to/serviceAccountKey.json
   ```

3. Run the application:
   ```bash
   python -m backend
   ```

## Testing

### Sample Data

We've provided sample data in [sample_data.json](sample_data.json) to help you test the API endpoints.

### Test Scripts

1. **example_client.py**: A simple client that demonstrates how to call the API endpoints
2. **test_with_sample_data.py**: A test script that uses the sample data to test the API

To run the test scripts:
```bash
# Test with example data
python example_client.py

# Test with sample data
python test_with_sample_data.py
```

## Usage

The API will be available at `http://localhost:5000`.

For detailed API documentation, please refer to the main project README.