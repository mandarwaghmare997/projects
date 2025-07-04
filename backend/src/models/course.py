from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    level = db.Column(db.Integer, nullable=False)  # 1-4: Foundation, Practitioner, Lead Implementer, Auditor
    duration_hours = db.Column(db.Float, nullable=False)
    passing_score = db.Column(db.Integer, default=70, nullable=False)  # Percentage required to pass
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # AWS S3 compatible fields
    thumbnail_url = db.Column(db.String(500), nullable=True)  # S3 URL for course thumbnail
    
    # Relationships
    modules = db.relationship('Module', backref='course', lazy=True, cascade='all, delete-orphan', order_by='Module.order_index')
    enrollments = db.relationship('CourseEnrollment', backref='course', lazy=True, cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='course', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Course {self.title}>'

    def to_dict(self, include_modules=False):
        """Convert course to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'level': self.level,
            'level_name': self.get_level_name(),
            'duration_hours': self.duration_hours,
            'passing_score': self.passing_score,
            'is_active': self.is_active,
            'thumbnail_url': self.thumbnail_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'module_count': len(self.modules),
            'enrollment_count': len(self.enrollments)
        }
        
        if include_modules:
            data['modules'] = [module.to_dict() for module in self.modules]
            
        return data

    def get_level_name(self):
        """Get human-readable level name"""
        level_names = {
            1: "ISO 42001 Foundations",
            2: "ISO 42001 Practitioner", 
            3: "ISO 42001 Lead Implementer",
            4: "ISO 42001 Auditor/Assessor"
        }
        return level_names.get(self.level, f"Level {self.level}")

    def get_completion_rate(self):
        """Calculate course completion rate"""
        if not self.enrollments:
            return 0
        completed = len([e for e in self.enrollments if e.status == 'completed'])
        return (completed / len(self.enrollments)) * 100

    @staticmethod
    def get_by_level(level):
        """Get courses by certification level"""
        return Course.query.filter_by(level=level, is_active=True).all()

    @staticmethod
    def get_active_courses():
        """Get all active courses"""
        return Course.query.filter_by(is_active=True).order_by(Course.level, Course.title).all()


class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content_text = db.Column(db.Text, nullable=True)  # Rich text content
    video_url = db.Column(db.String(500), nullable=True)  # YouTube or S3 video URL
    order_index = db.Column(db.Integer, nullable=False)  # Order within course
    duration_minutes = db.Column(db.Integer, nullable=False, default=30)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # AWS S3 compatible fields
    video_s3_key = db.Column(db.String(500), nullable=True)  # S3 object key for video
    transcript_s3_key = db.Column(db.String(500), nullable=True)  # S3 object key for transcript
    
    # Relationships
    progress = db.relationship('UserProgress', backref='module', lazy=True, cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='module', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Module {self.title}>'

    def to_dict(self, include_content=False):
        """Convert module to dictionary"""
        data = {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'video_url': self.video_url,
            'order_index': self.order_index,
            'duration_minutes': self.duration_minutes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'quiz_count': len(self.quizzes)
        }
        
        if include_content:
            data['content_text'] = self.content_text
            data['video_s3_key'] = self.video_s3_key
            data['transcript_s3_key'] = self.transcript_s3_key
            
        return data

    def get_completion_rate(self):
        """Calculate module completion rate"""
        if not self.progress:
            return 0
        completed = len([p for p in self.progress if p.status == 'completed'])
        return (completed / len(self.progress)) * 100

    @staticmethod
    def get_by_course(course_id):
        """Get modules by course ID"""
        return Module.query.filter_by(course_id=course_id, is_active=True).order_by(Module.order_index).all()


class CourseEnrollment(db.Model):
    __tablename__ = 'course_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    status = db.Column(db.String(20), default='enrolled', nullable=False)  # enrolled, in_progress, completed, dropped
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    final_score = db.Column(db.Float, nullable=True)  # Final course score percentage
    
    # Unique constraint to prevent duplicate enrollments
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course_enrollment'),)

    def __repr__(self):
        return f'<CourseEnrollment User:{self.user_id} Course:{self.course_id}>'

    def to_dict(self):
        """Convert enrollment to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'status': self.status,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'final_score': self.final_score,
            'course': self.course.to_dict() if self.course else None
        }

    def start_course(self):
        """Mark course as started"""
        if self.status == 'enrolled':
            self.status = 'in_progress'
            self.started_at = datetime.utcnow()
            db.session.commit()

    def complete_course(self, final_score):
        """Mark course as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        self.final_score = final_score
        db.session.commit()

    @staticmethod
    def get_user_enrollments(user_id):
        """Get all enrollments for a user"""
        return CourseEnrollment.query.filter_by(user_id=user_id).all()

    @staticmethod
    def is_enrolled(user_id, course_id):
        """Check if user is enrolled in course"""
        return CourseEnrollment.query.filter_by(user_id=user_id, course_id=course_id).first() is not None

    @staticmethod
    def enroll_user(user_id, course_id):
        """Enroll user in course"""
        if not CourseEnrollment.is_enrolled(user_id, course_id):
            enrollment = CourseEnrollment(user_id=user_id, course_id=course_id)
            db.session.add(enrollment)
            db.session.commit()
            return enrollment
        return None

