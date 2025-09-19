from flask import Blueprint, request, jsonify
import pandas as pd
import json
import logging
from backend.utils.data_processing import clean_data, normalize_data, encode_categorical_data, generate_summary_stats
from backend.utils.visualization import create_bar_chart, create_scatter_plot, create_line_chart, create_histogram, create_heatmap, create_box_plot
from backend.utils.ml_utils import MLModel, evaluate_model, compare_models
from backend.utils.firebase_utils import FirestoreManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
api = Blueprint('api', __name__)

@api.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Data Processing API'
    })

@api.route('/process-data', methods=['POST'])
def process_data():
    """
    Process and clean data
    """
    try:
        # Get data from request
        data = request.get_json()
        
        # Validate input
        if not data or 'data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing data in request'
            }), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(data['data'])
        
        # Apply data processing functions
        if data.get('clean', False):
            df = clean_data(df)
        
        if data.get('normalize', False):
            df = normalize_data(df)
        
        if data.get('encode_categorical', False):
            df = encode_categorical_data(df)
        
        # Generate summary statistics
        stats = generate_summary_stats(df)
        
        # Convert DataFrame back to dict
        processed_data = df.to_dict(orient='records')
        
        return jsonify({
            'status': 'success',
            'data': processed_data,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error in process_data: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/visualize', methods=['POST'])
def visualize_data():
    """
    Create visualizations
    """
    try:
        # Get data from request
        data = request.get_json()
        
        # Validate input
        if not data or 'data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing data in request'
            }), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(data['data'])
        
        # Get visualization parameters
        chart_type = data.get('chart_type', 'bar')
        x_column = data.get('x_column')
        y_column = data.get('y_column')
        
        # Validate required columns for chart types
        if chart_type in ['bar', 'scatter', 'line'] and (not x_column or not y_column):
            return jsonify({
                'status': 'error',
                'message': 'x_column and y_column are required for this chart type'
            }), 400
        
        # Create visualization based on chart type
        if chart_type == 'bar':
            chart_json = create_bar_chart(df, x_column, y_column, data.get('title', 'Bar Chart'))
        elif chart_type == 'scatter':
            chart_json = create_scatter_plot(df, x_column, y_column, data.get('color_column'), data.get('title', 'Scatter Plot'))
        elif chart_type == 'line':
            chart_json = create_line_chart(df, x_column, y_column, data.get('title', 'Line Chart'))
        elif chart_type == 'histogram':
            if not x_column:
                return jsonify({
                    'status': 'error',
                    'message': 'x_column is required for histogram'
                }), 400
            chart_json = create_histogram(df, x_column, data.get('title', 'Histogram'))
        elif chart_type == 'heatmap':
            chart_json = create_heatmap(df, data.get('title', 'Correlation Heatmap'))
        elif chart_type == 'box':
            if not x_column:
                return jsonify({
                    'status': 'error',
                    'message': 'x_column is required for box plot'
                }), 400
            chart_json = create_box_plot(df, x_column, data.get('title', 'Box Plot'))
        else:
            chart_json = create_bar_chart(df, x_column, y_column, data.get('title', 'Bar Chart'))
        
        return jsonify({
            'status': 'success',
            'visualization': chart_json
        })
    except Exception as e:
        logger.error(f"Error in visualize_data: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/train-model', methods=['POST'])
def train_model():
    """
    Train a machine learning model
    """
    try:
        # Get data from request
        data = request.get_json()
        
        # Validate input
        if not data or 'data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing data in request'
            }), 400
            
        if 'target_column' not in data:
            return jsonify({
                'status': 'error',
                'message': 'target_column is required'
            }), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(data['data'])
        
        # Separate features and target
        target_column = data['target_column']
        if target_column not in df.columns:
            return jsonify({
                'status': 'error',
                'message': f'Target column {target_column} not found in data'
            }), 400
            
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Get model parameters
        model_type = data.get('model_type', 'regression')
        algorithm = data.get('algorithm', 'random_forest')
        
        # Create and train model
        model = MLModel(model_type, algorithm)
        score = model.train(X, y)
        
        # Save model (optional)
        if data.get('save_model', False):
            model_path = data.get('model_path', 'model.pkl')
            model.save_model(model_path)
        
        return jsonify({
            'status': 'success',
            'score': score,
            'model_type': model_type,
            'algorithm': algorithm
        })
    except Exception as e:
        logger.error(f"Error in train_model: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/compare-models', methods=['POST'])
def compare_models_endpoint():
    """
    Compare different machine learning models
    """
    try:
        # Get data from request
        data = request.get_json()
        
        # Validate input
        if not data or 'data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing data in request'
            }), 400
            
        if 'target_column' not in data:
            return jsonify({
                'status': 'error',
                'message': 'target_column is required'
            }), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(data['data'])
        
        # Separate features and target
        target_column = data['target_column']
        if target_column not in df.columns:
            return jsonify({
                'status': 'error',
                'message': f'Target column {target_column} not found in data'
            }), 400
            
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Get model parameters
        model_type = data.get('model_type', 'regression')
        
        # Compare models
        comparison_result = compare_models(X, y, model_type)
        
        return jsonify({
            'status': 'success',
            'comparison': comparison_result
        })
    except Exception as e:
        logger.error(f"Error in compare_models_endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/predict', methods=['POST'])
def predict():
    """
    Make predictions using a trained model
    """
    try:
        # Get data from request
        data = request.get_json()
        
        # Validate input
        if not data or 'data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing data in request'
            }), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(data['data'])
        
        # Load model
        model_path = data.get('model_path', 'model.pkl')
        model = MLModel()
        model.load_model(model_path)
        
        # Make predictions
        predictions = model.predict(df).tolist()
        
        return jsonify({
            'status': 'success',
            'predictions': predictions
        })
    except Exception as e:
        logger.error(f"Error in predict: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/upload-to-firestore', methods=['POST'])
def upload_to_firestore():
    """
    Upload data to Firestore
    """
    try:
        # Get data from request
        data = request.get_json()
        
        # Validate input
        if not data or 'data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing data in request'
            }), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(data['data'])
        
        # Initialize Firestore manager
        credentials_path = data.get('credentials_path')
        firestore_manager = FirestoreManager(credentials_path)
        
        # Upload to Firestore
        collection_name = data.get('collection_name', 'default_collection')
        result = firestore_manager.upload_dataframe(df, collection_name)
        
        return jsonify({
            'status': 'success',
            'message': result
        })
    except Exception as e:
        logger.error(f"Error in upload_to_firestore: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500