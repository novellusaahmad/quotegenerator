#!/usr/bin/env python3
"""
Database initialization script for Novellus Loan Management System
This script creates all database tables and performs initial setup
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with all required tables"""
    try:
        # Add current directory to Python path
        current_dir = Path(__file__).parent.absolute()
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        
        # Import Flask app and database
        from app import app, db
        
        # Create application context
        with app.app_context():
            logger.info("Creating database tables...")
            
            # Import all models to ensure they're registered
            try:
                import models
                logger.info("Models imported successfully")
                
                # Verify critical loan calculator models are available
                from models import LoanSummary, PaymentSchedule, User, Application
                logger.info("Loan calculator storage models verified: LoanSummary, PaymentSchedule")
                
            except ImportError as e:
                logger.warning(f"Could not import models: {e}")
                logger.info("Proceeding with basic table creation...")
            
            # Create all tables
            db.create_all()
            logger.info("Database tables created")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                logger.info(f"Database initialized successfully with tables: {', '.join(sorted(tables))}")
                
                # Specifically verify loan calculator tables
                required_tables = ['loan_summary', 'payment_schedule', 'users']
                missing_tables = [table for table in required_tables if table not in tables]
                
                if missing_tables:
                    logger.warning(f"Missing critical tables: {', '.join(missing_tables)}")
                    return False
                else:
                    logger.info("✓ All loan calculator storage tables created successfully")
                    
            else:
                logger.warning("No tables found after creation - this may indicate a problem")
            
            # Check database connection type
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if 'postgresql' in db_uri:
                logger.info("✓ PostgreSQL database connection confirmed")
            else:
                logger.warning(f"⚠️  Unexpected database type in URI: {db_uri}")
            
            logger.info("Database initialization completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_database_connection():
    """Test database connection and loan calculator storage operations"""
    try:
        from app import app, db
        
        with app.app_context():
            # Test basic database operations
            logger.info("Testing database connection...")
            
            # Execute a simple query
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT 1")).fetchone()
            if result:
                logger.info("✓ Database connection test successful!")
                
                # Test loan calculator storage tables
                try:
                    from models import LoanSummary, PaymentSchedule
                    
                    # Test table access
                    loan_count = LoanSummary.query.count()
                    schedule_count = PaymentSchedule.query.count()
                    
                    logger.info(f"✓ Loan calculator storage operational:")
                    logger.info(f"  - LoanSummary table: {loan_count} records")
                    logger.info(f"  - PaymentSchedule table: {schedule_count} records")
                    
                    return True
                    
                except Exception as storage_error:
                    logger.error(f"Loan calculator storage test failed: {storage_error}")
                    return False
            else:
                logger.error("Database connection test failed - no result returned")
                return False
                
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

def create_required_directories():
    """Create required application directories"""
    directories = [
        'uploads',
        'static/uploads', 
        'instance',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Directory created/verified: {directory}")

def create_default_env():
    """Create default .env file if it doesn't exist"""
    env_path = '.env'
    if not os.path.exists(env_path):
        logger.info("Creating default .env file...")
        env_content = """# Novellus Loan Management System Environment Configuration
SESSION_SECRET=novellus-loan-management-secret-key-2025-change-this-in-production
DATABASE_URL=sqlite:///novellus_loans.db
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
SQLALCHEMY_TRACK_MODIFICATIONS=False
SQLALCHEMY_ENGINE_OPTIONS={"pool_recycle": 300, "pool_pre_ping": True}
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
        logger.info(f"Default .env file created: {env_path}")
    else:
        logger.info(".env file already exists")

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("Novellus Loan Management System - Database Initialization")
    logger.info("Including Loan Calculator Data Storage Setup")
    logger.info("="*60)
    
    # Create required directories
    create_required_directories()
    
    # Create default environment file
    create_default_env()
    
    # Initialize database with loan calculator storage
    if init_database():
        # Test database connection and loan calculator storage
        if test_database_connection():
            logger.info("="*60)
            logger.info("✓ Database setup completed successfully!")
            logger.info("✓ Loan calculator data storage is ready")
            logger.info("✓ System ready to store and retrieve loan calculations")
            logger.info("="*60)
            sys.exit(0)
        else:
            logger.error("Database connection or loan calculator storage test failed")
            sys.exit(1)
    else:
        logger.error("Database initialization failed")
        sys.exit(1)