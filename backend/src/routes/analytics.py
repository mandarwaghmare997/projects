from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_

from src.models.user import User, db
from src.models.course import Course, CourseEnrollment
from src.models.quiz import Quiz, QuizAttempt
from src.models.progress import UserProgress, Certificate, LearningAnalytics

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_analytics_summary():
    """Get analytics summary for current user"""
    try:
        current_user_id = int(get_jwt_identity())
        days = int(request.args.get('days', 30))
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get recent activity
        recent_activities = LearningAnalytics.query.filter(
            LearningAnalytics.user_id == current_user_id,
            LearningAnalytics.timestamp >= start_date
        ).order_by(desc(LearningAnalytics.timestamp)).limit(10).all()
        
        activity_descriptions = []
        for activity in recent_activities:
            description = get_activity_description(activity)
            activity_descriptions.append({
                'description': description,
                'timestamp': activity.timestamp.strftime('%Y-%m-%d %H:%M'),
                'event_type': activity.event_type
            })
        
        # Calculate learning streak
        learning_streak = calculate_learning_streak(current_user_id)
        
        # Get study time by day
        daily_study_time = get_daily_study_time(current_user_id, days)
        
        # Get performance metrics
        performance_metrics = get_performance_metrics(current_user_id, days)
        
        # Get achievement progress
        achievements = get_achievement_progress(current_user_id)
        
        analytics_data = {
            'recent_activity': activity_descriptions,
            'learning_streak': learning_streak,
            'daily_study_time': daily_study_time,
            'performance_metrics': performance_metrics,
            'achievements': achievements
        }
        
        return jsonify(analytics_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Get analytics summary error: {str(e)}")
        return jsonify({'error': 'Failed to get analytics summary'}), 500

@analytics_bp.route('/detailed', methods=['GET'])
@jwt_required()
def get_detailed_analytics():
    """Get detailed analytics for current user"""
    try:
        current_user_id = int(get_jwt_identity())
        days = int(request.args.get('days', 30))
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Learning patterns
        learning_patterns = get_learning_patterns(current_user_id, days)
        
        # Course performance breakdown
        course_performance = get_course_performance_breakdown(current_user_id)
        
        # Quiz performance trends
        quiz_trends = get_quiz_performance_trends(current_user_id, days)
        
        # Time distribution
        time_distribution = get_time_distribution(current_user_id, days)
        
        # Skill progression
        skill_progression = get_skill_progression(current_user_id)
        
        detailed_analytics = {
            'learning_patterns': learning_patterns,
            'course_performance': course_performance,
            'quiz_trends': quiz_trends,
            'time_distribution': time_distribution,
            'skill_progression': skill_progression
        }
        
        return jsonify(detailed_analytics), 200
        
    except Exception as e:
        current_app.logger.error(f"Get detailed analytics error: {str(e)}")
        return jsonify({'error': 'Failed to get detailed analytics'}), 500

@analytics_bp.route('/log-event', methods=['POST'])
@jwt_required()
def log_analytics_event():
    """Log a custom analytics event"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        event_type = data.get('event_type')
        event_data = data.get('event_data', {})
        
        if not event_type:
            return jsonify({'error': 'Event type is required'}), 400
        
        # Log the event
        LearningAnalytics.log_event(
            user_id=current_user_id,
            event_type=event_type,
            event_data=event_data,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({'message': 'Event logged successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Log analytics event error: {str(e)}")
        return jsonify({'error': 'Failed to log event'}), 500

def get_activity_description(activity):
    """Generate human-readable description for activity"""
    event_type = activity.event_type
    event_data = activity.event_data_json
    
    if event_type == 'login':
        return "Logged into the platform"
    elif event_type == 'module_started':
        return f"Started a new module"
    elif event_type == 'module_completed':
        return f"Completed a module"
    elif event_type == 'quiz_attempt':
        return f"Attempted a quiz"
    elif event_type == 'quiz_passed':
        return f"Passed a quiz"
    elif event_type == 'course_completed':
        return f"Completed a course"
    elif event_type == 'certificate_generated':
        return f"Earned a certificate"
    else:
        return f"Performed {event_type.replace('_', ' ')}"

def calculate_learning_streak(user_id):
    """Calculate current and longest learning streak"""
    try:
        # Get all learning days (days with any learning activity)
        learning_days = db.session.query(
            func.date(LearningAnalytics.timestamp).label('learning_date')
        ).filter(
            LearningAnalytics.user_id == user_id,
            LearningAnalytics.event_type.in_([
                'module_started', 'module_completed', 'quiz_attempt'
            ])
        ).distinct().order_by(desc('learning_date')).all()
        
        if not learning_days:
            return {'current_streak': 0, 'longest_streak': 0}
        
        # Calculate current streak
        current_streak = 0
        today = datetime.utcnow().date()
        
        for i, day in enumerate(learning_days):
            expected_date = today - timedelta(days=i)
            if day.learning_date == expected_date:
                current_streak += 1
            else:
                break
        
        # Calculate longest streak
        longest_streak = 0
        current_temp_streak = 1
        
        for i in range(1, len(learning_days)):
            prev_date = learning_days[i-1].learning_date
            curr_date = learning_days[i].learning_date
            
            if (prev_date - curr_date).days == 1:
                current_temp_streak += 1
            else:
                longest_streak = max(longest_streak, current_temp_streak)
                current_temp_streak = 1
        
        longest_streak = max(longest_streak, current_temp_streak)
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak
        }
        
    except Exception as e:
        current_app.logger.error(f"Calculate learning streak error: {str(e)}")
        return {'current_streak': 0, 'longest_streak': 0}

def get_daily_study_time(user_id, days):
    """Get daily study time for the last N days"""
    try:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        # Get time spent by day
        daily_time = db.session.query(
            func.date(UserProgress.last_accessed).label('study_date'),
            func.sum(UserProgress.time_spent_minutes).label('total_minutes')
        ).filter(
            UserProgress.user_id == user_id,
            func.date(UserProgress.last_accessed) >= start_date
        ).group_by('study_date').all()
        
        # Create a complete list for all days
        daily_data = []
        for i in range(days):
            date = end_date - timedelta(days=i)
            minutes = 0
            
            for record in daily_time:
                if record.study_date == date:
                    minutes = record.total_minutes or 0
                    break
            
            daily_data.append({
                'date': date.isoformat(),
                'minutes': minutes
            })
        
        return list(reversed(daily_data))
        
    except Exception as e:
        current_app.logger.error(f"Get daily study time error: {str(e)}")
        return []

def get_performance_metrics(user_id, days):
    """Get performance metrics for the last N days"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Quiz performance
        quiz_attempts = QuizAttempt.query.filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.attempted_at >= start_date
        ).all()
        
        total_attempts = len(quiz_attempts)
        passed_attempts = len([a for a in quiz_attempts if a.passed])
        pass_rate = (passed_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        scores = [a.score for a in quiz_attempts if a.score is not None]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Module completion
        completed_modules = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            UserProgress.status == 'completed',
            UserProgress.completed_at >= start_date
        ).count()
        
        return {
            'quiz_attempts': total_attempts,
            'quiz_pass_rate': round(pass_rate, 1),
            'average_score': round(average_score, 1),
            'modules_completed': completed_modules
        }
        
    except Exception as e:
        current_app.logger.error(f"Get performance metrics error: {str(e)}")
        return {}

