from flask import Flask
from backend.api.routes import api
from backend.config import Config
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    """
    Create and configure the Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register blueprints
    app.register_blueprint(api, url_prefix=app.config['API_PREFIX'])
    
    # Add CORS headers for development
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # Root endpoint
    @app.route('/')
    def index():
        return {
            'service': 'Data Processing Backend API',
            'version': '1.0.0',
            'description': 'Advanced data processing, ML predictions, and API endpoints',
            'tech_stack': [
                'Flask',
                'Pandas/Numpy',
                'Scikit-learn',
                'Matplotlib/Seaborn/Plotly',
                'Firebase Admin SDK'
            ],
            'endpoints': {
                'health_check': '/api/v1/health',
                'data_processing': '/api/v1/process-data',
                'visualization': '/api/v1/visualize',
                'ml_training': '/api/v1/train-model',
                'ml_comparison': '/api/v1/compare-models',
                'ml_prediction': '/api/v1/predict',
                'firestore_upload': '/api/v1/upload-to-firestore'
            }
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )