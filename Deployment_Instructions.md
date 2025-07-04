# Qryti Learn Phase 6 Deployment Instructions

## 🚀 **Deployment Overview**

This document provides step-by-step instructions for deploying the Phase 6 enhanced Qryti Learn platform with the new certification system, analytics dashboard, and achievement features.

## 📋 **Pre-Deployment Checklist**

### Backend Requirements
- ✅ Python 3.11+ installed
- ✅ All dependencies in `requirements.txt` installed
- ✅ Database configured and accessible
- ✅ SSL certificates for HTTPS (production)
- ✅ Environment variables configured

### Frontend Requirements
- ✅ Node.js 20+ installed
- ✅ npm/yarn package manager
- ✅ All dependencies in `package.json` installed
- ✅ Build process tested
- ✅ Static file hosting configured

## 🔧 **Backend Deployment**

### 1. Environment Setup
```bash
# Clone or update the repository
cd /path/to/qryti-learn/backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
export JWT_SECRET_KEY=your-jwt-secret-key
export DATABASE_URL=your-production-database-url
```

### 2. Database Migration
```bash
# Initialize database with new models
python -c "
from src.main import create_app
from src.models.user import db
app = create_app('production')
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"
```

### 3. Start Backend Server
```bash
# For production deployment
gunicorn -w 4 -b 0.0.0.0:5001 src.main:app

# For development testing
python -m src.main
```

### 4. Verify Backend Endpoints
```bash
# Test health endpoint
curl -X GET https://your-domain.com/health

# Test certificate stats (public endpoint)
curl -X GET https://your-domain.com/api/certificates/stats

# Test analytics endpoint (requires authentication)
curl -X GET https://your-domain.com/api/analytics/summary \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🌐 **Frontend Deployment**

### 1. Build Process
```bash
# Navigate to frontend directory
cd /path/to/qryti-learn/frontend

# Install dependencies
npm install

# Update API base URL for production
# Edit src/services/api.js and set production URL
# const API_BASE_URL = 'https://api.your-domain.com'

# Build for production
npm run build
```

### 2. Deploy Static Files
```bash
# The build folder contains all static files
# Deploy contents of 'dist' folder to your web server
# Example for nginx:
sudo cp -r dist/* /var/www/html/qryti-learn/

# Example for Apache:
sudo cp -r dist/* /var/www/html/qryti-learn/
```

### 3. Configure Web Server

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Frontend static files
    location / {
        root /var/www/html/qryti-learn;
        try_files $uri $uri/ /index.html;
    }
    
    # API proxy to backend
    location /api/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://localhost:5001;
    }
}
```

#### Apache Configuration
```apache
<VirtualHost *:80>
    ServerName your-domain.com
    Redirect permanent / https://your-domain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName your-domain.com
    
    SSLEngine on
    SSLCertificateFile /path/to/certificate.crt
    SSLCertificateKeyFile /path/to/private.key
    
    DocumentRoot /var/www/html/qryti-learn
    
    # Frontend routing
    <Directory /var/www/html/qryti-learn>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
        
        # React Router support
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>
    
    # API proxy
    ProxyPreserveHost On
    ProxyPass /api/ http://localhost:5001/api/
    ProxyPassReverse /api/ http://localhost:5001/api/
    ProxyPass /health http://localhost:5001/health
    ProxyPassReverse /health http://localhost:5001/health
</VirtualHost>
```

## 🔐 **Security Configuration**

### 1. SSL/TLS Setup
```bash
# Install SSL certificate (Let's Encrypt example)
sudo certbot --nginx -d your-domain.com

# Or for Apache
sudo certbot --apache -d your-domain.com
```

### 2. Firewall Configuration
```bash
# Allow HTTP and HTTPS traffic
sudo ufw allow 80
sudo ufw allow 443

# Allow backend port (if needed)
sudo ufw allow 5001

# Enable firewall
sudo ufw enable
```

### 3. Environment Variables (Production)
```bash
# Create production environment file
cat > /path/to/qryti-learn/backend/.env << EOF
FLASK_ENV=production
SECRET_KEY=your-super-secure-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/qryti_learn_prod
CORS_ORIGINS=https://your-domain.com
EOF
```

## 📊 **Database Setup**

### 1. PostgreSQL (Recommended for Production)
```sql
-- Create production database
CREATE DATABASE qryti_learn_prod;
CREATE USER qryti_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE qryti_learn_prod TO qryti_user;
```

### 2. Database Migration
```bash
# Run database initialization
python -c "
from src.main import create_app
from src.models.user import db
from src.models.course import Course, Module, CourseEnrollment
from src.models.quiz import Quiz, Question, QuizAttempt
from src.models.progress import UserProgress, Certificate, LearningAnalytics

app = create_app('production')
with app.app_context():
    db.create_all()
    print('All database tables created successfully')
"
```

## 🔍 **Testing Deployment**

### 1. Backend Health Check
```bash
# Test all critical endpoints
curl -X GET https://your-domain.com/health
curl -X GET https://your-domain.com/api/certificates/stats
curl -X GET https://your-domain.com/api/courses/
```

### 2. Frontend Functionality
- ✅ Landing page loads correctly
- ✅ User registration and login work
- ✅ Dashboard displays properly
- ✅ Certificate system functions
- ✅ Analytics dashboard loads
- ✅ Achievement system works
- ✅ Mobile responsiveness verified

### 3. Certificate System Test
```bash
# Test certificate verification (replace with actual certificate ID)
curl -X GET https://your-domain.com/api/certificates/verify/CERT123456
```

## 📈 **Monitoring & Maintenance**

### 1. Log Monitoring
```bash
# Backend logs
tail -f /var/log/qryti-learn/backend.log

# Web server logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 2. Performance Monitoring
- Set up application performance monitoring (APM)
- Monitor certificate generation performance
- Track API response times
- Monitor database performance

### 3. Backup Strategy
```bash
# Database backup
pg_dump qryti_learn_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Certificate files backup
tar -czf certificates_backup_$(date +%Y%m%d).tar.gz /path/to/certificates/
```

## 🚨 **Troubleshooting**

### Common Issues

1. **Certificate Generation Fails**
   - Check ReportLab installation
   - Verify file permissions for certificate storage
   - Check disk space availability

2. **Analytics Not Loading**
   - Verify database connection
   - Check JWT token validity
   - Ensure analytics routes are registered

3. **Frontend Build Issues**
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules and reinstall
   - Check for syntax errors in new components

4. **API Connection Issues**
   - Verify CORS configuration
   - Check API base URL in frontend
   - Ensure backend is running and accessible

### Debug Commands
```bash
# Check backend status
ps aux | grep python
netstat -tlnp | grep 5001

# Check frontend build
npm run build -- --verbose

# Test API connectivity
curl -v https://your-domain.com/api/health
```

## 📞 **Support & Documentation**

### API Documentation
- Backend API endpoints documented in code
- Swagger/OpenAPI documentation available at `/api/docs`
- Postman collection available for testing

### User Documentation
- User guides for new certificate features
- Admin documentation for system management
- Video tutorials for key features

## ✅ **Deployment Verification Checklist**

- [ ] Backend health endpoint responds correctly
- [ ] Frontend loads and displays properly
- [ ] User authentication works
- [ ] Certificate generation functions
- [ ] Certificate verification works
- [ ] Analytics dashboard loads data
- [ ] Achievement system functions
- [ ] Mobile responsiveness verified
- [ ] SSL certificate installed and working
- [ ] Database backup configured
- [ ] Monitoring systems active
- [ ] Error logging configured

---

**Deployment Guide Version:** 1.0  
**Last Updated:** July 4, 2025  
**Compatible with:** Qryti Learn Phase 6  
**Support Contact:** development@qryti.com

