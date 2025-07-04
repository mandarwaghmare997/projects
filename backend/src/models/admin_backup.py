"""
Admin and Organization Models for Qryti Learn Enterprise
Handles admin users, organizations, and enterprise features
"""

from datetime import datetime
from .user import db
import json

class Organization(db.Model):
    """Organizations for multi-tenant enterprise support"""
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # Contact information
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    
    # Address
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    
    # Enterprise settings
    max_users = db.Column(db.Integer, default=100)
    subscription_tier = db.Column(db.String(50), default='basic')  # basic, premium, enterprise
    subscription_status = db.Column(db.String(20), default='active')  # active, suspended, cancelled
    subscription_start = db.Column(db.DateTime)
    subscription_end = db.Column(db.DateTime)
    
    # Branding and customization
    logo_url = db.Column(db.String(500))
    primary_color = db.Column(db.String(20), default='#3B82F6')  # Blue
    secondary_color = db.Column(db.String(20), default='#1E40AF')  # Dark blue
    custom_domain = db.Column(db.String(200))
    
    # Features and permissions
    features_json = db.Column(db.Text)  # JSON of enabled features
    settings_json = db.Column(db.Text)  # JSON of organization settings
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='organization', cascade='all, delete-orphan')
    admin_users = db.relationship('AdminUser', backref='organization', cascade='all, delete-orphan')
    
    @property
    def features(self):
        """Get enabled features as a list"""
        if self.features_json:
            try:
                return json.loads(self.features_json)
            except:
                return []
        return []
    
    @features.setter
    def features(self, value):
        """Set features from a list"""
        if isinstance(value, list):
            self.features_json = json.dumps(value)
        else:
            self.features_json = json.dumps([])
    
    @property
    def settings(self):
        """Get organization settings as a dict"""
        if self.settings_json:
            try:
                return json.loads(self.settings_json)
            except:
                return {}
        return {}
    
    @settings.setter
    def settings(self, value):
        """Set settings from a dict"""
        if isinstance(value, dict):
            self.settings_json = json.dumps(value)
        else:
            self.settings_json = json.dumps({})
    
    @property
    def user_count(self):
        """Get current user count"""
        return len(self.users)
    
    @property
    def is_subscription_active(self):
        """Check if subscription is active and not expired"""
        if self.subscription_status != 'active':
            return False
        if self.subscription_end and self.subscription_end < datetime.utcnow():
            return False
        return True
    
    def to_dict(self):
        """Convert organization to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'website': self.website,
            'address': {
                'line1': self.address_line1,
                'line2': self.address_line2,
                'city': self.city,
                'state': self.state,
                'country': self.country,
                'postal_code': self.postal_code
            },
            'subscription': {
                'tier': self.subscription_tier,
                'status': self.subscription_status,
                'start': self.subscription_start.isoformat() if self.subscription_start else None,
                'end': self.subscription_end.isoformat() if self.subscription_end else None,
                'is_active': self.is_subscription_active
            },
            'branding': {
                'logo_url': self.logo_url,
                'primary_color': self.primary_color,
                'secondary_color': self.secondary_color,
                'custom_domain': self.custom_domain
            },
            'limits': {
                'max_users': self.max_users,
                'current_users': self.user_count
            },
            'features': self.features,
            'settings': self.settings,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AdminUser(db.Model):
    """Admin users with elevated permissions"""
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    
    # Admin role and permissions
    role = db.Column(db.String(50), nullable=False, default='admin')  # super_admin, admin, moderator
    permissions_json = db.Column(db.Text)  # JSON of specific permissions
    
    # Admin settings
    can_manage_users = db.Column(db.Boolean, default=True)
    can_manage_content = db.Column(db.Boolean, default=True)
    can_view_analytics = db.Column(db.Boolean, default=True)
    can_manage_organization = db.Column(db.Boolean, default=False)
    can_manage_billing = db.Column(db.Boolean, default=False)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='admin_profile')
    
    @property
    def permissions(self):
        """Get permissions as a list"""
        if self.permissions_json:
            try:
                return json.loads(self.permissions_json)
            except:
                return []
        return []
    
    @permissions.setter
    def permissions(self, value):
        """Set permissions from a list"""
        if isinstance(value, list):
            self.permissions_json = json.dumps(value)
        else:
            self.permissions_json = json.dumps([])
    
    @property
    def is_super_admin(self):
        """Check if user is super admin"""
        return self.role == 'super_admin'
    
    @property
    def is_organization_admin(self):
        """Check if user can manage organization"""
        return self.can_manage_organization or self.is_super_admin
    
    def has_permission(self, permission):
        """Check if admin has specific permission"""
        if self.is_super_admin:
            return True
        return permission in self.permissions
    
    def to_dict(self):
        """Convert admin user to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'organization_id': self.organization_id,
            'role': self.role,
            'permissions': self.permissions,
            'capabilities': {
                'can_manage_users': self.can_manage_users,
                'can_manage_content': self.can_manage_content,
                'can_view_analytics': self.can_view_analytics,
                'can_manage_organization': self.can_manage_organization,
                'can_manage_billing': self.can_manage_billing
            },
            'is_active': self.is_active,
            'is_super_admin': self.is_super_admin,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': self.user.to_dict() if self.user else None
        }

