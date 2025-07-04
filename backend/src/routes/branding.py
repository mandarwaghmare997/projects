"""
Branding and White-labeling Routes for Qryti Learn Enterprise
Provides custom branding, theming, and white-labeling capabilities
"""

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from ..models.user import db, User
from ..models.admin import AdminUser, Organization, AuditLog
import os
import json
from PIL import Image
import io
import base64

branding_bp = Blueprint('branding', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'branding')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_branding_permission():
    """Decorator to require branding management permissions"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            admin_user = AdminUser.query.filter_by(user_id=current_user_id, is_active=True).first()
            if not admin_user or not admin_user.can_manage_organization:
                return jsonify({'error': 'Branding management permission required'}), 403
            
            return f(admin_user, *args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# Brand Settings Management
@branding_bp.route('/settings', methods=['GET'])
@jwt_required()
@require_branding_permission()
def get_brand_settings(admin_user):
    """Get current brand settings for organization"""
    try:
        org_id = admin_user.organization_id
        if not org_id:
            return jsonify({'error': 'No organization associated'}), 400
        
        organization = Organization.query.get_or_404(org_id)
        
        # Get branding settings from organization settings
        branding_settings = organization.settings.get('branding', {})
        
        # Default branding settings
        default_settings = {
            'primary_color': '#3B82F6',
            'secondary_color': '#1E40AF',
            'accent_color': '#10B981',
            'background_color': '#FFFFFF',
            'text_color': '#1F2937',
            'font_family': 'Inter, sans-serif',
            'logo_url': None,
            'favicon_url': None,
            'custom_css': '',
            'theme_mode': 'light',
            'show_powered_by': True,
            'custom_domain': None,
            'email_template_header': None,
            'login_background': None
        }
        
        # Merge with saved settings
        current_settings = {**default_settings, **branding_settings}
        
        return jsonify({
            'organization_id': org_id,
            'organization_name': organization.name,
            'branding_settings': current_settings,
            'subscription_tier': organization.subscription_tier,
            'white_labeling_enabled': organization.subscription_tier in ['enterprise', 'custom']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@branding_bp.route('/settings', methods=['PUT'])
@jwt_required()
@require_branding_permission()
def update_brand_settings(admin_user):
    """Update brand settings for organization"""
    try:
        org_id = admin_user.organization_id
        if not org_id:
            return jsonify({'error': 'No organization associated'}), 400
        
        organization = Organization.query.get_or_404(org_id)
        data = request.get_json()
        
        # Validate branding settings
        valid_settings = [
            'primary_color', 'secondary_color', 'accent_color', 'background_color',
            'text_color', 'font_family', 'custom_css', 'theme_mode', 'show_powered_by',
            'custom_domain', 'email_template_header'
        ]
        
        # Check subscription tier for advanced features
        advanced_features = ['custom_domain', 'show_powered_by', 'custom_css']
        if organization.subscription_tier not in ['enterprise', 'custom']:
            for feature in advanced_features:
                if feature in data and data[feature] != organization.settings.get('branding', {}).get(feature):
                    return jsonify({
                        'error': f'Feature "{feature}" requires Enterprise subscription'
                    }), 403
        
        # Update branding settings
        current_settings = organization.settings.copy()
        if 'branding' not in current_settings:
            current_settings['branding'] = {}
        
        for setting in valid_settings:
            if setting in data:
                current_settings['branding'][setting] = data[setting]
        
        organization.settings = current_settings
        db.session.commit()
        
        # Log the action
        audit_log = AuditLog(
            admin_user_id=admin_user.id,
            action='update_branding_settings',
            resource_type='organization',
            resource_id=organization.id,
            details=f"Updated branding settings for {organization.name}"
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Branding settings updated successfully',
            'branding_settings': current_settings['branding']
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Asset Upload Management
@branding_bp.route('/upload/logo', methods=['POST'])
@jwt_required()
@require_branding_permission()
def upload_logo(admin_user):
    """Upload organization logo"""
    try:
        org_id = admin_user.organization_id
        if not org_id:
            return jsonify({'error': 'No organization associated'}), 400
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, SVG'}), 400
        
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Generate secure filename
        filename = secure_filename(f"logo_org_{org_id}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save and optimize image
        if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Optimize image size
            image = Image.open(file.stream)
            
            # Resize if too large (max 500x200 for logo)
            max_size = (500, 200)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized image
            image.save(file_path, optimize=True, quality=85)
        else:
            # Save SVG or other formats as-is
            file.save(file_path)
        
        # Update organization settings
        organization = Organization.query.get_or_404(org_id)
        current_settings = organization.settings.copy()
        if 'branding' not in current_settings:
            current_settings['branding'] = {}
        
        current_settings['branding']['logo_url'] = f"/api/branding/assets/{filename}"
        organization.settings = current_settings
        db.session.commit()
        
        # Log the action
        audit_log = AuditLog(
            admin_user_id=admin_user.id,
            action='upload_logo',
            resource_type='organization',
            resource_id=organization.id,
            details=f"Uploaded logo: {filename}"
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Logo uploaded successfully',
            'logo_url': current_settings['branding']['logo_url'],
            'filename': filename
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@branding_bp.route('/upload/favicon', methods=['POST'])
@jwt_required()
@require_branding_permission()
def upload_favicon(admin_user):
    """Upload organization favicon"""
    try:
        org_id = admin_user.organization_id
        if not org_id:
            return jsonify({'error': 'No organization associated'}), 400
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith(('.png', '.ico')):
            return jsonify({'error': 'Favicon must be PNG or ICO format'}), 400
        
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Generate secure filename
        filename = secure_filename(f"favicon_org_{org_id}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Optimize favicon (32x32 or 16x16)
        if file.filename.lower().endswith('.png'):
            image = Image.open(file.stream)
            
            # Resize to standard favicon size
            favicon_size = (32, 32)
            image = image.resize(favicon_size, Image.Resampling.LANCZOS)
            
            # Save optimized favicon
            image.save(file_path, optimize=True)
        else:
            # Save ICO as-is
            file.save(file_path)
        
        # Update organization settings
        organization = Organization.query.get_or_404(org_id)
        current_settings = organization.settings.copy()
        if 'branding' not in current_settings:
            current_settings['branding'] = {}
        
        current_settings['branding']['favicon_url'] = f"/api/branding/assets/{filename}"
        organization.settings = current_settings
        db.session.commit()
        
        # Log the action
        audit_log = AuditLog(
            admin_user_id=admin_user.id,
            action='upload_favicon',
            resource_type='organization',
            resource_id=organization.id,
            details=f"Uploaded favicon: {filename}"
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Favicon uploaded successfully',
            'favicon_url': current_settings['branding']['favicon_url'],
            'filename': filename
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@branding_bp.route('/assets/<filename>')
def serve_branding_asset(filename):
    """Serve branding assets (logos, favicons, etc.)"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({'error': 'Asset not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Theme Generation