def get_achievement_progress(user_id):
    """Get achievement progress for user"""
    try:
        # Define achievements
        achievements = [
            {
                'id': 'first_course',
                'title': 'First Steps',
                'description': 'Complete your first course',
                'icon': '🎯',
                'target': 1,
                'current': 0
            },
            {
                'id': 'quiz_master',
                'title': 'Quiz Master',
                'description': 'Pass 10 quizzes',
                'icon': '🧠',
                'target': 10,
                'current': 0
            },
            {
                'id': 'time_keeper',
                'title': 'Time Keeper',
                'description': 'Study for 100 hours',
                'icon': '⏰',
                'target': 6000,  # 100 hours in minutes
                'current': 0
            },
            {
                'id': 'certificate_collector',
                'title': 'Certificate Collector',
                'description': 'Earn 5 certificates',
                'icon': '🏆',
                'target': 5,
                'current': 0
            }
        ]
        
        # Calculate current progress
        completed_courses = CourseEnrollment.query.filter_by(
            user_id=user_id, status='completed'
        ).count()
        
        passed_quizzes = QuizAttempt.query.filter_by(
            user_id=user_id, passed=True
        ).count()
        
        total_time = db.session.query(func.sum(UserProgress.time_spent_minutes))\
            .filter_by(user_id=user_id).scalar() or 0
        
        certificates = Certificate.query.filter_by(
            user_id=user_id, is_valid=True
        ).count()
        
        # Update achievement progress
        achievements[0]['current'] = completed_courses
        achievements[1]['current'] = passed_quizzes
        achievements[2]['current'] = total_time
        achievements[3]['current'] = certificates
        
        # Mark completed achievements
        for achievement in achievements:
            achievement['completed'] = achievement['current'] >= achievement['target']
            achievement['progress_percentage'] = min(100, 
                (achievement['current'] / achievement['target']) * 100)
        
        return achievements
        
    except Exception as e:
        current_app.logger.error(f"Get achievement progress error: {str(e)}")
        return []

