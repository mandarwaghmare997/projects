from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import secrets
import json
from src.models.user import db

class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    status = db.Column(db.String(20), default='not_started', nullable=False)  # not_started, in_progress, completed
    score = db.Column(db.Float, nullable=True)  # Module completion score
    time_spent_minutes = db.Column(db.Integer, default=0, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Unique constraint to prevent duplicate progress records
    __table_args__ = (db.UniqueConstraint('user_id', 'module_id', name='unique_user_module_progress'),)

    def __repr__(self):
        return f'<UserProgress User:{self.user_id} Module:{self.module_id}>'

    def to_dict(self):
        """Convert progress to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'module_id': self.module_id,
            'status': self.status,
            'score': self.score,
            'time_spent_minutes': self.time_spent_minutes,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'module': self.module.to_dict() if self.module else None
        }

    def start_module(self):
        """Mark module as started"""
        if self.status == 'not_started':
            self.status = 'in_progress'
            self.started_at = datetime.utcnow()
            self.last_accessed = datetime.utcnow()
            db.session.commit()

    def complete_module(self, score=None):
        """Mark module as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        if score is not None:
            self.score = score
        db.session.commit()

    def update_time_spent(self, additional_minutes):
        """Update time spent on module"""
        self.time_spent_minutes += additional_minutes
        self.last_accessed = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def get_user_progress(user_id, course_id=None, module_id=None):
        """Get user progress records"""
        query = UserProgress.query.filter_by(user_id=user_id)
        if course_id:
            query = query.filter_by(course_id=course_id)
        if module_id:
            query = query.filter_by(module_id=module_id)
        return query.all()

    @staticmethod
    def get_or_create_progress(user_id, course_id, module_id):
        """Get existing progress or create new record"""
        progress = UserProgress.query.filter_by(
            user_id=user_id, 
            module_id=module_id
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                course_id=course_id,
                module_id=module_id
            )
            db.session.add(progress)
            db.session.commit()
        
        return progress

    @staticmethod
    def get_course_progress_summary(user_id, course_id):
        """Get course progress summary for user"""
        progress_records = UserProgress.get_user_progress(user_id, course_id)
        
        total_modules = len(progress_records)
        completed_modules = len([p for p in progress_records if p.status == 'completed'])
        in_progress_modules = len([p for p in progress_records if p.status == 'in_progress'])
        total_time = sum(p.time_spent_minutes for p in progress_records)
        average_score = sum(p.score for p in progress_records if p.score) / len([p for p in progress_records if p.score]) if progress_records else 0
        
        return {
            'total_modules': total_modules,
            'completed_modules': completed_modules,
            'in_progress_modules': in_progress_modules,
            'completion_percentage': (completed_modules / total_modules * 100) if total_modules > 0 else 0,
            'total_time_minutes': total_time,
            'average_score': round(average_score, 2)
        }


class Certificate(db.Model):
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    certificate_id = db.Column(db.String(50), unique=True, nullable=False)  # Public certificate ID
    verification_code = db.Column(db.String(20), unique=True, nullable=False)  # Short verification code
    final_score = db.Column(db.Float, nullable=False)  # Final course score
    issued_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)  # Optional expiration date
    is_valid = db.Column(db.Boolean, default=True, nullable=False)
    
    # AWS S3 compatible fields
    pdf_s3_key = db.Column(db.String(500), nullable=True)  # S3 object key for PDF
    pdf_url = db.Column(db.String(500), nullable=True)  # Public S3 URL for PDF
    pdf_path = db.Column(db.String(500), nullable=True)  # Local PDF file path
    verification_url = db.Column(db.String(500), nullable=True)  # Public verification URL
    
    # Metadata
    metadata_json = db.Column(db.Text, nullable=True)  # Additional certificate metadata
    
    # Unique constraint to prevent duplicate certificates
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course_certificate'),)

    def __repr__(self):
        return f'<Certificate {self.certificate_id}>'

    def to_dict(self, include_verification=False):
        """Convert certificate to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'certificate_id': self.certificate_id,
            'final_score': self.final_score,
            'issued_at': self.issued_at.isoformat() if self.issued_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_valid': self.is_valid,
            'pdf_url': self.pdf_url,
            'verification_url': self.verification_url,
            'user': self.user.to_dict() if self.user else None,
            'course': self.course.to_dict() if self.course else None
        }
        
        if include_verification:
            data['verification_code'] = self.verification_code
            data['pdf_s3_key'] = self.pdf_s3_key
            
        return data

    def generate_verification_url(self, base_url="https://learn.qryti.com"):
        """Generate public verification URL"""
        self.verification_url = f"{base_url}/verify/{self.certificate_id}"
        return self.verification_url

    def revoke(self):
        """Revoke the certificate"""
        self.is_valid = False
        db.session.commit()

    def is_expired(self):
        """Check if certificate is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    @staticmethod
    def generate_certificate_id():
        """Generate unique certificate ID"""
        return f"QRYTI-{datetime.utcnow().strftime('%Y')}-{secrets.token_hex(8).upper()}"

    @staticmethod
    def generate_verification_code():
        """Generate short verification code"""
        return secrets.token_hex(4).upper()

    @staticmethod
    def create_certificate(user_id, course_id, final_score):
        """Create a new certificate"""
        # Check if certificate already exists
        existing = Certificate.query.filter_by(user_id=user_id, course_id=course_id).first()
        if existing:
            return existing
        
        certificate = Certificate(
            user_id=user_id,
            course_id=course_id,
            certificate_id=Certificate.generate_certificate_id(),
            verification_code=Certificate.generate_verification_code(),
            final_score=final_score
        )
        
        certificate.generate_verification_url()
        
        db.session.add(certificate)
        db.session.commit()
        return certificate

    @staticmethod
    def verify_certificate(certificate_id):
        """Verify certificate by ID"""
        certificate = Certificate.query.filter_by(certificate_id=certificate_id).first()
        if certificate and certificate.is_valid and not certificate.is_expired():
            return certificate
        return None

    @staticmethod
    def verify_by_code(verification_code):
        """Verify certificate by verification code"""
        certificate = Certificate.query.filter_by(verification_code=verification_code).first()
        if certificate and certificate.is_valid and not certificate.is_expired():
            return certificate
        return None

    @staticmethod
    def get_user_certificates(user_id):
        """Get all certificates for a user"""
        return Certificate.query.filter_by(user_id=user_id, is_valid=True).order_by(Certificate.issued_at.desc()).all()

    @staticmethod
    def get_course_certificates(course_id):
        """Get all certificates for a course"""
        return Certificate.query.filter_by(course_id=course_id, is_valid=True).order_by(Certificate.issued_at.desc()).all()


