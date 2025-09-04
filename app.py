import os
import logging
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# In Replit environment, PostgreSQL is not running locally
# Use the existing cloud database for demonstration, but .env shows local config for deployment
# For actual VM deployment, the install.sh script will set up local PostgreSQL

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///novellus_loans.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

# JWT configuration
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "jwt-secret-string")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

# File upload configuration
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
app.config["UPLOAD_FOLDER"] = "uploads"

# Snowflake configuration placeholder
app.config["SNOWFLAKE_CONFIG"] = None

# Initialize extensions
db = SQLAlchemy(model_class=Base)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
jwt = JWTManager(app)

# Create upload directory
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Import models after db initialization
from models import User, Application, Quote, Document, Payment, Communication

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    db.create_all()
    logging.info("Database tables created")

# Import routes to ensure they are registered when running the app directly
import routes  # noqa: F401
