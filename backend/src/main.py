import os
import sys
import json
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
from src.models.video import Video, VideoProgress, VideoBookmark
from src.models.knowledge_base import (
    ResourceCategory, KnowledgeResource, ResourceDownload,
    ResourceBookmark
)
from src.models.admin import Organization, AdminUser, AuditLog, SystemSettings

# Import all route blueprints
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.courses import courses_bp
from src.routes.quizzes import quizzes_bp
from src.routes.progress import progress_bp
from src.routes.certificates import certificates_bp
from src.routes.analytics import analytics_bp
from src.routes.videos import videos_bp
from src.routes.knowledge_base import knowledge_base_bp
from src.routes.admin import admin_bp
from src.routes.reporting import reporting_bp
from src.routes.enterprise import enterprise_bp
from src.routes.branding import branding_bp

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
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(videos_bp, url_prefix='/api/videos')
    app.register_blueprint(knowledge_base_bp, url_prefix='/api/knowledge')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(reporting_bp, url_prefix='/api/reporting')
    app.register_blueprint(enterprise_bp, url_prefix='/api/enterprise')
    app.register_blueprint(branding_bp, url_prefix='/api/branding')
    
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
    
    # Create sample quizzes for each course
    from src.models.quiz import Quiz, Question
    
    # Get first module of each course for quiz assignment
    first_modules = Module.query.filter_by(order_index=1).all()
    
    quiz_data = [
        {
            'module_id': first_modules[0].id if len(first_modules) > 0 else 1,  # ISO 42001 Foundations
            'title': 'ISO 42001 Foundations Assessment',
            'description': 'Test your understanding of AI governance fundamentals',
            'time_limit_minutes': 30,
            'passing_score': 70,
            'max_attempts': 3,
            'questions': [
                {
                    'question_text': 'What is the primary purpose of ISO/IEC 42001?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'To provide guidelines for AI system development',
                        'To establish requirements for AI management systems',
                        'To define AI testing procedures',
                        'To regulate AI market practices'
                    ],
                    'correct_answer': 'To establish requirements for AI management systems',
                    'explanation': 'ISO/IEC 42001 specifies requirements for establishing, implementing, maintaining and continually improving an AI management system.'
                },
                {
                    'question_text': 'Which of the following are key components of an AI management system? (Select all that apply)',
                    'question_type': 'multiple_select',
                    'options': [
                        'Risk management',
                        'Governance framework',
                        'Performance monitoring',
                        'Marketing strategy'
                    ],
                    'correct_answer': 'Risk management,Governance framework,Performance monitoring',
                    'explanation': 'AI management systems include risk management, governance frameworks, and performance monitoring, but not marketing strategy.'
                }
            ]
        },
        {
            'module_id': first_modules[1].id if len(first_modules) > 1 else 2,  # ISO 42001 Practitioner
            'title': 'ISO 42001 Practitioner Exam',
            'description': 'Advanced assessment for practical implementation knowledge',
            'time_limit_minutes': 45,
            'passing_score': 75,
            'max_attempts': 2,
            'questions': [
                {
                    'question_text': 'How should AI risks be categorized in an ISO 42001 implementation?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'By technical complexity only',
                        'By business impact and likelihood',
                        'By development cost',
                        'By team size requirements'
                    ],
                    'correct_answer': 'By business impact and likelihood',
                    'explanation': 'AI risks should be categorized based on their potential business impact and likelihood of occurrence.'
                }
            ]
        }
    ]
    
    for quiz_info in quiz_data:
        questions_data = quiz_info.pop('questions')
        quiz = Quiz(**quiz_info)
        db.session.add(quiz)
        db.session.commit()  # Commit to get quiz.id
        
        for i, q_data in enumerate(questions_data):
            # Convert sample data format to model format
            question = Question(
                quiz_id=quiz.id,
                question_text=q_data['question_text'],
                question_type=q_data.get('question_type', 'mcq'),
                options_json=json.dumps(q_data.get('options', [])),
                correct_answers_json=json.dumps([q_data.get('correct_answer', '')]),
                explanation=q_data.get('explanation', ''),
                points=q_data.get('points', 1),
                order_index=i + 1
            )
            db.session.add(question)
    
    db.session.commit()
    print("Sample data created successfully!")

# Create the Flask application
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)

