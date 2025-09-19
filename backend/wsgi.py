"""
WSGI config for the backend API.
This module contains the WSGI application used by Web Server Gateway Interface
compliant servers to serve the application.
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from backend import create_app

# Create the Flask application
application = create_app()

if __name__ == "__main__":
    application.run()