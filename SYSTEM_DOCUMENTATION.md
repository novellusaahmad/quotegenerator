# Novellus Loan Management System - Complete Documentation Guide

## Table of Contents
1. [System Overview](#system-overview)
2. [File Structure and Architecture](#file-structure-and-architecture)
3. [Loan Calculation Engine](#loan-calculation-engine)
4. [Visual Interface Components](#visual-interface-components)
5. [Charts and Data Visualization](#charts-and-data-visualization)
6. [Reports and Document Generation](#reports-and-document-generation)
7. [Database Schema and Models](#database-schema-and-models)
8. [Authentication and User Management](#authentication-and-user-management)
9. [Configuration and Deployment](#configuration-and-deployment)
10. [Customization Guide](#customization-guide)
11. [Troubleshooting](#troubleshooting)

---

## System Overview

The Novellus Loan Management System is a comprehensive Flask-based web application designed for managing complex financial loan calculations and applications. The system supports three main loan types:

- **Bridge Loans**: Short-term financing with various repayment options
- **Term Loans**: Long-term financing with interest-only or amortizing payments
- **Development Loans**: Multi-tranche financing for property development projects

### Key Features
- Dual authentication system (session-based and JWT)
- Role-based access control (borrowers vs lenders)
- Precise decimal-based financial calculations
- Multi-currency support (GBP/EUR)
- Payment timing options (advance/arrears)
- Payment frequency options (monthly/quarterly)
- Professional document generation (PDF/Excel)
- Interactive charts and payment schedules
- Responsive design with Novellus branding

---

## File Structure and Architecture

### Core Application Files

#### `main.py`
- **Purpose**: Application entry point
- **Contents**: Imports the Flask app instance
- **Modifications**: Rarely needs changes unless changing the app structure

#### `app.py`
- **Purpose**: Flask application configuration and database setup
- **Key Components**:
  - Flask app initialization
  - Database configuration (PostgreSQL/SQLite)
  - SQLAlchemy setup
  - Session management
- **To Modify**: Database settings, app configuration, middleware

#### `models.py`
- **Purpose**: Database schema definitions using SQLAlchemy ORM
- **Key Models**:
  - `User`: User accounts and authentication
  - `LoanApplication`: Loan application data
  - `Quote`: Generated loan quotes
  - `Document`: File attachments
  - `Payment`: Payment tracking
  - `Communication`: Messaging system
- **To Modify**: Add new fields, relationships, or tables

### Calculation Engine

#### `calculations.py`
- **Purpose**: Main loan calculation engine with comprehensive methodologies
- **Key Classes**:
  - `LoanCalculator`: Primary calculation class
- **Key Methods**:
  - `calculate_loan()`: Main routing method
  - `calculate_bridge_loan()`: Bridge loan calculations
  - `calculate_term_loan()`: Term loan calculations
  - `calculate_development_loan()`: Development loan calculations
  - `generate_payment_schedule()`: Payment schedule generation
- **To Modify Calculations**:
  - Interest rate formulas: Modify `calculate_interest_amount()`
  - Fee structures: Update `_calculate_fees()`
  - Payment schedules: Adjust `_generate_*_schedule()` methods
  - Net-to-gross conversions: Update `_calculate_gross_from_net_*()` methods

#### `loan_calculator.py`
- **Purpose**: Legacy calculation methods (kept for compatibility)
- **Status**: Gradually being replaced by `calculations.py`

### Web Interface

#### `routes.py`
- **Purpose**: Flask route definitions and request handling
- **Key Routes**:
  - `/`: Homepage and dashboard
  - `/calculator`: Loan calculator interface
  - `/calculate`: AJAX calculation endpoint
  - `/applications`: Loan applications management
  - `/quotes`: Quote generation and management
- **To Modify**: Add new endpoints, change URL patterns, update request handling

#### `auth.py`
- **Purpose**: Authentication and user management
- **Key Functions**:
  - User registration and login
  - Password validation
  - Session management
  - Role-based access control
- **To Modify**: Authentication rules, password policies, user roles

### Frontend Components

#### Templates (`templates/` directory)

##### `base.html`
- **Purpose**: Base template with common layout
- **Contains**: Navigation, footer, Novellus branding
- **To Modify**: Global layout, navigation structure, branding elements

##### `calculator.html`
- **Purpose**: Main loan calculator interface
- **Key Sections**:
  - Loan parameter forms
  - Results display tiles
  - Payment schedule table
  - Detailed calculation breakdown
  - Interactive charts
- **To Modify**: Form fields, result displays, table layouts

##### `dashboard.html`
- **Purpose**: User dashboard for borrowers and lenders
- **Contains**: Application summaries, quick actions, status updates
- **To Modify**: Dashboard widgets, user-specific content

#### Static Assets (`static/` directory)

##### `static/css/novellus-theme.css`
- **Purpose**: Main stylesheet with Novellus branding
- **Key Sections**:
  - CSS variables for colors
  - Result card styling
  - Table formatting
  - Responsive design rules
- **Color Scheme**:
  - Gold: `#B8860B` (primary brand color)
  - Navy: `#1E2B3A` (secondary brand color)
- **To Modify Visual Design**:
  - Colors: Update CSS variables at the top
  - Layout: Modify grid and flexbox rules
  - Typography: Update font families and sizes
  - Responsive breakpoints: Adjust media queries

##### `static/js/calculator.js`
- **Purpose**: Frontend JavaScript for calculator functionality
- **Key Functions**:
  - Form validation and submission
  - AJAX communication with backend
  - Dynamic UI updates
  - Chart initialization and updates
  - Table population
- **To Modify Behavior**:
  - Form validation: Update `validateForm()`
  - Data processing: Modify `updateResults()`
  - Chart configuration: Adjust `updateChart()`
  - Table formatting: Update `populateScheduleTable()`

### Document Generation

#### `pdf_quote_generator.py`
- **Purpose**: PDF quote generation with professional formatting
- **Key Features**:
  - Novellus branding and colors
  - Multi-page layout support
  - Payment schedule tables
  - Fee breakdowns
- **To Modify PDF Output**:
  - Layout: Update page structure and margins
  - Styling: Modify colors, fonts, and spacing
  - Content: Add new sections or data fields
  - Branding: Update logos and company information

#### `excel_generator.py`
- **Purpose**: Excel export functionality with multiple worksheets
- **Key Features**:
  - Professional styling with Novellus colors
  - Multiple sheets (Quote Summary, Payment Schedule, Fees)
  - Conditional formatting
- **To Modify Excel Output**:
  - Styling: Update `_create_styles()` method
  - Content: Modify sheet generation methods
  - Formatting: Adjust column widths and cell formats

### Utility Files

#### `utils.py`
- **Purpose**: Shared utility functions
- **Common Functions**:
  - Date manipulation
  - Number formatting
  - Validation helpers
- **To Modify**: Add new utility functions, update formatting rules

---

## Loan Calculation Engine

### Calculation Flow

1. **Parameter Validation**: Input validation and type conversion
2. **Fee Calculation**: Arrangement fees, legal fees, title insurance
3. **Interest Computation**: Based on loan type and repayment option
4. **Schedule Generation**: Payment dates and amounts
5. **Result Formatting**: Currency formatting and display preparation

### Loan Types and Options

#### Bridge Loans

**Repayment Options**:
- `"none"`: Retained interest (fees and interest deducted upfront)
- `"service_only"`: Interest-only monthly payments
- `"service_and_capital"`: Interest + capital monthly payments
- `"flexible"`: Fixed monthly payment amount
- `"capital_only"`: Capital-only payments (interest refunded)

**Key Calculations**:
- Daily interest methodology for precision
- Net-to-gross conversions for retained interest
- Balloon payment calculations

#### Term Loans

**Repayment Options**:
- `"interest_only"`: Interest-only payments
- `"capital_and_interest"`: Amortizing payments

**Key Features**:
- Daily interest calculations for Excel compatibility
- Loan start date considerations
- Payment timing (advance/arrears) support

#### Development Loans

**Features**:
- Multiple tranches with different rates
- Staggered release dates
- Per-tranche interest calculations
- Automatic or manual tranche generation

### Payment Timing and Frequency

**Timing Options**:
- `"advance"`: Payments due at period start
- `"arrears"`: Payments due at period end

**Frequency Options**:
- `"monthly"`: 12 payments per year
- `"quarterly"`: 4 payments per year

### Modifying Calculations

#### Adding New Fee Types

1. Update the `_calculate_fees()` method in `calculations.py`
2. Add fee parameters to the calculator form
3. Update PDF and Excel generators to include new fees

#### Changing Interest Calculation Methods

1. Modify the appropriate `calculate_*_amount()` methods
2. Update the `interest_type` parameter handling
3. Test with known values for accuracy

#### Adding New Repayment Options

1. Add new option to the `calculate_*_loan()` method
2. Create corresponding `_calculate_*_*()` private method
3. Update payment schedule generation
4. Add frontend form options

---

## Visual Interface Components

### Novellus Branding

The application uses an exclusive two-color palette:
- **Gold (`#B8860B`)**: Primary brand color for highlights and call-to-action elements
- **Navy (`#1E2B3A`)**: Secondary color for headers and contrast elements

### Key UI Components

#### Result Cards
- **Location**: `templates/calculator.html`
- **Purpose**: Display key calculation results
- **Styling**: Gradient backgrounds with hover effects
- **Modification**: Update card content in JavaScript `updateResults()` function

#### Data Tables
- **Payment Schedule Table**: Shows period-by-period payment breakdown
- **Detailed Calculation Table**: Shows step-by-step calculation mechanics
- **Styling**: Fixed layout with optimized column widths to prevent horizontal scrolling
- **Responsive**: Automatic font size and padding adjustments for mobile

#### Forms
- **Calculator Form**: Multi-section loan parameter input
- **Dynamic Fields**: Show/hide based on loan type and options
- **Validation**: Client-side validation with real-time feedback

### Responsive Design

The application uses Bootstrap 5 with custom CSS for responsive behavior:

#### Breakpoints
- **Desktop**: > 768px (full layout)
- **Tablet**: 768px - 992px (compact layout)
- **Mobile**: < 768px (minimal layout)

#### Table Responsiveness
- Automatic font size reduction on smaller screens
- Column width optimization
- Word wrapping for long content
- Elimination of horizontal scrolling

### Customizing the Interface

#### Changing Colors

1. Update CSS variables in `novellus-theme.css`:
```css
:root {
    --novellus-gold: #B8860B;
    --novellus-navy: #1E2B3A;
    /* Add new colors here */
}
```

2. Apply new colors to components:
```css
.your-component {
    background-color: var(--your-new-color);
}
```

#### Modifying Layout

1. **Grid Layout**: Update Bootstrap grid classes in templates
2. **Card Layout**: Modify card structures in HTML templates
3. **Table Layout**: Adjust column widths in CSS

#### Adding New Form Fields

1. Add HTML form field in `calculator.html`
2. Update JavaScript form collection in `calculator.js`
3. Add backend parameter handling in `routes.py`
4. Update calculation method in `calculations.py`

---

## Charts and Data Visualization

### Chart Implementation

The application uses Chart.js for data visualization with two main chart types:

#### Payment Schedule Chart
- **Type**: Line chart
- **Data**: Payment amounts over time
- **Location**: `calculator.html` and `calculator.js`
- **Purpose**: Visual representation of payment schedule

#### Balance Progression Chart
- **Type**: Area chart
- **Data**: Outstanding balance over loan term
- **Purpose**: Show loan balance reduction over time

### Chart Configuration

#### Basic Setup
```javascript
// Chart initialization in calculator.js
const ctx = document.getElementById('scheduleChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: chartData,
    options: chartOptions
});
```

#### Customizing Charts

1. **Colors**: Update color schemes to match Novellus branding
2. **Data**: Modify data processing in `updateChart()` function
3. **Layout**: Adjust chart size and responsiveness
4. **Interactions**: Add tooltips and hover effects

#### Chart Data Processing

The chart data is processed from the payment schedule:
```javascript
function updateChart(scheduleData) {
    const labels = scheduleData.map(item => `Period ${item.period}`);
    const paymentData = scheduleData.map(item => item.total_payment);
    const balanceData = scheduleData.map(item => item.closing_balance);
    
    // Update chart with new data
}
```

### Adding New Charts

1. **HTML**: Add canvas element to template
2. **JavaScript**: Create chart initialization function
3. **Data**: Process calculation results for chart format
4. **Styling**: Apply Novellus color scheme

---

## Reports and Document Generation

### PDF Quote Generation

#### Features
- Professional layout with Novellus branding
- Multi-page support with headers and footers
- Payment schedule tables
- Fee breakdowns and summaries

#### Customization

##### Layout Modifications
```python
# In pdf_quote_generator.py
def _add_header(self, canvas, doc):
    # Modify header content and styling
    pass

def _add_footer(self, canvas, doc):
    # Modify footer content and positioning
    pass
```

##### Content Sections
```python
def generate_quote_pdf(self, quote_data, application_data=None):
    # Add new sections by creating story elements
    story.append(self._create_custom_section(data))
```

##### Styling Updates
```python
# Update colors and fonts
NOVELLUS_GOLD = colors.Color(184/255, 134/255, 11/255)
NOVELLUS_NAVY = colors.Color(30/255, 43/255, 58/255)
```

### Excel Report Generation

#### Workbook Structure
- **Quote Summary**: Main loan details and calculations
- **Payment Schedule**: Detailed payment breakdown
- **Fees Breakdown**: All fees and charges

#### Customization

##### Adding New Worksheets
```python
# In excel_generator.py
def generate_quote_excel(self, quote_data, application_data=None):
    # Create new worksheet
    new_sheet = workbook.create_sheet(title="New Sheet")
    self._create_new_sheet(new_sheet, data)
```

##### Styling Modifications
```python
def _create_styles(self):
    # Update cell styles and formatting
    self.styles['custom_style'] = {
        'font': Font(name='Arial', size=12, bold=True),
        'fill': PatternFill(start_color='B8860B', end_color='B8860B', fill_type='solid')
    }
```

### Document Templates

#### Word Template Processing
- **Location**: Template files in `templates/` directory
- **Processing**: `quote_generator.py` handles template replacement
- **Placeholders**: Use `{{placeholder}}` syntax for dynamic content

#### Adding New Templates

1. Create template file with placeholders
2. Add template processing method
3. Update quote generation routes
4. Test with sample data

---

## Database Schema and Models

### Core Models

#### User Model
```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='borrower')
    # Add new fields here
```

#### LoanApplication Model
```python
class LoanApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    loan_type = db.Column(db.String(50), nullable=False)
    property_value = db.Column(db.Numeric(15, 2))
    # Loan-specific fields
```

#### Quote Model
```python
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('loan_application.id'))
    quote_data = db.Column(db.JSON)  # Stores calculation results
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Database Operations

#### Adding New Fields

1. **Model Update**: Add field to model class
2. **Migration**: Create and run database migration
3. **Form Update**: Add form field if user-input required
4. **Validation**: Add field validation rules

#### Relationships

##### One-to-Many
```python
# User -> Applications
user = db.relationship('User', backref=db.backref('applications', lazy=True))
```

##### Many-to-Many
```python
# For complex relationships, use association tables
association_table = db.Table('association',
    db.Column('left_id', db.Integer, db.ForeignKey('left.id')),
    db.Column('right_id', db.Integer, db.ForeignKey('right.id'))
)
```

### Database Configuration

#### Development (SQLite)
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loan_management.db'
```

#### Production (PostgreSQL)
```python
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
```

---

## Authentication and User Management

### Authentication Flow

1. **Registration**: User creates account with role selection
2. **Login**: Session-based authentication with Flask-Login
3. **Authorization**: Role-based access control
4. **JWT**: API token authentication for AJAX requests

### User Roles

#### Borrower
- **Permissions**: Create applications, view own data
- **Interface**: Simplified dashboard with application focus

#### Lender
- **Permissions**: View all applications, create quotes, access reports
- **Interface**: Advanced dashboard with management tools

### Security Features

#### Password Security
- **Hashing**: Werkzeug PBKDF2 hashing
- **Validation**: Minimum length and complexity requirements
- **Storage**: Secure hash storage (never plain text)

#### Session Management
- **Flask-Login**: Secure session handling
- **CSRF Protection**: Built-in Flask-WTF protection
- **Timeout**: Configurable session timeout

### Customizing Authentication

#### Adding New Roles
```python
# In models.py
ROLES = ['borrower', 'lender', 'admin', 'new_role']

# In auth.py
def check_role(required_role):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != required_role:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
```

#### Password Policies
```python
# In auth.py
def validate_password(password):
    # Add custom validation rules
    if len(password) < 8:
        return False
    # Add complexity requirements
    return True
```

---

## Configuration and Deployment

### Environment Configuration

#### Required Environment Variables
```bash
DATABASE_URL=postgresql://user:password@localhost/dbname
SESSION_SECRET=your-secret-key-here
FLASK_ENV=development  # or production
```

#### Optional Configuration
```bash
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB file upload limit
```

### Development Setup

1. **Dependencies**: Install from `Requirements.txt`
2. **Database**: Initialize with `db.create_all()`
3. **Environment**: Set development environment variables
4. **Run**: `python main.py` or `gunicorn main:app`

### Production Deployment

#### Database Setup
```python
# Production database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True,
}
```

#### Security Settings
```python
# Production security
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET')
app.config['WTF_CSRF_ENABLED'] = True
```

#### File Storage
- **Development**: Local filesystem
- **Production**: Configure cloud storage or network drives

---

## Customization Guide

### Common Modifications

#### Adding New Loan Types

1. **Backend**:
   - Add calculation method in `calculations.py`
   - Update route handling in `routes.py`
   - Add database fields if needed

2. **Frontend**:
   - Add form option in `calculator.html`
   - Update JavaScript handling in `calculator.js`
   - Add specific styling if needed

#### Modifying Interest Rates

1. **Calculation Logic**: Update interest calculation methods
2. **Validation**: Add rate validation rules
3. **Display**: Update formatting for rate display

#### Changing Currency Support

1. **Backend**: Update currency handling in calculations
2. **Frontend**: Add currency selection options
3. **Formatting**: Update number formatting functions
4. **Symbols**: Add currency symbols and formatting rules

#### Custom Fee Structures

1. **Logic**: Update fee calculation methods
2. **Parameters**: Add fee configuration options
3. **Display**: Update fee breakdown displays
4. **Documentation**: Update user documentation

### Advanced Customizations

#### API Integration

1. **External Data**: Add external API calls for rates or property values
2. **Authentication**: Implement API key management
3. **Error Handling**: Add robust error handling for API failures

#### Workflow Automation

1. **Email Notifications**: Add automated email sending
2. **Status Updates**: Implement automatic status progression
3. **Document Generation**: Automate document creation triggers

#### Reporting Enhancements

1. **Analytics**: Add usage analytics and reporting
2. **Performance**: Implement performance monitoring
3. **Audit Trail**: Add comprehensive audit logging

---

## Troubleshooting

### Common Issues

#### Calculation Errors

**Problem**: Incorrect calculation results
**Solutions**:
1. Check decimal precision settings
2. Verify input parameter types
3. Review calculation methodology
4. Add debugging logging

**Debugging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def calculate_loan(self, params):
    logger.debug(f"Input parameters: {params}")
    result = self._perform_calculation(params)
    logger.debug(f"Calculation result: {result}")
    return result
```

#### Frontend Issues

**Problem**: Charts not displaying
**Solutions**:
1. Check JavaScript console for errors
2. Verify Chart.js library loading
3. Validate data format
4. Test with minimal data set

**Problem**: Form validation failing
**Solutions**:
1. Check form field names match JavaScript
2. Verify validation rules
3. Test with various input combinations

#### Database Issues

**Problem**: Connection errors
**Solutions**:
1. Verify database URL and credentials
2. Check database server status
3. Test connection pooling settings

**Problem**: Migration failures
**Solutions**:
1. Check for data type conflicts
2. Verify constraint requirements
3. Review foreign key relationships

#### Performance Issues

**Problem**: Slow calculation responses
**Solutions**:
1. Profile calculation methods
2. Optimize database queries
3. Implement result caching
4. Review algorithm complexity

**Problem**: Large payment schedules
**Solutions**:
1. Implement pagination
2. Add data filtering options
3. Optimize table rendering
4. Consider data aggregation

### Debugging Tools

#### Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

#### Database Query Debugging
```python
# Enable SQLAlchemy query logging
app.config['SQLALCHEMY_ECHO'] = True
```

#### Frontend Debugging
```javascript
// Add console logging for debugging
console.log('Form data:', formData);
console.log('Calculation response:', response);
```

### Performance Optimization

#### Database Optimization
1. **Indexing**: Add indexes for frequently queried fields
2. **Query Optimization**: Use efficient query patterns
3. **Connection Pooling**: Configure appropriate pool sizes

#### Frontend Optimization
1. **Asset Minification**: Minify CSS and JavaScript
2. **Image Optimization**: Optimize image sizes and formats
3. **Caching**: Implement browser caching strategies

#### Calculation Optimization
1. **Caching**: Cache complex calculation results
2. **Lazy Loading**: Load detailed calculations on demand
3. **Batch Processing**: Process multiple calculations efficiently

---

## Maintenance and Updates

### Regular Maintenance

#### Database Maintenance
- **Backups**: Regular automated backups
- **Cleanup**: Remove old temporary data
- **Optimization**: Periodic performance tuning

#### Security Updates
- **Dependencies**: Keep libraries updated
- **Vulnerability Scanning**: Regular security audits
- **Access Review**: Periodic access rights review

#### Performance Monitoring
- **Metrics**: Track key performance indicators
- **Logging**: Monitor error rates and patterns
- **User Feedback**: Collect and address user issues

### Update Procedures

#### Code Updates
1. **Testing**: Thorough testing in development environment
2. **Backup**: Create system backup before deployment
3. **Deployment**: Deploy changes during low-usage periods
4. **Verification**: Post-deployment testing and monitoring

#### Database Updates
1. **Schema Changes**: Use migration scripts
2. **Data Migration**: Test data migration procedures
3. **Rollback Plans**: Prepare rollback procedures
4. **Validation**: Verify data integrity after changes

This documentation provides a comprehensive guide for understanding, maintaining, and modifying the Novellus Loan Management System. Each section includes specific file references and code examples to help with implementation of changes and customizations.