"""
Enterprise Features and Multi-tenant Support Routes for Qryti Learn
Provides organization management, bulk operations, and enterprise features
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, desc
from ..models.user import db, User
from ..models.admin import AdminUser, Organization, AuditLog
from ..models.course import CourseEnrollment
from ..models.progress import UserProgress
import csv
import io
import json
from werkzeug.security import generate_password_hash

enterprise_bp = Blueprint('enterprise', __name__)

def require_enterprise_admin():
    """Decorator to require enterprise admin permissions"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            admin_user = AdminUser.query.filter_by(user_id=current_user_id, is_active=True).first()
            if not admin_user or not admin_user.can_manage_organization:
                return jsonify({'error': 'Enterprise admin permission required'}), 403
            
            return f(admin_user, *args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# Organization Management
@enterprise_bp.route('/organizations', methods=['GET'])
@jwt_required()
@require_enterprise_admin()
def list_organizations(admin_user):
    """Get list of organizations"""
    try:
        # Super admins can see all organizations
        if admin_user.is_super_admin:
            organizations = Organization.query.all()
        else:
            # Regular admins can only see their organization
            organizations = Organization.query.filter_by(id=admin_user.organization_id).all()
        
        org_data = []
        for org in organizations:
            # Get organization statistics
            user_count = User.query.filter_by(organization_id=org.id).count()
            active_users = User.query.filter_by(
                organization_id=org.id, 
                is_active=True
            ).count()
            
            org_data.append({
                'id': org.id,
                'name': org.name,
                'domain': org.domain,
                'subscription_tier': org.subscription_tier,
                'is_active': org.is_active,
                'created_at': org.created_at.isoformat() if org.created_at else None,
                'settings': org.settings,
                'statistics': {
                    'total_users': user_count,
                    'active_users': active_users,
                    'activation_rate': round((active_users / user_count * 100), 2) if user_count else 0
                }
            })
        
        return jsonify({
            'organizations': org_data,
            'total': len(org_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enterprise_bp.route('/organizations', methods=['POST'])
@jwt_required()
@require_enterprise_admin()
def create_organization(admin_user):
    """Create new organization"""
    try:
        if not admin_user.is_super_admin:
            return jsonify({'error': 'Super admin permission required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'domain', 'subscription_tier']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if domain already exists
        existing_org = Organization.query.filter_by(domain=data['domain']).first()
        if existing_org:
            return jsonify({'error': 'Domain already exists'}), 400
        
        # Create organization
        organization = Organization(
            name=data['name'],
            domain=data['domain'],
            subscription_tier=data['subscription_tier'],
            max_users=data.get('max_users', 100),
            settings=data.get('settings', {}),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(organization)
        db.session.commit()
        
        # Log the action
        audit_log = AuditLog(
            admin_user_id=admin_user.id,
            action='create_organization',
            resource_type='organization',
            resource_id=organization.id,
            details=f"Created organization: {organization.name}"
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Organization created successfully',
            'organization': {
                'id': organization.id,
                'name': organization.name,
                'domain': organization.domain,
                'subscription_tier': organization.subscription_tier
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@enterprise_bp.route('/organizations/<int:org_id>', methods=['PUT'])
@jwt_required()
@require_enterprise_admin()
def update_organization(admin_user, org_id):
    """Update organization settings"""
    try:
        # Check permissions
        if not admin_user.is_super_admin and admin_user.organization_id != org_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        organization = Organization.query.get_or_404(org_id)
        data = request.get_json()
        
        # Update allowed fields
        updatable_fields = ['name', 'subscription_tier', 'max_users', 'settings', 'is_active']
        for field in updatable_fields:
            if field in data:
                setattr(organization, field, data[field])
        
        # Super admins can update domain
        if admin_user.is_super_admin and 'domain' in data:
            organization.domain = data['domain']
        
        db.session.commit()
        
        # Log the action
        audit_log = AuditLog(
            admin_user_id=admin_user.id,
            action='update_organization',
            resource_type='organization',
            resource_id=organization.id,
            details=f"Updated organization: {organization.name}"
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Organization updated successfully',
            'organization': {
                'id': organization.id,
                'name': organization.name,
                'domain': organization.domain,
                'subscription_tier': organization.subscription_tier,
                'settings': organization.settings
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Bulk User Operations
@enterprise_bp.route('/users/bulk-import', methods=['POST'])
@jwt_required()
@require_enterprise_admin()
def bulk_import_users(admin_user):
    """Bulk import users from CSV"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'File must be CSV format'}), 400
        
        # Read CSV content
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        imported_users = []
        errors = []
        
        for row_num, row in enumerate(csv_input, start=2):
            try:
                # Validate required fields
                required_fields = ['email', 'first_name', 'last_name']
                for field in required_fields:
                    if field not in row or not row[field].strip():
                        errors.append(f"Row {row_num}: Missing {field}")
                        continue
                
                # Check if user already exists
                existing_user = User.query.filter_by(email=row['email'].strip().lower()).first()
                if existing_user:
                    errors.append(f"Row {row_num}: User with email {row['email']} already exists")
                    continue
                
                # Create user
                user = User(
                    email=row['email'].strip().lower(),
                    first_name=row['first_name'].strip(),
                    last_name=row['last_name'].strip(),
                    password_hash=generate_password_hash(row.get('password', 'TempPass123!')),
                    organization_id=admin_user.organization_id if not admin_user.is_super_admin else row.get('organization_id'),
                    is_active=row.get('is_active', 'true').lower() == 'true'
                )
                
                db.session.add(user)
                imported_users.append({
                    'email': user.email,
                    'name': f"{user.first_name} {user.last_name}"
                })
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        if imported_users:
            db.session.commit()
            
            # Log the action
            audit_log = AuditLog(
                admin_user_id=admin_user.id,
                action='bulk_import_users',
                resource_type='user',
                details=f"Imported {len(imported_users)} users"
            )
            db.session.add(audit_log)
            db.session.commit()
        else:
            db.session.rollback()
        
        return jsonify({
            'message': f'Import completed. {len(imported_users)} users imported.',
            'imported_users': imported_users,
            'errors': errors,
            'success_count': len(imported_users),
            'error_count': len(errors)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@enterprise_bp.route('/users/bulk-export', methods=['GET'])
@jwt_required()
@require_enterprise_admin()
def bulk_export_users(admin_user):
    """Export users to CSV format"""
    try:
        # Organization filter
        org_filter = {}
        if not admin_user.is_super_admin and admin_user.organization_id:
            org_filter['organization_id'] = admin_user.organization_id
        
        # Get export parameters
        include_progress = request.args.get('include_progress', 'false').lower() == 'true'
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        # Build query
        query = User.query.filter_by(**org_filter)
        if not include_inactive:
            query = query.filter_by(is_active=True)
        
        users = query.all()
        
        # Prepare CSV data
        csv_data = []
        for user in users:
            user_data = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else '',
                'last_login': user.last_login.isoformat() if user.last_login else '',
                'organization_id': user.organization_id
            }
            
            if include_progress:
                # Add learning progress data
                enrollments = CourseEnrollment.query.filter_by(user_id=user.id).count()
                completions = UserProgress.query.filter_by(
                    user_id=user.id, 
                    completion_status='completed'
                ).count()
                
                user_data.update({
                    'course_enrollments': enrollments,
                    'course_completions': completions,
                    'completion_rate': round((completions / enrollments * 100), 2) if enrollments else 0
                })
            
            csv_data.append(user_data)
        
        # Log the action
        audit_log = AuditLog(
            admin_user_id=admin_user.id,
            action='bulk_export_users',
            resource_type='user',
            details=f"Exported {len(csv_data)} users"
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'export_data': csv_data,
            'total_records': len(csv_data),
            'exported_at': datetime.utcnow().isoformat(),
            'include_progress': include_progress,
            'include_inactive': include_inactive
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Subscription Management
@enterprise_bp.route('/subscription/usage', methods=['GET'])
@jwt_required()
@require_enterprise_admin()
def get_subscription_usage(admin_user):
    """Get subscription usage statistics"""
    try:
        org_id = admin_user.organization_id
        if not org_id:
            return jsonify({'error': 'No organization associated'}), 400
        
        organization = Organization.query.get_or_404(org_id)
        
        # Get usage statistics
        total_users = User.query.filter_by(organization_id=org_id).count()
        active_users = User.query.filter_by(organization_id=org_id, is_active=True).count()
        
        # Calculate usage percentages
        user_usage_percent = (total_users / organization.max_users * 100) if organization.max_users else 0
        
        # Get feature usage
        current_month = datetime.utcnow().replace(day=1)
        monthly_enrollments = CourseEnrollment.query.join(User).filter(
            User.organization_id == org_id,
            CourseEnrollment.enrolled_at >= current_month
        ).count()
        
        return jsonify({
            'organization': {
                'name': organization.name,
                'subscription_tier': organization.subscription_tier,
                'max_users': organization.max_users
            },
            'usage': {
                'users': {
                    'current': total_users,
                    'active': active_users,
                    'limit': organization.max_users,
                    'usage_percent': round(user_usage_percent, 2)
                },
                'monthly_activity': {
                    'enrollments': monthly_enrollments
                }
            },
            'features': organization.settings.get('features', {}),
            'limits': {
                'approaching_user_limit': user_usage_percent > 80,
                'at_user_limit': user_usage_percent >= 100
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enterprise_bp.route('/subscription/upgrade', methods=['POST'])
@jwt_required()
@require_enterprise_admin()
def request_subscription_upgrade(admin_user):
    """Request subscription tier upgrade"""
    try:
        data = request.get_json()
        
        org_id = admin_user.organization_id
        if not org_id:
            return jsonify({'error': 'No organization associated'}), 400
        
        organization = Organization.query.get_or_404(org_id)
        
        # Validate upgrade request
        new_tier = data.get('new_tier')
        if not new_tier:
            return jsonify({'error': 'New tier required'}), 400
        
        valid_tiers = ['basic', 'professional', 'enterprise', 'custom']
        if new_tier not in valid_tiers:
            return jsonify({'error': 'Invalid subscription tier'}), 400
        
        # Log the upgrade request
        audit_log = AuditLog(
            admin_user_id=admin_user.id,
            action='request_subscription_upgrade',
            resource_type='organization',
            resource_id=organization.id,
            details=f"Requested upgrade from {organization.subscription_tier} to {new_tier}"
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Subscription upgrade request submitted',
            'current_tier': organization.subscription_tier,
            'requested_tier': new_tier,
            'request_id': audit_log.id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Enterprise Analytics
@enterprise_bp.route('/analytics/organization-overview', methods=['GET'])
@jwt_required()
@require_enterprise_admin()
def organization_analytics_overview(admin_user):
    """Get organization-wide analytics overview"""
    try:
        org_id = admin_user.organization_id
        if not org_id:
            return jsonify({'error': 'No organization associated'}), 400
        
        # Date range
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # User metrics
        total_users = User.query.filter_by(organization_id=org_id).count()
        active_users = User.query.filter_by(organization_id=org_id, is_active=True).count()
        new_users = User.query.filter(
            User.organization_id == org_id,
            User.created_at >= start_date
        ).count()
        
        # Learning metrics
        total_enrollments = CourseEnrollment.query.join(User).filter(
            User.organization_id == org_id
        ).count()
        
        recent_enrollments = CourseEnrollment.query.join(User).filter(
            User.organization_id == org_id,
            CourseEnrollment.enrolled_at >= start_date
        ).count()
        
        completions = UserProgress.query.join(User).filter(
            User.organization_id == org_id,
            UserProgress.completion_status == 'completed'
        ).count()
        
        # Department breakdown (if available)
        department_stats = db.session.query(
            User.department,
            func.count(User.id).label('user_count'),
            func.count(CourseEnrollment.id).label('enrollments')
        ).outerjoin(CourseEnrollment).filter(
            User.organization_id == org_id
        ).group_by(User.department).all()
        
        return jsonify({
            'organization_id': org_id,
            'period_days': days,
            'user_metrics': {
                'total_users': total_users,
                'active_users': active_users,
                'new_users': new_users,
                'activation_rate': round((active_users / total_users * 100), 2) if total_users else 0
            },
            'learning_metrics': {
                'total_enrollments': total_enrollments,
                'recent_enrollments': recent_enrollments,
                'completions': completions,
                'completion_rate': round((completions / total_enrollments * 100), 2) if total_enrollments else 0
            },
            'department_breakdown': [
                {
                    'department': row.department or 'Unassigned',
                    'user_count': row.user_count,
                    'enrollments': row.enrollments or 0
                }
                for row in department_stats
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

