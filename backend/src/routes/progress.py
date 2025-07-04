from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, desc

from src.models.user import User, db
from src.models.course import Course, CourseEnrollment
from src.models.quiz import Quiz, QuizAttempt
from src.models.progress import UserProgress, Certificate, LearningAnalytics

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_progress_dashboard():
    """Get comprehensive progress dashboard data for current user"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Get overview statistics
        enrolled_courses = CourseEnrollment.query.filter_by(user_id=current_user_id).count()
        completed_courses = CourseEnrollment.query.filter_by(
            user_id=current_user_id, 
            status='completed'
        ).count()
        certificates_earned = Certificate.query.filter_by(
            user_id=current_user_id, 
            is_valid=True
        ).count()
        
        # Calculate total time spent
        total_time = db.session.query(func.sum(UserProgress.time_spent_minutes))\
            .filter_by(user_id=current_user_id).scalar() or 0
        
        # Get course progress details
        enrollments = CourseEnrollment.query.filter_by(user_id=current_user_id)\
            .join(Course).all()
        
        courses_progress = []
        for enrollment in enrollments:
            course = enrollment.course
            
            # Get progress for this course
            progress_records = UserProgress.query.filter_by(
                user_id=current_user_id,
                course_id=course.id
            ).all()
            
            total_modules = len(course.modules) if course.modules else 0
            completed_modules = len([p for p in progress_records if p.status == 'completed'])
            completion_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0
            
            course_time = sum(p.time_spent_minutes for p in progress_records)
            
            # Calculate average score from quiz attempts
            quiz_attempts = QuizAttempt.query.join(Quiz)\
                .filter(Quiz.course_id == course.id, QuizAttempt.user_id == current_user_id)\
                .all()
            
            average_score = None
            if quiz_attempts:
                scores = [attempt.score for attempt in quiz_attempts if attempt.score is not None]
                if scores:
                    average_score = sum(scores) / len(scores)
            
            courses_progress.append({
                'id': course.id,
                'title': course.title,
                'level': course.level,
                'total_modules': total_modules,
                'completed_modules': completed_modules,
                'completion_percentage': completion_percentage,
                'time_spent_minutes': course_time,
                'average_score': average_score,
                'enrollment_status': enrollment.status,
                'enrolled_at': enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None
            })
        
        dashboard_data = {
            'overview': {
                'enrolled_courses': enrolled_courses,
                'completed_courses': completed_courses,
                'certificates_earned': certificates_earned,
                'total_time_minutes': total_time
            },
            'courses': courses_progress
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Get progress dashboard error: {str(e)}")
        return jsonify({'error': 'Failed to get progress dashboard'}), 500

@progress_bp.route('/course/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_progress(course_id):
    """Get detailed progress for a specific course"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Check if user is enrolled in the course
        enrollment = CourseEnrollment.query.filter_by(
            user_id=current_user_id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Not enrolled in this course'}), 404
        
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Get all progress records for this course
        progress_records = UserProgress.query.filter_by(
            user_id=current_user_id,
            course_id=course_id
        ).all()
        
        # Get quiz attempts for this course
        quiz_attempts = QuizAttempt.query.join(Quiz)\
            .filter(Quiz.course_id == course_id, QuizAttempt.user_id == current_user_id)\
            .order_by(desc(QuizAttempt.attempted_at)).all()
        
        # Calculate summary statistics
        total_modules = len(course.modules) if course.modules else 0
        completed_modules = len([p for p in progress_records if p.status == 'completed'])
        in_progress_modules = len([p for p in progress_records if p.status == 'in_progress'])
        total_time = sum(p.time_spent_minutes for p in progress_records)
        
        completion_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0
        
        # Average score from quiz attempts
        scores = [attempt.score for attempt in quiz_attempts if attempt.score is not None]
        average_score = sum(scores) / len(scores) if scores else None
        
        progress_data = {
            'course': {
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'level': course.level
            },
            'enrollment': {
                'status': enrollment.status,
                'enrolled_at': enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
                'completed_at': enrollment.completed_at.isoformat() if enrollment.completed_at else None,
                'final_score': enrollment.final_score
            },
            'summary': {
                'total_modules': total_modules,
                'completed_modules': completed_modules,
                'in_progress_modules': in_progress_modules,
                'completion_percentage': completion_percentage,
                'total_time_minutes': total_time,
                'average_score': average_score
            },
            'modules': [p.to_dict() for p in progress_records],
            'quiz_attempts': [
                {
                    'id': attempt.id,
                    'quiz_title': attempt.quiz.title,
                    'score': attempt.score,
                    'passed': attempt.passed,
                    'attempted_at': attempt.attempted_at.isoformat(),
                    'time_taken_minutes': attempt.time_taken_minutes
                } for attempt in quiz_attempts
            ]
        }
        
        return jsonify(progress_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Get course progress error: {str(e)}")
        return jsonify({'error': 'Failed to get course progress'}), 500

@progress_bp.route('/module/<int:module_id>/start', methods=['POST'])
@jwt_required()
def start_module(module_id):
    """Mark a module as started"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Get or create progress record
        progress = UserProgress.query.filter_by(
            user_id=current_user_id,
            module_id=module_id
        ).first()
        
        if not progress:
            # Get module to find course_id
            from src.models.course import Module
            module = Module.query.get(module_id)
            if not module:
                return jsonify({'error': 'Module not found'}), 404
            
            progress = UserProgress(
                user_id=current_user_id,
                course_id=module.course_id,
                module_id=module_id
            )
            db.session.add(progress)
        
        progress.start_module()
        
        # Log analytics event
        LearningAnalytics.log_event(
            user_id=current_user_id,
            event_type='module_started',
            event_data={
                'module_id': module_id,
                'course_id': progress.course_id
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'message': 'Module started successfully',
            'progress': progress.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Start module error: {str(e)}")
        return jsonify({'error': 'Failed to start module'}), 500

@progress_bp.route('/module/<int:module_id>/complete', methods=['POST'])
@jwt_required()
def complete_module(module_id):
    """Mark a module as completed"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        score = data.get('score')
        
        progress = UserProgress.query.filter_by(
            user_id=current_user_id,
            module_id=module_id
        ).first()
        
        if not progress:
            return jsonify({'error': 'Module progress not found'}), 404
        
        progress.complete_module(score)
        
        # Log analytics event
        LearningAnalytics.log_event(
            user_id=current_user_id,
            event_type='module_completed',
            event_data={
                'module_id': module_id,
                'course_id': progress.course_id,
                'score': score
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        # Check if course is now complete
        course_progress = UserProgress.get_course_progress_summary(
            current_user_id, 
            progress.course_id
        )
        
        if course_progress['completion_percentage'] >= 100:
            # Update enrollment status
            enrollment = CourseEnrollment.query.filter_by(
                user_id=current_user_id,
                course_id=progress.course_id
            ).first()
            
            if enrollment and enrollment.status != 'completed':
                enrollment.status = 'completed'
                enrollment.completed_at = datetime.utcnow()
                enrollment.final_score = course_progress['average_score']
                db.session.commit()
                
                # Log course completion
                LearningAnalytics.log_event(
                    user_id=current_user_id,
                    event_type='course_completed',
                    event_data={
                        'course_id': progress.course_id,
                        'final_score': course_progress['average_score']
                    },
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )
        
        return jsonify({
            'message': 'Module completed successfully',
            'progress': progress.to_dict(),
            'course_progress': course_progress
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Complete module error: {str(e)}")
        return jsonify({'error': 'Failed to complete module'}), 500

@progress_bp.route('/module/<int:module_id>/time', methods=['POST'])
@jwt_required()
def update_time_spent(module_id):
    """Update time spent on a module"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        additional_minutes = data.get('additional_minutes', 0)
        
        if additional_minutes <= 0:
            return jsonify({'error': 'Invalid time value'}), 400
        
        progress = UserProgress.query.filter_by(
            user_id=current_user_id,
            module_id=module_id
        ).first()
        
        if not progress:
            return jsonify({'error': 'Module progress not found'}), 404
        
        progress.update_time_spent(additional_minutes)
        
        return jsonify({
            'message': 'Time updated successfully',
            'total_time_minutes': progress.time_spent_minutes
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update time spent error: {str(e)}")
        return jsonify({'error': 'Failed to update time spent'}), 500

@progress_bp.route('/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    """Get leaderboard data"""
    try:
        # Get top learners by certificates earned
        top_by_certificates = db.session.query(
            User.id,
            User.first_name,
            User.last_name,
            func.count(Certificate.id).label('certificates_count')
        ).join(Certificate, User.id == Certificate.user_id)\
         .filter(Certificate.is_valid == True)\
         .group_by(User.id, User.first_name, User.last_name)\
         .order_by(desc('certificates_count'))\
         .limit(10).all()
        
        # Get top learners by time spent
        top_by_time = db.session.query(
            User.id,
            User.first_name,
            User.last_name,
            func.sum(UserProgress.time_spent_minutes).label('total_time')
        ).join(UserProgress, User.id == UserProgress.user_id)\
         .group_by(User.id, User.first_name, User.last_name)\
         .order_by(desc('total_time'))\
         .limit(10).all()
        
        # Get top learners by courses completed
        top_by_courses = db.session.query(
            User.id,
            User.first_name,
            User.last_name,
            func.count(CourseEnrollment.id).label('completed_courses')
        ).join(CourseEnrollment, User.id == CourseEnrollment.user_id)\
         .filter(CourseEnrollment.status == 'completed')\
         .group_by(User.id, User.first_name, User.last_name)\
         .order_by(desc('completed_courses'))\
         .limit(10).all()
        
        leaderboard_data = {
            'certificates': [
                {
                    'user_id': row.id,
                    'name': f"{row.first_name} {row.last_name}",
                    'count': row.certificates_count
                } for row in top_by_certificates
            ],
            'time_spent': [
                {
                    'user_id': row.id,
                    'name': f"{row.first_name} {row.last_name}",
                    'minutes': row.total_time
                } for row in top_by_time
            ],
            'courses_completed': [
                {
                    'user_id': row.id,
                    'name': f"{row.first_name} {row.last_name}",
                    'count': row.completed_courses
                } for row in top_by_courses
            ]
        }
        
        return jsonify(leaderboard_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Get leaderboard error: {str(e)}")
        return jsonify({'error': 'Failed to get leaderboard data'}), 500


