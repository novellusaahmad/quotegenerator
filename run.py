#!/usr/bin/env python3
"""
Run script for Novellus Loan Management System
Optimized for Replit web preview
"""
import os
import sys
from app import app
import routes  # noqa: F401

if __name__ == "__main__":
    # Get port from environment or default to 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Run the app with proper configuration for Replit
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
        use_reloader=False,
        threaded=True
    )