@branding_bp.route('/theme/generate', methods=['POST'])
@jwt_required()
@require_branding_permission()
def generate_theme(admin_user):
    """Generate CSS theme based on brand colors"""
    try:
        org_id = admin_user.organization_id
        if not org_id:
            return jsonify({'error': 'No organization associated'}), 400
        
        organization = Organization.query.get_or_404(org_id)
        branding_settings = organization.settings.get('branding', {})
        
        # Extract colors
        primary_color = branding_settings.get('primary_color', '#3B82F6')
        secondary_color = branding_settings.get('secondary_color', '#1E40AF')
        accent_color = branding_settings.get('accent_color', '#10B981')
        background_color = branding_settings.get('background_color', '#FFFFFF')
        text_color = branding_settings.get('text_color', '#1F2937')
        font_family = branding_settings.get('font_family', 'Inter, sans-serif')
        
        # Generate CSS theme
        css_theme = f"""
/* Custom Theme for {organization.name} */
:root {{
  --primary-color: {primary_color};
  --secondary-color: {secondary_color};
  --accent-color: {accent_color};
  --background-color: {background_color};
  --text-color: {text_color};
  --font-family: {font_family};
}}

/* Apply theme colors */
.btn-primary {{
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}}

.btn-primary:hover {{
  background-color: var(--secondary-color);
  border-color: var(--secondary-color);
}}

.text-primary {{
  color: var(--primary-color) !important;
}}

.bg-primary {{
  background-color: var(--primary-color) !important;
}}

.border-primary {{
  border-color: var(--primary-color) !important;
}}

.accent {{
  color: var(--accent-color) !important;
}}

.bg-accent {{
  background-color: var(--accent-color) !important;
}}

body {{
  font-family: var(--font-family);
  background-color: var(--background-color);
  color: var(--text-color);
}}

/* Navigation styling */
.navbar {{
  background-color: var(--primary-color) !important;
}}

.navbar-brand {{
  color: white !important;
}}

/* Form styling */
.form-control:focus {{
  border-color: var(--primary-color);
  box-shadow: 0 0 0 0.2rem rgba({primary_color[1:3]}, {primary_color[3:5]}, {primary_color[5:7]}, 0.25);
}}

/* Link styling */
a {{
  color: var(--primary-color);
}}

a:hover {{
  color: var(--secondary-color);
}}

/* Card styling */
.card {{
  border-color: var(--primary-color);
}}

.card-header {{
  background-color: var(--primary-color);
  color: white;
}}

/* Progress bars */
.progress-bar {{
  background-color: var(--accent-color);
}}

/* Badges */
.badge-primary {{
  background-color: var(--primary-color);
}}

.badge-success {{
  background-color: var(--accent-color);
}}
"""
        
        return jsonify({
            'message': 'Theme generated successfully',
            'css_theme': css_theme,
            'theme_variables': {
                'primary_color': primary_color,
                'secondary_color': secondary_color,
                'accent_color': accent_color,
                'background_color': background_color,
                'text_color': text_color,
                'font_family': font_family
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# White-labeling Features
@branding_bp.route('/white-label/preview', methods=['POST'])
@jwt_required()
@require_branding_permission()
def preview_white_label(admin_user):
    """Preview white-labeled version of the platform"""
    try:
        org_id = admin_user.organization_id
        if not org_id:
            return jsonify({'error': 'No organization associated'}), 400
        
        organization = Organization.query.get_or_404(org_id)
        
        # Check if white-labeling is available
        if organization.subscription_tier not in ['enterprise', 'custom']:
            return jsonify({
                'error': 'White-labeling requires Enterprise subscription'
            }), 403
        
        data = request.get_json()
        branding_settings = data.get('branding_settings', {})
        
        # Generate preview configuration
        preview_config = {
            'organization_name': organization.name,
            'custom_domain': branding_settings.get('custom_domain'),
            'logo_url': branding_settings.get('logo_url'),
            'favicon_url': branding_settings.get('favicon_url'),
            'primary_color': branding_settings.get('primary_color', '#3B82F6'),
            'secondary_color': branding_settings.get('secondary_color', '#1E40AF'),
            'font_family': branding_settings.get('font_family', 'Inter, sans-serif'),
            'show_powered_by': branding_settings.get('show_powered_by', True),
            'custom_css': branding_settings.get('custom_css', ''),
            'theme_mode': branding_settings.get('theme_mode', 'light')
        }
        
        # Generate preview HTML
        preview_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{organization.name} - Learning Platform</title>
    <link rel="icon" href="{preview_config['favicon_url'] or '/favicon.ico'}">
    <style>
        :root {{
            --primary-color: {preview_config['primary_color']};
            --secondary-color: {preview_config['secondary_color']};
            --font-family: {preview_config['font_family']};
        }}
        
        body {{
            font-family: var(--font-family);
            margin: 0;
            padding: 0;
            background-color: #f8fafc;
        }}
        
        .header {{
            background-color: var(--primary-color);
            color: white;
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        .logo {{
            height: 40px;
        }}
        
        .nav {{
            display: flex;
            gap: 2rem;
        }}
        
        .nav a {{
            color: white;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .main {{
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .card {{
            background: white;
            border-radius: 8px;
            padding: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}
        
        .btn {{
            background-color: var(--primary-color);
            color: white;
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 6px;
            font-weight: 500;
            cursor: pointer;
        }}
        
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #6b7280;
            font-size: 0.875rem;
        }}
        
        {preview_config['custom_css']}
    </style>
</head>
<body>
    <header class="header">
        <div style="display: flex; align-items: center; gap: 1rem;">
            {f'<img src="{preview_config["logo_url"]}" alt="Logo" class="logo">' if preview_config['logo_url'] else f'<h1 style="margin: 0; font-size: 1.5rem;">{organization.name}</h1>'}
        </div>
        <nav class="nav">
            <a href="#">Courses</a>
            <a href="#">Quizzes</a>
            <a href="#">Certificates</a>
            <a href="#">Profile</a>
        </nav>
    </header>
    
    <main class="main">
        <div class="card">
            <h2>Welcome to {organization.name} Learning Platform</h2>
            <p>This is a preview of your white-labeled learning platform. Your custom branding and colors are applied throughout the interface.</p>
            <button class="btn">Start Learning</button>
        </div>
        
        <div class="card">
            <h3>Featured Courses</h3>
            <p>Explore our comprehensive course catalog designed for your organization's learning needs.</p>
        </div>
    </main>
    
    <footer class="footer">
        {f'Powered by {organization.name}' if not preview_config['show_powered_by'] else 'Powered by Qryti Learn'}
    </footer>
</body>
</html>
"""
        
        return jsonify({
            'message': 'White-label preview generated',
            'preview_config': preview_config,
            'preview_html': preview_html,
            'preview_url': f"/api/branding/white-label/preview/{org_id}"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@branding_bp.route('/domain/validate', methods=['POST'])
@jwt_required()
@require_branding_permission()
def validate_custom_domain(admin_user):
    """Validate custom domain configuration"""
    try:
        org_id = admin_user.organization_id
        if not org_id:
            return jsonify({'error': 'No organization associated'}), 400
        
        organization = Organization.query.get_or_404(org_id)
        
        # Check if custom domain is available
        if organization.subscription_tier not in ['enterprise', 'custom']:
            return jsonify({
                'error': 'Custom domain requires Enterprise subscription'
            }), 403
        
        data = request.get_json()
        domain = data.get('domain', '').strip().lower()
        
        if not domain:
            return jsonify({'error': 'Domain is required'}), 400
        
        # Basic domain validation
        import re
        domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
        if not re.match(domain_pattern, domain):
            return jsonify({'error': 'Invalid domain format'}), 400
        
        # Check if domain is already in use
        existing_org = Organization.query.filter(
            Organization.id != org_id,
            Organization.domain == domain
        ).first()
        
        if existing_org:
            return jsonify({'error': 'Domain is already in use'}), 400
        
        # Simulate DNS validation (in production, you'd check actual DNS records)
        validation_results = {
            'domain': domain,
            'is_valid': True,
            'dns_configured': True,  # Would check actual DNS in production
            'ssl_available': True,   # Would check SSL certificate availability
            'recommendations': [
                f"Point your domain {domain} to our servers",
                "Ensure SSL certificate is configured",
                "Update your DNS CNAME record"
            ]
        }
        
        return jsonify({
            'message': 'Domain validation completed',
            'validation_results': validation_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