class LearningAnalytics(db.Model):
    __tablename__ = 'learning_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # login, module_start, module_complete, quiz_attempt, etc.
    event_data_json = db.Column(db.Text, nullable=True)  # JSON data for the event
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    session_id = db.Column(db.String(100), nullable=True)  # Session tracking
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4/IPv6 address
    user_agent = db.Column(db.String(500), nullable=True)  # Browser/device info

    def __repr__(self):
        return f'<LearningAnalytics {self.event_type} User:{self.user_id}>'

    def to_dict(self):
        """Convert analytics record to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'event_type': self.event_type,
            'event_data': json.loads(self.event_data_json) if self.event_data_json else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }

    @staticmethod
    def log_event(user_id, event_type, event_data=None, session_id=None, ip_address=None, user_agent=None):
        """Log a learning analytics event"""
        analytics = LearningAnalytics(
            user_id=user_id,
            event_type=event_type,
            event_data_json=json.dumps(event_data) if event_data else None,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(analytics)
        db.session.commit()
        return analytics

    @staticmethod
    def get_user_analytics(user_id, event_type=None, limit=100):
        """Get analytics for a user"""
        query = LearningAnalytics.query.filter_by(user_id=user_id)
        if event_type:
            query = query.filter_by(event_type=event_type)
        return query.order_by(LearningAnalytics.timestamp.desc()).limit(limit).all()

