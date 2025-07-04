"""
Admin API Routes for Qryti Learn Enterprise
Handles admin authentication, user management, and content administration
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from datetime import datetime, timedelta
from ..models.user import db, User
from ..models.admin import Organization, AdminUser, AuditLog, SystemSettings
from ..models.course import Course, Module
from ..models.quiz import Quiz, Question
from ..models.knowledge_base import ResourceCategory, KnowledgeResource
from ..models.video import Video
import json

admin_bp = Blueprint('admin', __name__)

def require_admin_permission(permission=None):
    """Decorator to require admin permissions"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            admin_user = AdminUser.query.filter_by(user_id=current_user_id, is_active=True).first()
            if not admin_user:
                return jsonify({'error': 'Admin access required'}), 403
            
            if permission and not admin_user.has_permission(permission) and not admin_user.is_super_admin:
                return jsonify({'error': f'Permission {permission} required'}), 403
            
            return f(admin_user, *args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

def log_admin_action(admin_user, action, resource_type=None, resource_id=None, description=None, metadata=None):
    """Log admin action for audit trail"""
    try:
        audit_log = AuditLog(
            admin_user_id=admin_user.id,
            organization_id=admin_user.organization_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            metadata=metadata or {},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Failed to log admin action: {e}")

# Admin Authentication
@admin_bp.route('/auth/login', methods=['POST'])
def admin_login():
    """Admin login with elevated permissions check"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user is admin
        admin_user = AdminUser.query.filter_by(user_id=user.id, is_active=True).first()
        if not admin_user:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Update last login
        admin_user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=8)  # Longer session for admin
        )
        
        log_admin_action(admin_user, 'admin_login', description='Admin user logged in')
        
        return jsonify({
            'access_token': access_token,
            'admin_user': admin_user.to_dict(),
            'organization': admin_user.organization.to_dict() if admin_user.organization else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Dashboard Overview
@admin_bp.route('/dashboard/overview', methods=['GET'])
@jwt_required()
@require_admin_permission()
def admin_dashboard_overview(admin_user):
    """Get admin dashboard overview statistics"""
    try:
        # Get organization filter
        org_filter = {}
        if not admin_user.is_super_admin and admin_user.organization_id:
            org_filter['organization_id'] = admin_user.organization_id
        
        # User statistics
        total_users = User.query.filter_by(**org_filter).count()
        active_users = User.query.filter_by(is_active=True, **org_filter).count()
        new_users_this_month = User.query.filter(
            User.created_at >= datetime.utcnow().replace(day=1),
            **{k: v for k, v in org_filter.items() if k in User.__table__.columns}
        ).count()
        
        # Content statistics
        total_courses = Course.query.count()
        total_modules = Module.query.count()
        total_quizzes = Quiz.query.count()
        total_videos = VideoModule.query.count()
        total_resources = KnowledgeResource.query.count()
        
        # Recent activity
        recent_users = User.query.filter_by(**org_filter).order_by(User.created_at.desc()).limit(5).all()
        recent_audit_logs = AuditLog.query.filter_by(
            organization_id=admin_user.organization_id if not admin_user.is_super_admin else None
        ).order_by(AuditLog.created_at.desc()).limit(10).all()
        
        return jsonify({
            'statistics': {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'new_this_month': new_users_this_month
                },
                'content': {
                    'courses': total_courses,
                    'modules': total_modules,
                    'quizzes': total_quizzes,
                    'videos': total_videos,
                    'resources': total_resources
                }
            },
            'recent_users': [user.to_dict() for user in recent_users],
            'recent_activity': [log.to_dict() for log in recent_audit_logs]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Management
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@require_admin_permission('manage_users')
def get_users(admin_user):
    """Get list of users with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '')
        status = request.args.get('status', '')  # active, inactive
        role = request.args.get('role', '')
        
        # Build query
        query = User.query
        
        # Organization filter for non-super admins
        if not admin_user.is_super_admin and admin_user.organization_id:
            query = query.filter_by(organization_id=admin_user.organization_id)
        
        # Search filter
        if search:
            query = query.filter(
                db.or_(
                    User.first_name.ilike(f'%{search}%'),
                    User.last_name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%')
                )
            )
        
        # Status filter
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
        
        # Role filter
        if role == 'admin':
            admin_user_ids = [au.user_id for au in AdminUser.query.filter_by(is_active=True).all()]
            query = query.filter(User.id.in_(admin_user_ids))
        elif role == 'user':
            admin_user_ids = [au.user_id for au in AdminUser.query.filter_by(is_active=True).all()]
            query = query.filter(~User.id.in_(admin_user_ids))
        
        # Pagination
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@require_admin_permission('manage_users')
def get_user_details(admin_user, user_id):
    """Get detailed user information"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Check organization access
        if not admin_user.is_super_admin and admin_user.organization_id:
            if user.organization_id != admin_user.organization_id:
                return jsonify({'error': 'Access denied'}), 403
        
        # Get user's admin profile if exists
        user_admin_profile = AdminUser.query.filter_by(user_id=user.id).first()
        
        # Get user's progress and activity
        # This would include course progress, quiz attempts, etc.
        
        return jsonify({
            'user': user.to_dict(),
            'admin_profile': user_admin_profile.to_dict() if user_admin_profile else None,
            'statistics': {
                # Add user-specific statistics here
                'courses_enrolled': 0,  # Placeholder
                'quizzes_completed': 0,  # Placeholder
                'certificates_earned': 0  # Placeholder
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@require_admin_permission('manage_users')
def update_user(admin_user, user_id):
    """Update user information"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Check organization access
        if not admin_user.is_super_admin and admin_user.organization_id:
            if user.organization_id != admin_user.organization_id:
                return jsonify({'error': 'Access denied'}), 403
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'email', 'is_active']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_admin_action(
            admin_user, 'update_user', 'user', user.id,
            f'Updated user {user.email}',
            {'updated_fields': list(data.keys())}
        )
        
        return jsonify({'user': user.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/admin', methods=['POST'])
@jwt_required()
@require_admin_permission('manage_organization')
def make_user_admin(admin_user, user_id):
    """Grant admin privileges to a user"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Check if user already has admin profile
        existing_admin = AdminUser.query.filter_by(user_id=user.id).first()
        if existing_admin:
            return jsonify({'error': 'User is already an admin'}), 400
        
        # Create admin profile
        new_admin = AdminUser(
            user_id=user.id,
            organization_id=admin_user.organization_id,
            role=data.get('role', 'admin'),
            can_manage_users=data.get('can_manage_users', True),
            can_manage_content=data.get('can_manage_content', True),
            can_view_analytics=data.get('can_view_analytics', True),
            can_manage_organization=data.get('can_manage_organization', False),
            can_manage_billing=data.get('can_manage_billing', False)
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        log_admin_action(
            admin_user, 'create_admin', 'admin_user', new_admin.id,
            f'Granted admin privileges to {user.email}',
            {'role': new_admin.role}
        )
        
        return jsonify({'admin_user': new_admin.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Content Management
@admin_bp.route('/content/overview', methods=['GET'])
@jwt_required()
@require_admin_permission('manage_content')
def content_overview(admin_user):
    """Get content management overview"""
    try:
        # Get content statistics
        courses = Course.query.all()
        modules = Module.query.all()
        quizzes = Quiz.query.all()
        videos = VideoModule.query.all()
        resources = KnowledgeResource.query.all()
        categories = ResourceCategory.query.all()
        
        return jsonify({
            'statistics': {
                'courses': len(courses),
                'modules': len(modules),
                'quizzes': len(quizzes),
                'videos': len(videos),
                'resources': len(resources),
                'categories': len(categories)
            },
            'recent_content': {
                'courses': [course.to_dict() for course in courses[-5:]],
                'quizzes': [quiz.to_dict() for quiz in quizzes[-5:]],
                'resources': [resource.to_dict() for resource in resources[-5:]]
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# System Settings
@admin_bp.route('/settings', methods=['GET'])
@jwt_required()
@require_admin_permission('manage_organization')
def get_system_settings(admin_user):
    """Get system settings"""
    try:
        settings = SystemSettings.query.all()
        
        # Group settings by category
        settings_by_category = {}
        for setting in settings:
            if setting.category not in settings_by_category:
                settings_by_category[setting.category] = []
            settings_by_category[setting.category].append(setting.to_dict())
        
        return jsonify({'settings': settings_by_category})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/settings/<setting_key>', methods=['PUT'])
@jwt_required()
@require_admin_permission('manage_organization')
def update_system_setting(admin_user, setting_key):
    """Update a system setting"""
    try:
        setting = SystemSettings.query.filter_by(key=setting_key).first_or_404()
        data = request.get_json()
        
        if not setting.is_editable:
            return jsonify({'error': 'Setting is not editable'}), 400
        
        old_value = setting.parsed_value
        setting.set_value(data.get('value'))
        setting.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_admin_action(
            admin_user, 'update_setting', 'system_setting', setting.id,
            f'Updated setting {setting_key}',
            {'old_value': old_value, 'new_value': setting.parsed_value}
        )
        
        return jsonify({'setting': setting.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Audit Logs
@admin_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
@require_admin_permission('view_analytics')
def get_audit_logs(admin_user):
    """Get audit logs with filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        action = request.args.get('action', '')
        resource_type = request.args.get('resource_type', '')
        
        # Build query
        query = AuditLog.query
        
        # Organization filter for non-super admins
        if not admin_user.is_super_admin and admin_user.organization_id:
            query = query.filter_by(organization_id=admin_user.organization_id)
        
        # Filters
        if action:
            query = query.filter_by(action=action)
        if resource_type:
            query = query.filter_by(resource_type=resource_type)
        
        # Pagination
        logs = query.order_by(AuditLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': logs.total,
                'pages': logs.pages,
                'has_next': logs.has_next,
                'has_prev': logs.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Organization Management
@admin_bp.route('/organization', methods=['GET'])
@jwt_required()
@require_admin_permission('view_analytics')
def get_organization(admin_user):
    """Get organization details"""
    try:
        if admin_user.is_super_admin:
            # Super admin can see all organizations
            organizations = Organization.query.all()
            return jsonify({
                'organizations': [org.to_dict() for org in organizations]
            })
        else:
            # Regular admin sees their organization
            if not admin_user.organization:
                return jsonify({'error': 'No organization found'}), 404
            
            return jsonify({
                'organization': admin_user.organization.to_dict()
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/organization/<int:org_id>', methods=['PUT'])
@jwt_required()
@require_admin_permission('manage_organization')
def update_organization(admin_user, org_id):
    """Update organization details"""
    try:
        organization = Organization.query.get_or_404(org_id)
        data = request.get_json()
        
        # Check access
        if not admin_user.is_super_admin and admin_user.organization_id != org_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Update allowed fields
        allowed_fields = [
            'name', 'description', 'contact_email', 'contact_phone', 'website',
            'address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code',
            'primary_color', 'secondary_color', 'logo_url'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(organization, field, data[field])
        
        organization.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_admin_action(
            admin_user, 'update_organization', 'organization', organization.id,
            f'Updated organization {organization.name}',
            {'updated_fields': list(data.keys())}
        )
        
        return jsonify({'organization': organization.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