def get_learning_patterns(user_id, days):
    """Analyze learning patterns"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get activity by hour of day
        hourly_activity = db.session.query(
            func.extract('hour', LearningAnalytics.timestamp).label('hour'),
            func.count(LearningAnalytics.id).label('activity_count')
        ).filter(
            LearningAnalytics.user_id == user_id,
            LearningAnalytics.timestamp >= start_date
        ).group_by('hour').all()
        
        # Get activity by day of week
        weekly_activity = db.session.query(
            func.extract('dow', LearningAnalytics.timestamp).label('day_of_week'),
            func.count(LearningAnalytics.id).label('activity_count')
        ).filter(
            LearningAnalytics.user_id == user_id,
            LearningAnalytics.timestamp >= start_date
        ).group_by('day_of_week').all()
        
        return {
            'hourly_activity': [
                {'hour': int(row.hour), 'count': row.activity_count}
                for row in hourly_activity
            ],
            'weekly_activity': [
                {'day': int(row.day_of_week), 'count': row.activity_count}
                for row in weekly_activity
            ]
        }
        
    except Exception as e:
        current_app.logger.error(f"Get learning patterns error: {str(e)}")
        return {}

def get_course_performance_breakdown(user_id):
    """Get performance breakdown by course"""
    try:
        enrollments = CourseEnrollment.query.filter_by(user_id=user_id)\
            .join(Course).all()
        
        course_data = []
        for enrollment in enrollments:
            course = enrollment.course
            
            # Get quiz performance for this course
            quiz_attempts = QuizAttempt.query.join(Quiz)\
                .filter(Quiz.course_id == course.id, QuizAttempt.user_id == user_id)\
                .all()
            
            scores = [a.score for a in quiz_attempts if a.score is not None]
            average_score = sum(scores) / len(scores) if scores else 0
            
            # Get time spent
            total_time = db.session.query(func.sum(UserProgress.time_spent_minutes))\
                .filter_by(user_id=user_id, course_id=course.id).scalar() or 0
            
            course_data.append({
                'course_id': course.id,
                'course_title': course.title,
                'level': course.level,
                'enrollment_status': enrollment.status,
                'average_score': round(average_score, 1),
                'time_spent_minutes': total_time,
                'quiz_attempts': len(quiz_attempts)
            })
        
        return course_data
        
    except Exception as e:
        current_app.logger.error(f"Get course performance breakdown error: {str(e)}")
        return []

def get_quiz_performance_trends(user_id, days):
    """Get quiz performance trends over time"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        quiz_attempts = QuizAttempt.query.filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.attempted_at >= start_date
        ).order_by(QuizAttempt.attempted_at).all()
        
        trends = []
        for attempt in quiz_attempts:
            trends.append({
                'date': attempt.attempted_at.date().isoformat(),
                'score': attempt.score,
                'passed': attempt.passed,
                'quiz_title': attempt.quiz.title
            })
        
        return trends
        
    except Exception as e:
        current_app.logger.error(f"Get quiz performance trends error: {str(e)}")
        return []

def get_time_distribution(user_id, days):
    """Get time distribution across different activities"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Time spent by course
        course_time = db.session.query(
            Course.title,
            func.sum(UserProgress.time_spent_minutes).label('total_time')
        ).join(UserProgress, Course.id == UserProgress.course_id)\
         .filter(
             UserProgress.user_id == user_id,
             UserProgress.last_accessed >= start_date
         ).group_by(Course.title).all()
        
        return {
            'by_course': [
                {'course': row.title, 'minutes': row.total_time}
                for row in course_time
            ]
        }
        
    except Exception as e:
        current_app.logger.error(f"Get time distribution error: {str(e)}")
        return {}

def get_skill_progression(user_id):
    """Get skill progression based on course levels and scores"""
    try:
        # Get completed courses with scores
        completed_courses = db.session.query(
            Course.level,
            CourseEnrollment.final_score,
            CourseEnrollment.completed_at
        ).join(CourseEnrollment, Course.id == CourseEnrollment.course_id)\
         .filter(
             CourseEnrollment.user_id == user_id,
             CourseEnrollment.status == 'completed'
         ).order_by(CourseEnrollment.completed_at).all()
        
        skill_levels = {
            1: {'name': 'Foundation', 'completed': 0, 'average_score': 0},
            2: {'name': 'Practitioner', 'completed': 0, 'average_score': 0},
            3: {'name': 'Lead Implementer', 'completed': 0, 'average_score': 0},
            4: {'name': 'Auditor/Assessor', 'completed': 0, 'average_score': 0}
        }
        
        for course in completed_courses:
            level = course.level
            if level in skill_levels:
                skill_levels[level]['completed'] += 1
                if course.final_score:
                    current_avg = skill_levels[level]['average_score']
                    count = skill_levels[level]['completed']
                    skill_levels[level]['average_score'] = (
                        (current_avg * (count - 1) + course.final_score) / count
                    )
        
        return [
            {
                'level': level,
                'name': data['name'],
                'completed_courses': data['completed'],
                'average_score': round(data['average_score'], 1)
            }
            for level, data in skill_levels.items()
        ]
        
    except Exception as e:
        current_app.logger.error(f"Get skill progression error: {str(e)}")
        return []

