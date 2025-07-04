from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from src.models.user import User, db
from src.models.course import Course, CourseEnrollment
from src.models.progress import UserProgress, LearningAnalytics

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get user's learning dashboard data"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get user's enrollments
        enrollments = CourseEnrollment.get_user_enrollments(current_user_id)
        
        # Calculate overall statistics
        total_courses = len(enrollments)
        completed_courses = len([e for e in enrollments if e.status == 'completed'])
        in_progress_courses = len([e for e in enrollments if e.status == 'in_progress'])
        
        # Get recent activity
        recent_progress = UserProgress.query.filter_by(user_id=current_user_id)\
            .order_by(UserProgress.last_accessed.desc()).limit(5).all()
        
        # Calculate total learning time
        total_time = db.session.query(db.func.sum(UserProgress.time_spent_minutes))\
            .filter_by(user_id=current_user_id).scalar() or 0
        
        # Get course progress summaries
        course_progress = []
        for enrollment in enrollments:
            progress_summary = UserProgress.get_course_progress_summary(
                current_user_id, enrollment.course_id
            )
            course_data = {
                'enrollment': enrollment.to_dict(),
                'progress': progress_summary
            }
            course_progress.append(course_data)
        
        return jsonify({
            'overview': {
                'total_courses': total_courses,
                'completed_courses': completed_courses,
                'in_progress_courses': in_progress_courses,
                'completion_rate': (completed_courses / total_courses * 100) if total_courses > 0 else 0,
                'total_learning_time_minutes': total_time,
                'total_learning_time_hours': round(total_time / 60, 1)
            },
            'course_progress': course_progress,
            'recent_activity': [progress.to_dict() for progress in recent_progress]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get dashboard error: {str(e)}")
        return jsonify({'error': 'Failed to get dashboard data'}), 500

@progress_bp.route('/course/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_progress(course_id):
    """Get detailed progress for a specific course"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check enrollment
        enrollment = CourseEnrollment.query.filter_by(
            user_id=current_user_id, course_id=course_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Not enrolled in this course'}), 404
        
        # Get progress records
        progress_records = UserProgress.get_user_progress(current_user_id, course_id)
        progress_summary = UserProgress.get_course_progress_summary(current_user_id, course_id)
        
        # Get course details
        course = Course.query.get(course_id)
        
        return jsonify({
            'course': course.to_dict() if course else None,
            'enrollment': enrollment.to_dict(),
            'progress_summary': progress_summary,
            'module_progress': [progress.to_dict() for progress in progress_records]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get course progress error: {str(e)}")
        return jsonify({'error': 'Failed to get course progress'}), 500

@progress_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_learning_analytics():
    """Get user's learning analytics"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        event_type = request.args.get('event_type')
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get analytics data
        query = LearningAnalytics.query.filter(
            LearningAnalytics.user_id == current_user_id,
            LearningAnalytics.timestamp >= start_date,
            LearningAnalytics.timestamp <= end_date
        )
        
        if event_type:
            query = query.filter(LearningAnalytics.event_type == event_type)
        
        analytics = query.order_by(LearningAnalytics.timestamp.desc()).limit(100).all()
        
        # Calculate activity summary
        activity_by_day = {}
        event_counts = {}
        
        for record in analytics:
            day_key = record.timestamp.strftime('%Y-%m-%d')
            activity_by_day[day_key] = activity_by_day.get(day_key, 0) + 1
            event_counts[record.event_type] = event_counts.get(record.event_type, 0) + 1
        
        return jsonify({
            'analytics': [record.to_dict() for record in analytics],
            'summary': {
                'total_events': len(analytics),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                },
                'activity_by_day': activity_by_day,
                'event_counts': event_counts
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get learning analytics error: {str(e)}")
        return jsonify({'error': 'Failed to get learning analytics'}), 500

@progress_bp.route('/module/<int:module_id>/time', methods=['POST'])
@jwt_required()
def update_time_spent(module_id):
    """Update time spent on a module"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        additional_minutes = data.get('minutes', 0)
        if additional_minutes <= 0:
            return jsonify({'error': 'Invalid time value'}), 400
        
        # Get or create progress record
        progress = UserProgress.query.filter_by(
            user_id=current_user_id, module_id=module_id
        ).first()
        
        if not progress:
            return jsonify({'error': 'Module progress not found'}), 404
        
        # Update time spent
        progress.update_time_spent(additional_minutes)
        
        # Log time tracking event
        LearningAnalytics.log_event(
            user_id=current_user_id,
            event_type='time_tracked',
            event_data={
                'module_id': module_id,
                'additional_minutes': additional_minutes,
                'total_minutes': progress.time_spent_minutes
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'message': 'Time updated successfully',
            'progress': progress.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update time spent error: {str(e)}")
        return jsonify({'error': 'Failed to update time spent'}), 500

@progress_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_progress_stats():
    """Get user's progress statistics"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get overall statistics
        total_enrollments = CourseEnrollment.query.filter_by(user_id=current_user_id).count()
        completed_courses = CourseEnrollment.query.filter_by(
            user_id=current_user_id, status='completed'
        ).count()
        
        # Get total modules and completed modules
        total_progress = UserProgress.query.filter_by(user_id=current_user_id).count()
        completed_modules = UserProgress.query.filter_by(
            user_id=current_user_id, status='completed'
        ).count()
        
        # Get total learning time
        total_time = db.session.query(db.func.sum(UserProgress.time_spent_minutes))\
            .filter_by(user_id=current_user_id).scalar() or 0
        
        # Get average scores
        avg_score = db.session.query(db.func.avg(UserProgress.score))\
            .filter(UserProgress.user_id == current_user_id, UserProgress.score.isnot(None))\
            .scalar() or 0
        
        # Get learning streak (consecutive days with activity)
        recent_activity = LearningAnalytics.query.filter_by(user_id=current_user_id)\
            .order_by(LearningAnalytics.timestamp.desc()).limit(30).all()
        
        # Calculate streak
        streak_days = 0
        current_date = datetime.utcnow().date()
        activity_dates = set()
        
        for activity in recent_activity:
            activity_dates.add(activity.timestamp.date())
        
        # Count consecutive days from today backwards
        check_date = current_date
        while check_date in activity_dates:
            streak_days += 1
            check_date -= timedelta(days=1)
        
        return jsonify({
            'courses': {
                'total_enrolled': total_enrollments,
                'completed': completed_courses,
                'completion_rate': (completed_courses / total_enrollments * 100) if total_enrollments > 0 else 0
            },
            'modules': {
                'total_accessed': total_progress,
                'completed': completed_modules,
                'completion_rate': (completed_modules / total_progress * 100) if total_progress > 0 else 0
            },
            'learning_time': {
                'total_minutes': total_time,
                'total_hours': round(total_time / 60, 1),
                'average_per_session': round(total_time / total_progress, 1) if total_progress > 0 else 0
            },
            'performance': {
                'average_score': round(avg_score, 1) if avg_score else 0,
                'learning_streak_days': streak_days
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get progress stats error: {str(e)}")
        return jsonify({'error': 'Failed to get progress statistics'}), 500

