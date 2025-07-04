import os
import sys
from datetime import datetime, timedelta
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, current_app
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

# Import all models to ensure they're registered with SQLAlchemy
from src.models.user import db, User
from src.models.course import Course, Module, CourseEnrollment
from src.models.quiz import Quiz, Question, QuizAttempt
from src.models.progress import UserProgress, Certificate, LearningAnalytics

# Import all route blueprints
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.courses import courses_bp
from src.routes.quizzes import quizzes_bp
from src.routes.progress import progress_bp
from src.routes.certificates import certificates_bp

def create_app(config_name='development'):
    """Application factory pattern for AWS deployment"""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Configuration for different environments
    if config_name == 'production':
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'qryti-learn-production-key-2025')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 
            f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
        app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'qryti-jwt-secret-2025')
        app.config['DEBUG'] = False
    else:
        app.config['SECRET_KEY'] = 'qryti-learn-dev-key-2025'
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
        app.config['JWT_SECRET_KEY'] = 'qryti-jwt-dev-secret-2025'
        app.config['DEBUG'] = True
    
    # Database configuration
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT configuration
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_ALGORITHM'] = 'HS256'
    app.config['JWT_DECODE_ALGORITHMS'] = ['HS256']
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    
    # AWS and Qryti.com configuration
    app.config['QRYTI_DOMAIN'] = os.environ.get('QRYTI_DOMAIN', 'qryti.com')
    app.config['QRYTI_LEARN_URL'] = os.environ.get('QRYTI_LEARN_URL', 'https://learn.qryti.com')
    app.config['AWS_S3_BUCKET'] = os.environ.get('AWS_S3_BUCKET', 'qryti-learn-assets')
    app.config['AWS_REGION'] = os.environ.get('AWS_REGION', 'us-east-1')
    
    # Initialize extensions
    db.init_app(app)
    
    # Configure CORS for AWS deployment and frontend integration
    CORS(app, 
         origins=[
             'http://localhost:3000',  # Local development
             'http://localhost:5173',  # Vite dev server
             'https://learn.qryti.com',  # Production domain
             'https://*.qryti.com',  # All Qryti subdomains
             'https://*.amazonaws.com',  # AWS CloudFront
         ],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    )
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # JWT error handlers with debug logging
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        current_app.logger.error(f"JWT expired token: header={jwt_header}, payload={jwt_payload}")
        return jsonify({'error': 'Token has expired', 'code': 'token_expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        current_app.logger.error(f"JWT invalid token: error={error}")
        return jsonify({'error': 'Invalid token', 'code': 'invalid_token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        current_app.logger.error(f"JWT missing token: error={error}")
        return jsonify({'error': 'Authorization token required', 'code': 'authorization_required'}), 401
    
    # Register blueprints with API prefix
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    app.register_blueprint(quizzes_bp, url_prefix='/api/quizzes')
    app.register_blueprint(progress_bp, url_prefix='/api/progress')
    app.register_blueprint(certificates_bp, url_prefix='/api/certificates')
    
    # Health check endpoint for AWS load balancer
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'qryti-learn-api',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # API info endpoint
    @app.route('/api')
    def api_info():
        return jsonify({
            'service': 'Qryti Learn API',
            'version': '1.0.0',
            'description': 'ISO/IEC 42001 AI Management Systems Learning Platform',
            'domain': app.config['QRYTI_DOMAIN'],
            'endpoints': {
                'auth': '/api/auth',
                'users': '/api/users',
                'courses': '/api/courses',
                'quizzes': '/api/quizzes',
                'progress': '/api/progress',
                'certificates': '/api/certificates'
            },
            'documentation': f"https://docs.{app.config['QRYTI_DOMAIN']}/api"
        })
    
    # Frontend serving (for production deployment)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return jsonify({'error': 'Frontend not configured'}), 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return jsonify({
                    'message': 'Qryti Learn API is running',
                    'frontend': 'Not deployed',
                    'api_docs': '/api'
                }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found', 'code': 'not_found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error', 'code': 'internal_error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'code': 'bad_request'}), 400
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create sample data if in development mode
        if config_name == 'development':
            create_sample_data()
    
    return app

def create_sample_data():
    """Create sample data for development and testing"""
    from datetime import datetime
    
    # Check if data already exists
    if User.query.first():
        return
    
    print("Creating sample data for Qryti Learn...")
    
    # Create sample admin user
    admin = User.create_user(
        email='admin@qryti.com',
        password='admin123',
        first_name='Qryti',
        last_name='Administrator',
        organization='Qryti.com',
        role='admin'
    )
    db.session.add(admin)
    
    # Create sample student user
    student = User.create_user(
        email='student@example.com',
        password='student123',
        first_name='John',
        last_name='Doe',
        organization='TechCorp Inc.',
        role='student'
    )
    db.session.add(student)
    
    db.session.commit()
    
    # Create sample courses
    courses_data = [
        {
            'title': 'ISO 42001 Foundations',
            'description': 'Basic understanding of AI governance and ISO 42001 standard',
            'level': 1,
            'duration_hours': 3.0,
            'passing_score': 70
        },
        {
            'title': 'ISO 42001 Practitioner',
            'description': 'Practical implementation knowledge and risk management',
            'level': 2,
            'duration_hours': 5.0,
            'passing_score': 75
        },
        {
            'title': 'ISO 42001 Lead Implementer',
            'description': 'Advanced implementation strategies and audit preparation',
            'level': 3,
            'duration_hours': 8.0,
            'passing_score': 80
        },
        {
            'title': 'ISO 42001 Auditor/Assessor',
            'description': 'Audit techniques and assessment methodologies',
            'level': 4,
            'duration_hours': 10.0,
            'passing_score': 85
        }
    ]
    
    for course_data in courses_data:
        course = Course(**course_data)
        db.session.add(course)
        db.session.commit()
        
        # Create sample modules for each course
        for i in range(1, course_data['level'] * 2 + 3):  # Variable number of modules
            module = Module(
                course_id=course.id,
                title=f'Module {i}: {course.title} - Part {i}',
                description=f'Learning module {i} for {course.title}',
                content_text=f'This is the content for module {i} of {course.title}.',
                video_url=f'https://youtube.com/watch?v=sample{i}',
                order_index=i,
                duration_minutes=30 + (i * 10)
            )
            db.session.add(module)
    
    db.session.commit()
    print("Sample data created successfully!")

# Create the Flask application
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # For local development
    app.run(host='0.0.0.0', port=5000, debug=True)

