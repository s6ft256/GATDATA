from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import firebase_admin
from firebase_admin import credentials, firestore
import os
import io
import base64
import json

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate("path/to/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Sample ML model endpoint
@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        # Get data from request
        data = request.get_json()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Perform prediction (sample implementation)
        # In a real scenario, you would load a pre-trained model
        X = df.drop('target', axis=1, errors='ignore')
        y = df.get('target', pd.Series([0]*len(df)))
        
        # Train a simple model
        model = RandomForestRegressor(n_estimators=100)
        model.fit(X, y)
        
        # Make predictions
        predictions = model.predict(X).tolist()
        
        return jsonify({
            'status': 'success',
            'predictions': predictions
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# Data processing endpoint
@app.route('/api/process', methods=['POST'])
def process_data():
    try:
        # Get data from request
        data = request.get_json()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Perform data cleaning
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        # Basic statistics
        stats = {
            'rows': len(df),
            'columns': len(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.astype(str).to_dict()
        }
        
        # Convert DataFrame back to dict
        processed_data = df.to_dict(orient='records')
        
        return jsonify({
            'status': 'success',
            'data': processed_data,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# Visualization endpoint
@app.route('/api/visualize', methods=['POST'])
def visualize_data():
    try:
        # Get data from request
        data = request.get_json()
        chart_type = data.get('chart_type', 'bar')
        x_column = data.get('x_column')
        y_column = data.get('y_column')
        
        # Convert to DataFrame
        df = pd.DataFrame(data['data'])
        
        # Create visualization based on chart type
        if chart_type == 'bar':
            fig = px.bar(df, x=x_column, y=y_column)
        elif chart_type == 'scatter':
            fig = px.scatter(df, x=x_column, y=y_column)
        elif chart_type == 'line':
            fig = px.line(df, x=x_column, y=y_column)
        else:
            fig = px.bar(df, x=x_column, y=y_column)
        
        # Convert to JSON
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return jsonify({
            'status': 'success',
            'visualization': graphJSON
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# Firestore data upload endpoint
@app.route('/api/upload-to-firestore', methods=['POST'])
def upload_to_firestore():
    try:
        # Get data from request
        data = request.get_json()
        collection_name = data.get('collection_name', 'default_collection')
        
        # Upload data to Firestore
        batch = db.batch()
        for i, record in enumerate(data['records']):
            doc_ref = db.collection(collection_name).document(f'record_{i}')
            batch.set(doc_ref, record)
            
            # Commit batch every 500 records
            if (i + 1) % 500 == 0:
                batch.commit()
                batch = db.batch()
        
        # Commit remaining records
        batch.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Uploaded {len(data["records"])} records to {collection_name}'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Data Processing Backend'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)