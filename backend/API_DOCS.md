# API Documentation

## Overview

The backend API provides advanced data processing capabilities including data cleaning, visualization, machine learning, and Firebase integration.

## Base URL

All endpoints are prefixed with `/api/v1`

Example: `http://localhost:5000/api/v1/health`

## Authentication

Currently, the API does not implement authentication. For production use, you should add authentication to protect the endpoints.

## Endpoints

### Health Check

#### `GET /api/v1/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "Data Processing API"
}
```

### Data Processing

#### `POST /api/v1/process-data`

Process and clean data using Pandas and Numpy.

**Request Body:**
```json
{
  "data": [/* array of data records */],
  "clean": true,
  "normalize": true,
  "encode_categorical": true
}
```

**Response:**
```json
{
  "status": "success",
  "data": [/* processed data */],
  "statistics": {
    "shape": [rows, columns],
    "columns": ["column1", "column2"],
    "data_types": {/* data type information */},
    "detected_types": {/* detected data types */},
    "missing_values": {/* missing values count */},
    "missing_percentage": {/* missing values percentage */},
    "duplicates": 0,
    "memory_usage": 12345,
    "numerical_summary": {/* statistical summary for numerical columns */},
    "categorical_summary": {/* summary for categorical columns */}
  }
}
```

### Visualization

#### `POST /api/v1/visualize`

Create visualizations from data.

**Request Body:**
```json
{
  "data": [/* array of data records */],
  "chart_type": "bar", // Options: bar, scatter, line, histogram, heatmap, box
  "x_column": "column_name",
  "y_column": "column_name",
  "title": "Chart Title"
}
```

**Response:**
```json
{
  "status": "success",
  "visualization": "/* JSON representation of the chart */"
}
```

### Machine Learning

#### `POST /api/v1/train-model`

Train a machine learning model.

**Request Body:**
```json
{
  "data": [/* array of data records */],
  "target_column": "target_column_name",
  "model_type": "regression", // Options: regression, classification
  "algorithm": "random_forest", // Options: random_forest, linear, logistic
  "save_model": true,
  "model_path": "path/to/save/model.pkl"
}
```

**Response:**
```json
{
  "status": "success",
  "score": {
    "rmse": 0.5, 
    "r2": 0.85
  }, // For regression
  // OR
  "score": {
    "accuracy": 0.95
  }, // For classification
  "model_type": "regression",
  "algorithm": "random_forest"
}
```

#### `POST /api/v1/compare-models`

Compare different machine learning models.

**Request Body:**
```json
{
  "data": [/* array of data records */],
  "target_column": "target_column_name",
  "model_type": "regression" // Options: regression, classification
}
```

**Response:**
```json
{
  "status": "success",
  "comparison": {
    "scores": [
      ["Random Forest", 0.85],
      ["Linear Regression", 0.75]
    ],
    "best_model": "Random Forest",
    "best_score": 0.85
  }
}
```

#### `POST /api/v1/predict`

Make predictions using a trained model.

**Request Body:**
```json
{
  "data": [/* array of data records */],
  "model_path": "path/to/saved/model.pkl"
}
```

**Response:**
```json
{
  "status": "success",
  "predictions": [/* array of predictions */]
}
```

### Firebase Integration

#### `POST /api/v1/upload-to-firestore`

Upload data to Firestore.

**Request Body:**
```json
{
  "data": [/* array of data records */],
  "collection_name": "collection_name",
  "credentials_path": "path/to/firebase/credentials.json"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Uploaded X records to collection_name"
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `500`: Internal Server Error

Error responses follow this format:
```json
{
  "status": "error",
  "message": "Description of the error"
}
```