class AuditLog(db.Model):
    """Audit log for tracking admin actions"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    
    # Action details
    action = db.Column(db.String(100), nullable=False)  # create_user, delete_content, etc.
    resource_type = db.Column(db.String(50))  # user, course, quiz, etc.
    resource_id = db.Column(db.Integer)
    
    # Action context
    description = db.Column(db.Text)
    metadata_json = db.Column(db.Text)  # JSON of additional data
    ip_address = db.Column(db.String(45))
    user_agent = db.Co    metadata_json = db.Column(db.Text)  # JSON of additional data
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    admin_user = db.relationship('AdminUser', backref='audit_logs')
    
    @property
    def audit_metadata(self):
        """Get audit metadata as a dict"""
        if self.metadata_json:
            try:
                return json.loads(self.metadata_json)
            except:
                return {}
        return {}
    
    @audit_metadata.setter
    def audit_metadata(self, value):
        """Set audit metadata from a dict"""
        if isinstance(value, dict):
            self.metadata_json = json.dumps(value)
        else:
            self.metadata_json = json.dumps({})json = json.dumps({})
    
    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'admin_user_id': self.admin_user_id,
            'organization_id': self.organization_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'description': self.description,
            'metadata': self.metadata,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'admin_user': self.admin_user.to_dict() if self.admin_user else None
        }

class SystemSettings(db.Model):
    """Global system settings for the platform"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False, unique=True)
    value = db.Column(db.Text)
    data_type = db.Column(db.String(20), default='string')  # string, integer, boolean, json
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='general')
    
    # Access control
    is_public = db.Column(db.Boolean, default=False)  # Can be accessed by non-admin users
    is_editable = db.Column(db.Boolean, default=True)  # Can be modified
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def parsed_value(self):
        """Get value parsed according to data type"""
        if not self.value:
            return None
        
        try:
            if self.data_type == 'integer':
                return int(self.value)
            elif self.data_type == 'boolean':
                return self.value.lower() in ('true', '1', 'yes', 'on')
            elif self.data_type == 'json':
                return json.loads(self.value)
            else:
                return self.value
        except:
            return self.value
    
    def set_value(self, value):
        """Set value with automatic type conversion"""
        if self.data_type == 'json':
            self.value = json.dumps(value)
        else:
            self.value = str(value)
    
    def to_dict(self):
        """Convert system setting to dictionary"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.parsed_value,
            'data_type': self.data_type,
            'description': self.description,
            'category': self.category,
            'is_public': self.is_public,
            'is_editable': self.is_editable,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

