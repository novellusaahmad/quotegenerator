from flask import Blueprint, request, jsonify, session, redirect, url_for, flash, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import User, UserRole
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    # At least 8 characters, one uppercase, one lowercase, one digit
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    return True, "Password is valid"

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if not data.get(field):
                if request.is_json:
                    return jsonify({'error': f'{field} is required'}), 400
                else:
                    flash(f'{field.replace("_", " ").title()} is required', 'error')
                    return render_template('register.html')
        
        email = data.get('email').lower().strip()
        password = data.get('password')
        first_name = data.get('first_name').strip()
        last_name = data.get('last_name').strip()
        phone = data.get('phone', '').strip()
        role = data.get('role')
        company_name = data.get('company_name', '').strip()
        
        # Validate email format
        if not validate_email(email):
            error_msg = 'Invalid email format'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            else:
                flash(error_msg, 'error')
                return render_template('register.html')
        
        # Validate password
        is_valid, password_msg = validate_password(password)
        if not is_valid:
            if request.is_json:
                return jsonify({'error': password_msg}), 400
            else:
                flash(password_msg, 'error')
                return render_template('register.html')
        
        # Validate role
        try:
            user_role = UserRole(role)
        except ValueError:
            error_msg = 'Invalid role specified'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            else:
                flash(error_msg, 'error')
                return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            error_msg = 'Email already registered'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            else:
                flash(error_msg, 'error')
                return render_template('register.html')
        
        # Create new user
        try:
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role=user_role,
                company_name=company_name
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Create access token
            access_token = create_access_token(identity=user.id)
            
            if request.is_json:
                return jsonify({
                    'message': 'User created successfully',
                    'access_token': access_token,
                    'user': user.to_dict()
                }), 201
            else:
                session['user_id'] = user.id
                session['access_token'] = access_token
                flash('Registration successful!', 'success')
                return redirect(url_for('main.dashboard'))
                
        except Exception as e:
            db.session.rollback()
            error_msg = 'Registration failed. Please try again.'
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            else:
                flash(error_msg, 'error')
                return render_template('register.html')
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            error_msg = 'Email and password are required'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            else:
                flash(error_msg, 'error')
                return render_template('login.html')
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            error_msg = 'Invalid email or password'
            if request.is_json:
                return jsonify({'error': error_msg}), 401
            else:
                flash(error_msg, 'error')
                return render_template('login.html')
        
        if not user.is_active:
            error_msg = 'Account is deactivated'
            if request.is_json:
                return jsonify({'error': error_msg}), 401
            else:
                flash(error_msg, 'error')
                return render_template('login.html')
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        if request.is_json:
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': user.to_dict()
            }), 200
        else:
            session['user_id'] = user.id
            session['access_token'] = access_token
            flash('Login successful!', 'success')
            
            # Redirect based on role
            if user.role == UserRole.LENDER:
                return redirect(url_for('main.lender_dashboard'))
            else:
                return redirect(url_for('main.dashboard'))
    
    return render_template('login.html')

@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    if request.is_json:
        return jsonify({'message': 'Logged out successfully'}), 200
    else:
        flash('You have been logged out', 'info')
        return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'first_name' in data:
        user.first_name = data['first_name'].strip()
    if 'last_name' in data:
        user.last_name = data['last_name'].strip()
    if 'phone' in data:
        user.phone = data['phone'].strip()
    if 'company_name' in data:
        user.company_name = data['company_name'].strip()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Update failed'}), 500

# Session-based authentication helper
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None
