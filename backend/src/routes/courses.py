from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from src.models.user import User, db
from src.models.course import Course, Module, CourseEnrollment
from src.models.quiz import Quiz, QuizAttempt
from src.models.progress import UserProgress, LearningAnalytics

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/', methods=['GET'])
def get_courses():
    """Get all active courses"""
    try:
        level = request.args.get('level', type=int)
        
        if level:
            courses = Course.get_by_level(level)
        else:
            courses = Course.get_active_courses()
        
        return jsonify({
            'courses': [course.to_dict() for course in courses],
            'total': len(courses)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get courses error: {str(e)}")
        return jsonify({'error': 'Failed to get courses'}), 500

@courses_bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Get course details with modules"""
    try:
        course = Course.query.get(course_id)
        
        if not course or not course.is_active:
            return jsonify({'error': 'Course not found'}), 404
        
        return jsonify({
            'course': course.to_dict(include_modules=True)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get course error: {str(e)}")
        return jsonify({'error': 'Failed to get course'}), 500

@courses_bp.route('/<int:course_id>/quizzes', methods=['GET'])
def get_course_quizzes(course_id):
    """Get all quizzes for a course"""
    try:
        course = Course.query.get(course_id)
        if not course or not course.is_active:
            return jsonify({'error': 'Course not found'}), 404
        
        # Get quizzes for this course (through modules)
        quizzes = Quiz.query.join(Module).filter(
            Module.course_id == course_id,
            Quiz.is_active == True
        ).all()
        
        quizzes_data = []
        for quiz in quizzes:
            quiz_data = quiz.to_dict()
            # Add some basic stats
            quiz_data['question_count'] = len(quiz.questions)
            quiz_data['stats'] = {
                'total_attempts': QuizAttempt.query.filter_by(quiz_id=quiz.id).count(),
                'average_score': quiz.get_average_score()
            }
            quizzes_data.append(quiz_data)
        
        return jsonify(quizzes_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Get course quizzes error: {str(e)}")
        return jsonify({'error': 'Failed to get course quizzes'}), 500

@courses_bp.route('/<int:course_id>/modules', methods=['GET'])
def get_course_modules(course_id):
    """Get all modules for a course"""
    try:
        course = Course.query.get(course_id)
        
        if not course or not course.is_active:
            return jsonify({'error': 'Course not found'}), 404
        
        modules = Module.get_by_course(course_id)
        
        return jsonify({
            'modules': [module.to_dict() for module in modules],
            'course': course.to_dict(),
            'total': len(modules)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get course modules error: {str(e)}")
        return jsonify({'error': 'Failed to get course modules'}), 500

@courses_bp.route('/<int:course_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_in_course(course_id):
    """Enroll current user in a course"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if course exists and is active
        course = Course.query.get(course_id)
        if not course or not course.is_active:
            return jsonify({'error': 'Course not found'}), 404
        
        # Check if user is already enrolled
        if CourseEnrollment.is_enrolled(current_user_id, course_id):
            return jsonify({'error': 'Already enrolled in this course'}), 409
        
        # Create enrollment
        enrollment = CourseEnrollment.enroll_user(current_user_id, course_id)
        
        if not enrollment:
            return jsonify({'error': 'Failed to enroll in course'}), 500
        
        # Log enrollment event
        LearningAnalytics.log_event(
            user_id=current_user_id,
            event_type='course_enrolled',
            event_data={
                'course_id': course_id,
                'course_title': course.title,
                'course_level': course.level
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'message': 'Successfully enrolled in course',
            'enrollment': enrollment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Course enrollment error: {str(e)}")
        return jsonify({'error': 'Failed to enroll in course'}), 500

@courses_bp.route('/<int:course_id>/unenroll', methods=['DELETE'])
@jwt_required()
def unenroll_from_course(course_id):
    """Unenroll current user from a course"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find enrollment
        enrollment = CourseEnrollment.query.filter_by(
            user_id=current_user_id, 
            course_id=course_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Not enrolled in this course'}), 404
        
        # Don't allow unenrollment if course is completed
        if enrollment.status == 'completed':
            return jsonify({'error': 'Cannot unenroll from completed course'}), 400
        
        # Delete enrollment and related progress
        UserProgress.query.filter_by(
            user_id=current_user_id, 
            course_id=course_id
        ).delete()
        
        db.session.delete(enrollment)
        db.session.commit()
        
        # Log unenrollment event
        LearningAnalytics.log_event(
            user_id=current_user_id,
            event_type='course_unenrolled',
            event_data={
                'course_id': course_id
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({'message': 'Successfully unenrolled from course'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Course unenrollment error: {str(e)}")
        return jsonify({'error': 'Failed to unenroll from course'}), 500

@courses_bp.route('/my-courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    """Get current user's enrolled courses"""
    try:
        current_user_id = get_jwt_identity()
        
        enrollments = CourseEnrollment.get_user_enrollments(current_user_id)
        
        courses_data = []
        for enrollment in enrollments:
            course_data = enrollment.to_dict()
            
            # Add progress summary
            progress_summary = UserProgress.get_course_progress_summary(
                current_user_id, 
                enrollment.course_id
            )
            course_data['progress'] = progress_summary
            
            courses_data.append(course_data)
        
        return jsonify({
            'enrollments': courses_data,
            'total': len(courses_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get my courses error: {str(e)}")
        return jsonify({'error': 'Failed to get enrolled courses'}), 500

@courses_bp.route('/<int:course_id>/progress', methods=['GET'])
@jwt_required()
def get_course_progress(course_id):
    """Get current user's progress for a specific course"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user is enrolled
        enrollment = CourseEnrollment.query.filter_by(
            user_id=current_user_id, 
            course_id=course_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Not enrolled in this course'}), 404
        
        # Get detailed progress
        progress_records = UserProgress.get_user_progress(current_user_id, course_id)
        progress_summary = UserProgress.get_course_progress_summary(current_user_id, course_id)
        
        return jsonify({
            'enrollment': enrollment.to_dict(),
            'progress_summary': progress_summary,
            'module_progress': [progress.to_dict() for progress in progress_records]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get course progress error: {str(e)}")
        return jsonify({'error': 'Failed to get course progress'}), 500

@courses_bp.route('/modules/<int:module_id>', methods=['GET'])
@jwt_required()
def get_module(module_id):
    """Get module details with content"""
    try:
        current_user_id = get_jwt_identity()
        
        module = Module.query.get(module_id)
        if not module or not module.is_active:
            return jsonify({'error': 'Module not found'}), 404
        
        # Check if user is enrolled in the course
        enrollment = CourseEnrollment.query.filter_by(
            user_id=current_user_id, 
            course_id=module.course_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Not enrolled in this course'}), 403
        
        # Get or create progress record
        progress = UserProgress.get_or_create_progress(
            current_user_id, 
            module.course_id, 
            module_id
        )
        
        # Start module if not started
        if progress.status == 'not_started':
            progress.start_module()
        
        # Log module access event
        LearningAnalytics.log_event(
            user_id=current_user_id,
            event_type='module_accessed',
            event_data={
                'module_id': module_id,
                'module_title': module.title,
                'course_id': module.course_id
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'module': module.to_dict(include_content=True),
            'progress': progress.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get module error: {str(e)}")
        return jsonify({'error': 'Failed to get module'}), 500

@courses_bp.route('/modules/<int:module_id>/complete', methods=['POST'])
@jwt_required()
def complete_module(module_id):
    """Mark module as completed"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        module = Module.query.get(module_id)
        if not module or not module.is_active:
            return jsonify({'error': 'Module not found'}), 404
        
        # Check enrollment
        enrollment = CourseEnrollment.query.filter_by(
            user_id=current_user_id, 
            course_id=module.course_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Not enrolled in this course'}), 403
        
        # Get progress record
        progress = UserProgress.get_or_create_progress(
            current_user_id, 
            module.course_id, 
            module_id
        )
        
        # Complete module
        score = data.get('score')
        time_spent = data.get('time_spent_minutes', 0)
        
        progress.complete_module(score)
        progress.update_time_spent(time_spent)
        
        # Update enrollment status
        if enrollment.status == 'enrolled':
            enrollment.start_course()
        
        # Log module completion event
        LearningAnalytics.log_event(
            user_id=current_user_id,
            event_type='module_completed',
            event_data={
                'module_id': module_id,
                'module_title': module.title,
                'course_id': module.course_id,
                'score': score,
                'time_spent_minutes': time_spent
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        # Check if course is completed
        course_progress = UserProgress.get_course_progress_summary(current_user_id, module.course_id)
        if course_progress['completion_percentage'] == 100:
            enrollment.complete_course(course_progress['average_score'])
            
            # Log course completion event
            LearningAnalytics.log_event(
                user_id=current_user_id,
                event_type='course_completed',
                event_data={
                    'course_id': module.course_id,
                    'final_score': course_progress['average_score'],
                    'total_time_minutes': course_progress['total_time_minutes']
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

# Admin endpoints (for future implementation)
@courses_bp.route('/admin/courses', methods=['POST'])
@jwt_required()
def create_course():
    """Create a new course (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'level', 'duration_hours']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        course = Course(
            title=data['title'],
            description=data['description'],
            level=data['level'],
            duration_hours=data['duration_hours'],
            passing_score=data.get('passing_score', 70),
            thumbnail_url=data.get('thumbnail_url')
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({
            'message': 'Course created successfully',
            'course': course.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create course error: {str(e)}")
        return jsonify({'error': 'Failed to create course'}), 500

@courses_bp.route('/stats', methods=['GET'])
def get_course_stats():
    """Get course statistics"""
    try:
        total_courses = Course.query.filter_by(is_active=True).count()
        total_enrollments = CourseEnrollment.query.count()
        total_completions = CourseEnrollment.query.filter_by(status='completed').count()
        
        # Course completion rate
        completion_rate = (total_completions / total_enrollments * 100) if total_enrollments > 0 else 0
        
        # Courses by level
        courses_by_level = {}
        for level in range(1, 5):
            count = Course.query.filter_by(level=level, is_active=True).count()
            courses_by_level[f'level_{level}'] = count
        
        return jsonify({
            'total_courses': total_courses,
            'total_enrollments': total_enrollments,
            'total_completions': total_completions,
            'completion_rate': round(completion_rate, 2),
            'courses_by_level': courses_by_level
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get course stats error: {str(e)}")
        return jsonify({'error': 'Failed to get course statistics'}), 500

