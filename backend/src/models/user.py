from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    organization = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='student')  # student, admin, enterprise_admin
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    progress = db.relationship('UserProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='user', lazy=True, cascade='all, delete-orphan')
    enrollments = db.relationship('CourseEnrollment', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def get_full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'organization': self.organization,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
            
        return data

    def get_progress_summary(self):
        """Get user's learning progress summary"""
        total_courses = len(self.enrollments)
        completed_courses = len([e for e in self.enrollments if e.status == 'completed'])
        total_certificates = len(self.certificates)
        
        return {
            'total_courses': total_courses,
            'completed_courses': completed_courses,
            'completion_rate': (completed_courses / total_courses * 100) if total_courses > 0 else 0,
            'total_certificates': total_certificates
        }

    @staticmethod
    def create_user(email, password, first_name, last_name, organization=None, role='student'):
        """Create a new user"""
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            organization=organization,
            role=role
        )
        user.set_password(password)
        return user

    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def authenticate(email, password):
        """Authenticate user with email and password"""
        user = User.find_by_email(email)
        if user and user.check_password(password) and user.is_active:
            user.last_login = datetime.utcnow()
            db.session.commit()
            return user
        return None

