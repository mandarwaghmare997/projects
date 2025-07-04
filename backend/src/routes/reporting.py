"""
Advanced Reporting and Analytics Routes for Qryti Learn Enterprise
Provides comprehensive business intelligence and learning analytics
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, desc, asc
from ..models.user import db, User
from ..models.admin import AdminUser, Organization
from ..models.course import Course, Module, CourseEnrollment
from ..models.quiz import Quiz, QuizAttempt
from ..models.progress import UserProgress, Certificate, LearningAnalytics
from ..models.video import VideoProgress
from ..models.knowledge_base import KnowledgeResource, ResourceDownload
import json

reporting_bp = Blueprint('reporting', __name__)

def require_analytics_permission():
    """Decorator to require analytics viewing permissions"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            admin_user = AdminUser.query.filter_by(user_id=current_user_id, is_active=True).first()
            if not admin_user or not admin_user.can_view_analytics:
                return jsonify({'error': 'Analytics permission required'}), 403
            
            return f(admin_user, *args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# User Analytics
@reporting_bp.route('/users/overview', methods=['GET'])
@jwt_required()
@require_analytics_permission()
def user_analytics_overview(admin_user):
    """Get comprehensive user analytics overview"""
    try:
        # Date range parameters
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Organization filter
        org_filter = {}
        if not admin_user.is_super_admin and admin_user.organization_id:
            org_filter['organization_id'] = admin_user.organization_id
        
        # Total users
        total_users = User.query.filter_by(**org_filter).count()
        active_users = User.query.filter_by(is_active=True, **org_filter).count()
        
        # New users over time
        new_users_query = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= start_date,
            **{k: v for k, v in org_filter.items() if k in User.__table__.columns}
        ).group_by(func.date(User.created_at)).order_by('date')
        
        new_users_data = [
            {'date': str(row.date), 'count': row.count}
            for row in new_users_query.all()
        ]
        
        # User activity metrics
        active_users_last_7_days = User.query.filter(
            User.last_login >= datetime.utcnow() - timedelta(days=7),
            **{k: v for k, v in org_filter.items() if k in User.__table__.columns}
        ).count()
        
        active_users_last_30_days = User.query.filter(
            User.last_login >= datetime.utcnow() - timedelta(days=30),
            **{k: v for k, v in org_filter.items() if k in User.__table__.columns}
        ).count()
        
        # User engagement metrics
        enrolled_users = db.session.query(func.count(func.distinct(CourseEnrollment.user_id))).scalar() or 0
        quiz_takers = db.session.query(func.count(func.distinct(QuizAttempt.user_id))).scalar() or 0
        certificate_earners = db.session.query(func.count(func.distinct(Certificate.user_id))).scalar() or 0
        
        return jsonify({
            'overview': {
                'total_users': total_users,
                'active_users': active_users,
                'active_last_7_days': active_users_last_7_days,
                'active_last_30_days': active_users_last_30_days,
                'engagement': {
                    'enrolled_users': enrolled_users,
                    'quiz_takers': quiz_takers,
                    'certificate_earners': certificate_earners
                }
            },
            'trends': {
                'new_users': new_users_data
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reporting_bp.route('/users/engagement', methods=['GET'])
@jwt_required()
@require_analytics_permission()
def user_engagement_report(admin_user):
    """Get detailed user engagement analytics"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Course enrollment trends
        enrollment_trends = db.session.query(
            func.date(CourseEnrollment.enrolled_at).label('date'),
            func.count(CourseEnrollment.id).label('enrollments')
        ).filter(
            CourseEnrollment.enrolled_at >= start_date
        ).group_by(func.date(CourseEnrollment.enrolled_at)).order_by('date').all()
        
        # Quiz completion trends
        quiz_trends = db.session.query(
            func.date(QuizAttempt.started_at).label('date'),
            func.count(QuizAttempt.id).label('attempts'),
            func.avg(QuizAttempt.score).label('avg_score')
        ).filter(
            QuizAttempt.started_at >= start_date,
            QuizAttempt.completed_at.isnot(None)
        ).group_by(func.date(QuizAttempt.started_at)).order_by('date').all()
        
        # Video engagement
        video_engagement = db.session.query(
            func.date(VideoProgress.last_watched).label('date'),
            func.count(func.distinct(VideoProgress.user_id)).label('viewers'),
            func.avg(VideoProgress.progress_percentage).label('avg_progress')
        ).filter(
            VideoProgress.last_watched >= start_date
        ).group_by(func.date(VideoProgress.last_watched)).order_by('date').all()
        
        # Resource downloads
        resource_downloads = db.session.query(
            func.date(ResourceDownload.downloaded_at).label('date'),
            func.count(ResourceDownload.id).label('downloads')
        ).filter(
            ResourceDownload.downloaded_at >= start_date
        ).group_by(func.date(ResourceDownload.downloaded_at)).order_by('date').all()
        
        return jsonify({
            'enrollment_trends': [
                {'date': str(row.date), 'enrollments': row.enrollments}
                for row in enrollment_trends
            ],
            'quiz_trends': [
                {
                    'date': str(row.date),
                    'attempts': row.attempts,
                    'avg_score': float(row.avg_score) if row.avg_score else 0
                }
                for row in quiz_trends
            ],
            'video_engagement': [
                {
                    'date': str(row.date),
                    'viewers': row.viewers,
                    'avg_progress': float(row.avg_progress) if row.avg_progress else 0
                }
                for row in video_engagement
            ],
            'resource_downloads': [
                {'date': str(row.date), 'downloads': row.downloads}
                for row in resource_downloads
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Content Analytics
@reporting_bp.route('/content/performance', methods=['GET'])
@jwt_required()
@require_analytics_permission()
def content_performance_report(admin_user):
    """Get content performance analytics"""
    try:
        # Course performance
        course_stats = db.session.query(
            Course.id,
            Course.title,
            func.count(CourseEnrollment.id).label('enrollments'),
            func.count(UserProgress.id).label('completions'),
            func.avg(QuizAttempt.score).label('avg_quiz_score')
        ).outerjoin(CourseEnrollment).outerjoin(UserProgress).outerjoin(
            QuizAttempt, and_(
                QuizAttempt.user_id == CourseEnrollment.user_id,
                QuizAttempt.completed_at.isnot(None)
            )
        ).group_by(Course.id, Course.title).all()
        
        # Quiz performance
        quiz_stats = db.session.query(
            Quiz.id,
            Quiz.title,
            func.count(QuizAttempt.id).label('attempts'),
            func.count(QuizAttempt.id.distinct()).filter(QuizAttempt.completed_at.isnot(None)).label('completions'),
            func.avg(QuizAttempt.score).label('avg_score'),
            func.min(QuizAttempt.score).label('min_score'),
            func.max(QuizAttempt.score).label('max_score')
        ).outerjoin(QuizAttempt).group_by(Quiz.id, Quiz.title).all()
        
        # Video performance
        video_stats = db.session.query(
            Video.id,
            Video.title,
            func.count(VideoProgress.id).label('views'),
            func.avg(VideoProgress.progress_percentage).label('avg_completion'),
            func.sum(VideoProgress.watch_time_seconds).label('total_watch_time')
        ).outerjoin(VideoProgress).group_by(Video.id, Video.title).all()
        
        # Resource performance
        resource_stats = db.session.query(
            KnowledgeResource.id,
            KnowledgeResource.title,
            func.count(ResourceDownload.id).label('downloads'),
            func.avg(KnowledgeResource.rating).label('avg_rating')
        ).outerjoin(ResourceDownload).group_by(
            KnowledgeResource.id, KnowledgeResource.title
        ).all()
        
        return jsonify({
            'courses': [
                {
                    'id': row.id,
                    'title': row.title,
                    'enrollments': row.enrollments or 0,
                    'completions': row.completions or 0,
                    'completion_rate': (row.completions / row.enrollments * 100) if row.enrollments else 0,
                    'avg_quiz_score': float(row.avg_quiz_score) if row.avg_quiz_score else 0
                }
                for row in course_stats
            ],
            'quizzes': [
                {
                    'id': row.id,
                    'title': row.title,
                    'attempts': row.attempts or 0,
                    'completions': row.completions or 0,
                    'completion_rate': (row.completions / row.attempts * 100) if row.attempts else 0,
                    'avg_score': float(row.avg_score) if row.avg_score else 0,
                    'min_score': float(row.min_score) if row.min_score else 0,
                    'max_score': float(row.max_score) if row.max_score else 0
                }
                for row in quiz_stats
            ],
            'videos': [
                {
                    'id': row.id,
                    'title': row.title,
                    'views': row.views or 0,
                    'avg_completion': float(row.avg_completion) if row.avg_completion else 0,
                    'total_watch_time': row.total_watch_time or 0
                }
                for row in video_stats
            ],
            'resources': [
                {
                    'id': row.id,
                    'title': row.title,
                    'downloads': row.downloads or 0,
                    'avg_rating': float(row.avg_rating) if row.avg_rating else 0
                }
                for row in resource_stats
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Learning Analytics
@reporting_bp.route('/learning/progress', methods=['GET'])
@jwt_required()
@require_analytics_permission()
def learning_progress_report(admin_user):
    """Get learning progress analytics"""
    try:
        # Overall progress statistics
        total_enrollments = CourseEnrollment.query.count()
        completed_courses = UserProgress.query.filter_by(completion_status='completed').count()
        in_progress_courses = UserProgress.query.filter_by(completion_status='in_progress').count()
        
        # Average completion time
        avg_completion_time = db.session.query(
            func.avg(
                func.extract('epoch', UserProgress.completed_at - CourseEnrollment.enrolled_at) / 86400
            )
        ).join(CourseEnrollment).filter(
            UserProgress.completion_status == 'completed'
        ).scalar()
        
        # Learning path analysis
        learning_paths = db.session.query(
            Course.title,
            func.count(CourseEnrollment.id).label('enrollments'),
            func.count(UserProgress.id).filter(UserProgress.completion_status == 'completed').label('completions'),
            func.avg(UserProgress.progress_percentage).label('avg_progress')
        ).outerjoin(CourseEnrollment).outerjoin(UserProgress).group_by(Course.id, Course.title).all()
        
        # Skill development tracking
        skill_progress = db.session.query(
            LearningAnalytics.skill_area,
            func.avg(LearningAnalytics.proficiency_score).label('avg_proficiency'),
            func.count(LearningAnalytics.id).label('assessments')
        ).group_by(LearningAnalytics.skill_area).all()
        
        # Certificate achievements
        certificate_stats = db.session.query(
            Certificate.certificate_type,
            func.count(Certificate.id).label('issued'),
            func.count(Certificate.id).filter(Certificate.is_verified == True).label('verified')
        ).group_by(Certificate.certificate_type).all()
        
        return jsonify({
            'overview': {
                'total_enrollments': total_enrollments,
                'completed_courses': completed_courses,
                'in_progress_courses': in_progress_courses,
                'completion_rate': (completed_courses / total_enrollments * 100) if total_enrollments else 0,
                'avg_completion_days': float(avg_completion_time) if avg_completion_time else 0
            },
            'learning_paths': [
                {
                    'course': row.title,
                    'enrollments': row.enrollments or 0,
                    'completions': row.completions or 0,
                    'completion_rate': (row.completions / row.enrollments * 100) if row.enrollments else 0,
                    'avg_progress': float(row.avg_progress) if row.avg_progress else 0
                }
                for row in learning_paths
            ],
            'skill_development': [
                {
                    'skill_area': row.skill_area,
                    'avg_proficiency': float(row.avg_proficiency) if row.avg_proficiency else 0,
                    'assessments': row.assessments or 0
                }
                for row in skill_progress
            ],
            'certificates': [
                {
                    'type': row.certificate_type,
                    'issued': row.issued or 0,
                    'verified': row.verified or 0,
                    'verification_rate': (row.verified / row.issued * 100) if row.issued else 0
                }
                for row in certificate_stats
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Business Intelligence
@reporting_bp.route('/business/kpis', methods=['GET'])
@jwt_required()
@require_analytics_permission()
def business_kpis(admin_user):
    """Get key business performance indicators"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # User growth metrics
        new_users_period = User.query.filter(User.created_at >= start_date).count()
        total_users = User.query.count()
        active_users = User.query.filter(User.last_login >= start_date).count()
        
        # Engagement metrics
        course_enrollments = CourseEnrollment.query.filter(CourseEnrollment.enrolled_at >= start_date).count()
        quiz_attempts = QuizAttempt.query.filter(QuizAttempt.started_at >= start_date).count()
        certificates_issued = Certificate.query.filter(Certificate.issued_at >= start_date).count()
        
        # Content consumption
        video_views = VideoProgress.query.filter(VideoProgress.last_watched >= start_date).count()
        resource_downloads = ResourceDownload.query.filter(ResourceDownload.downloaded_at >= start_date).count()
        
        # Learning outcomes
        course_completions = UserProgress.query.filter(
            UserProgress.completed_at >= start_date,
            UserProgress.completion_status == 'completed'
        ).count()
        
        quiz_pass_rate = db.session.query(
            func.count(QuizAttempt.id).filter(QuizAttempt.score >= 70).label('passed'),
            func.count(QuizAttempt.id).label('total')
        ).filter(
            QuizAttempt.started_at >= start_date,
            QuizAttempt.completed_at.isnot(None)
        ).first()
        
        # Calculate growth rates (compared to previous period)
        prev_start_date = start_date - timedelta(days=days)
        prev_new_users = User.query.filter(
            User.created_at >= prev_start_date,
            User.created_at < start_date
        ).count()
        
        user_growth_rate = ((new_users_period - prev_new_users) / prev_new_users * 100) if prev_new_users else 0
        
        return jsonify({
            'period_days': days,
            'user_metrics': {
                'new_users': new_users_period,
                'total_users': total_users,
                'active_users': active_users,
                'user_growth_rate': round(user_growth_rate, 2),
                'activation_rate': round((active_users / total_users * 100), 2) if total_users else 0
            },
            'engagement_metrics': {
                'course_enrollments': course_enrollments,
                'quiz_attempts': quiz_attempts,
                'certificates_issued': certificates_issued,
                'video_views': video_views,
                'resource_downloads': resource_downloads
            },
            'learning_outcomes': {
                'course_completions': course_completions,
                'quiz_pass_rate': round((quiz_pass_rate.passed / quiz_pass_rate.total * 100), 2) if quiz_pass_rate.total else 0,
                'completion_rate': round((course_completions / course_enrollments * 100), 2) if course_enrollments else 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Custom Reports
@reporting_bp.route('/custom/user-cohort', methods=['GET'])
@jwt_required()
@require_analytics_permission()
def user_cohort_analysis(admin_user):
    """Generate user cohort analysis report"""
    try:
        # Get cohort parameters
        cohort_period = request.args.get('period', 'month')  # week, month, quarter
        
        # Define cohort grouping based on registration date
        if cohort_period == 'week':
            date_trunc = func.date_trunc('week', User.created_at)
        elif cohort_period == 'quarter':
            date_trunc = func.date_trunc('quarter', User.created_at)
        else:  # month
            date_trunc = func.date_trunc('month', User.created_at)
        
        # Get user cohorts
        cohorts = db.session.query(
            date_trunc.label('cohort_period'),
            func.count(User.id).label('users')
        ).group_by(date_trunc).order_by(date_trunc).all()
        
        # Calculate retention for each cohort
        cohort_data = []
        for cohort in cohorts:
            cohort_start = cohort.cohort_period
            
            # Calculate retention at different intervals
            retention_data = {}
            for weeks in [1, 2, 4, 8, 12, 24]:
                retention_date = cohort_start + timedelta(weeks=weeks)
                retained_users = User.query.filter(
                    date_trunc == cohort_start,
                    User.last_login >= retention_date
                ).count()
                
                retention_data[f'week_{weeks}'] = {
                    'retained': retained_users,
                    'rate': round((retained_users / cohort.users * 100), 2) if cohort.users else 0
                }
            
            cohort_data.append({
                'cohort_period': cohort_start.isoformat(),
                'initial_users': cohort.users,
                'retention': retention_data
            })
        
        return jsonify({
            'cohort_period': cohort_period,
            'cohorts': cohort_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reporting_bp.route('/export/users', methods=['GET'])
@jwt_required()
@require_analytics_permission()
def export_user_report(admin_user):
    """Export user data for Excel/CSV analysis"""
    try:
        # Get export parameters
        format_type = request.args.get('format', 'json')  # json, csv
        include_progress = request.args.get('include_progress', 'false').lower() == 'true'
        
        # Organization filter
        org_filter = {}
        if not admin_user.is_super_admin and admin_user.organization_id:
            org_filter['organization_id'] = admin_user.organization_id
        
        # Get user data
        users_query = User.query.filter_by(**org_filter)
        
        user_data = []
        for user in users_query.all():
            user_info = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
            
            if include_progress:
                # Add learning progress data
                enrollments = CourseEnrollment.query.filter_by(user_id=user.id).count()
                completions = UserProgress.query.filter_by(
                    user_id=user.id, 
                    completion_status='completed'
                ).count()
                certificates = Certificate.query.filter_by(user_id=user.id).count()
                
                user_info.update({
                    'course_enrollments': enrollments,
                    'course_completions': completions,
                    'certificates_earned': certificates,
                    'completion_rate': round((completions / enrollments * 100), 2) if enrollments else 0
                })
            
            user_data.append(user_info)
        
        return jsonify({
            'format': format_type,
            'exported_at': datetime.utcnow().isoformat(),
            'total_records': len(user_data),
            'data': user_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

