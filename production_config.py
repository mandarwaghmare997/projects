#!/usr/bin/env python3
"""
Production Configuration Setup for Qryti Learn
Prepares the application for production deployment
"""

import os
import json
import shutil
from datetime import datetime

class ProductionConfig:
    def __init__(self):
        self.project_root = "/home/ubuntu/projects"
        self.backend_path = f"{self.project_root}/backend"
        self.frontend_path = f"{self.project_root}/frontend"
        self.config_results = []
        
    def log_config(self, category, action, result, status="success"):
        """Log configuration action and result"""
        self.config_results.append({
            'category': category,
            'action': action,
            'result': result,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        status_icon = "✅" if status == "success" else "⚠️" if status == "warning" else "❌"
        print(f"{status_icon} {category}: {action} - {result}")
    
    def create_environment_files(self):
        """Create production environment configuration files"""
        print("🔧 Creating Environment Configuration Files...")
        
        # Backend environment file
        backend_env = """# Qryti Learn Backend Production Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-production-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this
DATABASE_URL=sqlite:///app.db
CORS_ORIGINS=https://learn.qryti.com,https://qryti.com
API_RATE_LIMIT=1000 per hour
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH=16777216
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=noreply@qryti.com
MAIL_PASSWORD=your-email-password
ADMIN_EMAIL=admin@qryti.com
MONITORING_ENABLED=True
LOG_LEVEL=INFO
CERTIFICATE_STORAGE_PATH=/app/certificates
BACKUP_ENABLED=True
BACKUP_SCHEDULE=0 2 * * *
"""
        
        backend_env_path = f"{self.backend_path}/.env.production"
        with open(backend_env_path, 'w') as f:
            f.write(backend_env)
        
        self.log_config(
            "Environment",
            "Backend .env.production",
            f"Created at {backend_env_path}"
        )
        
        # Frontend environment file
        frontend_env = """# Qryti Learn Frontend Production Configuration
REACT_APP_API_URL=https://api.qryti.com
REACT_APP_ENVIRONMENT=production
REACT_APP_VERSION=1.0.0
REACT_APP_SENTRY_DSN=your-sentry-dsn-here
REACT_APP_GOOGLE_ANALYTICS=your-ga-tracking-id
REACT_APP_CERTIFICATE_VERIFY_URL=https://verify.qryti.com
REACT_APP_SUPPORT_EMAIL=support@qryti.com
REACT_APP_COMPANY_NAME=Qryti Learn
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_MONITORING=true
"""
        
        frontend_env_path = f"{self.frontend_path}/.env.production"
        with open(frontend_env_path, 'w') as f:
            f.write(frontend_env)
        
        self.log_config(
            "Environment",
            "Frontend .env.production",
            f"Created at {frontend_env_path}"
        )
    
    def create_nginx_config(self):
        """Create Nginx configuration for production"""
        print("🌐 Creating Nginx Configuration...")
        
        nginx_config = """# Nginx Configuration for Qryti Learn Production
server {
    listen 80;
    server_name learn.qryti.com www.learn.qryti.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name learn.qryti.com www.learn.qryti.com;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/qryti.com.crt;
    ssl_certificate_key /etc/ssl/private/qryti.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.google-analytics.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https://api.qryti.com;";
    
    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Frontend Static Files
    location / {
        root /var/www/qryti-learn;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health Check
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
    
    # Certificate Downloads
    location /certificates/ {
        proxy_pass http://127.0.0.1:5000/api/certificates/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;
    
    location /api/auth/ {
        limit_req zone=auth burst=10 nodelay;
        proxy_pass http://127.0.0.1:5000/api/auth/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Logging
    access_log /var/log/nginx/qryti-learn.access.log;
    error_log /var/log/nginx/qryti-learn.error.log;
}

# API Server Configuration
server {
    listen 80;
    server_name api.qryti.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.qryti.com;
    
    # SSL Configuration (same as above)
    ssl_certificate /etc/ssl/certs/qryti.com.crt;
    ssl_certificate_key /etc/ssl/private/qryti.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    
    # CORS Headers
    add_header Access-Control-Allow-Origin "https://learn.qryti.com" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With" always;
    add_header Access-Control-Allow-Credentials true always;
    
    # Handle preflight requests
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin "https://learn.qryti.com";
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With";
        add_header Access-Control-Max-Age 1728000;
        add_header Content-Type "text/plain charset=UTF-8";
        add_header Content-Length 0;
        return 204;
    }
    
    # API Endpoints
    location / {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Logging
    access_log /var/log/nginx/qryti-api.access.log;
    error_log /var/log/nginx/qryti-api.error.log;
}
"""
        
        nginx_config_path = f"{self.project_root}/nginx.conf"
        with open(nginx_config_path, 'w') as f:
            f.write(nginx_config)
        
        self.log_config(
            "Web Server",
            "Nginx Configuration",
            f"Created at {nginx_config_path}"
        )
    
    def create_systemd_services(self):
        """Create systemd service files for production"""
        print("⚙️ Creating Systemd Service Files...")
        
        # Backend service
        backend_service = """[Unit]
Description=Qryti Learn API Server
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/qryti-learn/backend
Environment=PATH=/opt/qryti-learn/venv/bin
ExecStart=/opt/qryti-learn/venv/bin/python -m src.main
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=qryti-learn-api

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/qryti-learn/backend/src/database
ReadWritePaths=/opt/qryti-learn/certificates
ReadWritePaths=/opt/qryti-learn/uploads

[Install]
WantedBy=multi-user.target
"""
        
        backend_service_path = f"{self.project_root}/qryti-learn-api.service"
        with open(backend_service_path, 'w') as f:
            f.write(backend_service)
        
        self.log_config(
            "System Service",
            "Backend Service File",
            f"Created at {backend_service_path}"
        )
        
        # Monitoring service
        monitoring_service = """[Unit]
Description=Qryti Learn Monitoring Service
After=network.target qryti-learn-api.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/qryti-learn/monitoring
ExecStart=/opt/qryti-learn/venv/bin/python monitor.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal
SyslogIdentifier=qryti-learn-monitor

[Install]
WantedBy=multi-user.target
"""
        
        monitoring_service_path = f"{self.project_root}/qryti-learn-monitor.service"
        with open(monitoring_service_path, 'w') as f:
            f.write(monitoring_service)
        
        self.log_config(
            "System Service",
            "Monitoring Service File",
            f"Created at {monitoring_service_path}"
        )
    
    def create_deployment_scripts(self):
        """Create deployment and maintenance scripts"""
        print("📦 Creating Deployment Scripts...")
        
        # Main deployment script
        deploy_script = """#!/bin/bash
# Qryti Learn Production Deployment Script

set -e

echo "🚀 Starting Qryti Learn Deployment..."

# Configuration
PROJECT_DIR="/opt/qryti-learn"
BACKUP_DIR="/opt/qryti-learn/backups"
VENV_DIR="/opt/qryti-learn/venv"
WEB_DIR="/var/www/qryti-learn"

# Create directories
sudo mkdir -p $PROJECT_DIR
sudo mkdir -p $BACKUP_DIR
sudo mkdir -p $WEB_DIR
sudo mkdir -p /opt/qryti-learn/certificates
sudo mkdir -p /opt/qryti-learn/uploads

# Backup existing installation
if [ -d "$PROJECT_DIR/backend" ]; then
    echo "📦 Creating backup..."
    sudo tar -czf "$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz" -C $PROJECT_DIR .
fi

# Copy application files
echo "📁 Copying application files..."
sudo cp -r backend $PROJECT_DIR/
sudo cp -r frontend/build/* $WEB_DIR/

# Set up Python virtual environment
echo "🐍 Setting up Python environment..."
sudo python3 -m venv $VENV_DIR
sudo $VENV_DIR/bin/pip install -r $PROJECT_DIR/backend/requirements.txt

# Set permissions
echo "🔐 Setting permissions..."
sudo chown -R www-data:www-data $PROJECT_DIR
sudo chown -R www-data:www-data $WEB_DIR
sudo chmod -R 755 $PROJECT_DIR
sudo chmod -R 755 $WEB_DIR

# Database setup
echo "💾 Setting up database..."
cd $PROJECT_DIR/backend
sudo -u www-data $VENV_DIR/bin/python -c "
from src.main import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"

# Install systemd services
echo "⚙️ Installing system services..."
sudo cp qryti-learn-api.service /etc/systemd/system/
sudo cp qryti-learn-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable qryti-learn-api
sudo systemctl enable qryti-learn-monitor

# Install nginx configuration
echo "🌐 Configuring web server..."
sudo cp nginx.conf /etc/nginx/sites-available/qryti-learn
sudo ln -sf /etc/nginx/sites-available/qryti-learn /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Start services
echo "🚀 Starting services..."
sudo systemctl start qryti-learn-api
sudo systemctl start qryti-learn-monitor

# Health check
echo "🏥 Performing health check..."
sleep 5
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ API service is healthy"
else
    echo "❌ API service health check failed"
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo "📊 Access the application at: https://learn.qryti.com"
echo "📈 Monitor the system at: https://learn.qryti.com/admin"
"""
        
        deploy_script_path = f"{self.project_root}/deploy-production.sh"
        with open(deploy_script_path, 'w') as f:
            f.write(deploy_script)
        os.chmod(deploy_script_path, 0o755)
        
        self.log_config(
            "Deployment",
            "Production Deployment Script",
            f"Created at {deploy_script_path}"
        )
        
        # Backup script
        backup_script = """#!/bin/bash
# Qryti Learn Backup Script

BACKUP_DIR="/opt/qryti-learn/backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/qryti-backup-$DATE.tar.gz"

echo "📦 Starting backup process..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Stop services temporarily
sudo systemctl stop qryti-learn-api

# Create backup
tar -czf $BACKUP_FILE \\
    -C /opt/qryti-learn backend/src/database \\
    -C /opt/qryti-learn certificates \\
    -C /opt/qryti-learn uploads

# Restart services
sudo systemctl start qryti-learn-api

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "qryti-backup-*.tar.gz" -mtime +7 -delete

echo "✅ Backup completed: $BACKUP_FILE"
"""
        
        backup_script_path = f"{self.project_root}/backup.sh"
        with open(backup_script_path, 'w') as f:
            f.write(backup_script)
        os.chmod(backup_script_path, 0o755)
        
        self.log_config(
            "Maintenance",
            "Backup Script",
            f"Created at {backup_script_path}"
        )
    
    def create_monitoring_config(self):
        """Create monitoring and logging configuration"""
        print("📊 Creating Monitoring Configuration...")
        
        # Logging configuration
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                },
                "detailed": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "detailed",
                    "filename": "/var/log/qryti-learn/app.log",
                    "maxBytes": 10485760,
                    "backupCount": 5
                },
                "error_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "detailed",
                    "filename": "/var/log/qryti-learn/error.log",
                    "maxBytes": 10485760,
                    "backupCount": 5
                }
            },
            "loggers": {
                "qryti_learn": {
                    "level": "INFO",
                    "handlers": ["console", "file", "error_file"],
                    "propagate": False
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["console", "file"]
            }
        }
        
        logging_config_path = f"{self.project_root}/logging.json"
        with open(logging_config_path, 'w') as f:
            json.dump(logging_config, f, indent=2)
        
        self.log_config(
            "Monitoring",
            "Logging Configuration",
            f"Created at {logging_config_path}"
        )
    
    def generate_production_checklist(self):
        """Generate production deployment checklist"""
        print("📋 Generating Production Checklist...")
        
        checklist = """# Qryti Learn Production Deployment Checklist

## Pre-Deployment
- [ ] SSL certificates obtained and configured
- [ ] Domain DNS configured (learn.qryti.com, api.qryti.com)
- [ ] Server provisioned with adequate resources (2+ CPU, 4GB+ RAM)
- [ ] Firewall configured (ports 80, 443, 22)
- [ ] Backup storage configured
- [ ] Monitoring tools installed (optional: Prometheus, Grafana)

## Environment Configuration
- [ ] Update .env.production files with actual values
- [ ] Set secure SECRET_KEY and JWT_SECRET_KEY
- [ ] Configure email settings for notifications
- [ ] Set up database connection (PostgreSQL recommended for production)
- [ ] Configure file storage (AWS S3 recommended)

## Security Configuration
- [ ] Change default passwords and keys
- [ ] Configure rate limiting
- [ ] Set up SSL/TLS certificates
- [ ] Configure security headers
- [ ] Set up fail2ban for SSH protection
- [ ] Configure database access restrictions

## Application Deployment
- [ ] Build frontend for production (npm run build)
- [ ] Run database migrations
- [ ] Copy application files to production server
- [ ] Install and configure systemd services
- [ ] Configure Nginx reverse proxy
- [ ] Set up log rotation

## Testing
- [ ] Verify API endpoints are accessible
- [ ] Test user registration and login
- [ ] Verify certificate generation
- [ ] Test file uploads and downloads
- [ ] Check SSL certificate validity
- [ ] Verify monitoring endpoints

## Monitoring Setup
- [ ] Configure log aggregation
- [ ] Set up health check monitoring
- [ ] Configure alerting for critical issues
- [ ] Set up performance monitoring
- [ ] Configure backup monitoring

## Post-Deployment
- [ ] Verify all services are running
- [ ] Test complete user workflow
- [ ] Set up automated backups
- [ ] Configure monitoring alerts
- [ ] Document any custom configurations
- [ ] Train support team on monitoring tools

## Maintenance
- [ ] Schedule regular security updates
- [ ] Set up automated backup verification
- [ ] Plan capacity monitoring and scaling
- [ ] Document incident response procedures
- [ ] Set up log analysis and alerting
"""
        
        checklist_path = f"{self.project_root}/PRODUCTION_CHECKLIST.md"
        with open(checklist_path, 'w') as f:
            f.write(checklist)
        
        self.log_config(
            "Documentation",
            "Production Checklist",
            f"Created at {checklist_path}"
        )
    
    def generate_config_report(self):
        """Generate configuration report"""
        print("\n" + "="*60)
        print("📊 PRODUCTION CONFIGURATION REPORT")
        print("="*60)
        
        # Categorize results
        categories = {}
        for result in self.config_results:
            category = result['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # Print results by category
        for category, results in categories.items():
            print(f"\n🔧 {category.upper()}")
            print("-" * 40)
            for result in results:
                status_icon = "✅" if result['status'] == "success" else "⚠️" if result['status'] == "warning" else "❌"
                print(f"  {status_icon} {result['action']}")
                print(f"    {result['result']}")
        
        # Generate summary
        total_configs = len(self.config_results)
        successful_configs = [r for r in self.config_results if r['status'] == 'success']
        
        print(f"\n📈 SUMMARY")
        print("-" * 40)
        print(f"Total Configurations: {total_configs}")
        print(f"Successful: {len(successful_configs)}")
        print(f"Success Rate: {(len(successful_configs)/total_configs)*100:.1f}%")
        
        # Save report to file
        report_data = {
            'summary': {
                'total_configurations': total_configs,
                'successful_configurations': len(successful_configs),
                'success_rate': (len(successful_configs)/total_configs)*100,
                'generated_at': datetime.now().isoformat()
            },
            'configurations': self.config_results,
            'categories': categories
        }
        
        report_file = f"{self.project_root}/production_config_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
    
    def run_full_configuration(self):
        """Run complete production configuration setup"""
        print("🚀 Starting Production Configuration Setup")
        print("="*60)
        
        self.create_environment_files()
        self.create_nginx_config()
        self.create_systemd_services()
        self.create_deployment_scripts()
        self.create_monitoring_config()
        self.generate_production_checklist()
        self.generate_config_report()

if __name__ == "__main__":
    config = ProductionConfig()
    config.run_full_configuration()

