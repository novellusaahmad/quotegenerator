#!/usr/bin/env python3
import os
import sys

# Set environment variables
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the Flask app
from app import app
import routes

if __name__ == '__main__':
    print("Starting Novellus Loan Calculator...")
    print("Server will be available at http://0.0.0.0:5000")
    
    # Run with Werkzeug development server for better Replit compatibility
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )