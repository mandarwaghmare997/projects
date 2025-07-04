# Qryti Learn Deployment Guide

## 🚀 **Production Deployment Guide**

This guide provides comprehensive instructions for deploying Qryti Learn in production environments.

## 📋 **Prerequisites**

### **System Requirements**

#### Minimum Requirements
- **CPU:** 2 cores
- **RAM:** 4GB
- **Storage:** 20GB SSD
- **Network:** 100 Mbps

#### Recommended Requirements
- **CPU:** 4 cores
- **RAM:** 8GB
- **Storage:** 50GB SSD
- **Network:** 1 Gbps

### **Software Dependencies**

- **Docker:** 20.0 or higher
- **Docker Compose:** 2.0 or higher
- **Git:** Latest version
- **SSL Certificate:** For HTTPS (recommended)

### **Network Requirements**

- **Ports:** 80 (HTTP), 443 (HTTPS), 5000 (API)
- **Firewall:** Configure to allow web traffic
- **Domain:** Configured DNS pointing to server

## 🔧 **Environment Setup**

### **1. Server Preparation**

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### **2. Application Deployment**

```bash
# Clone repository
git clone <repository-url>
cd qryti-learn

# Create production environment file
cp .env.example .env
nano .env  # Edit with production values
```

### **3. Environment Configuration**

Create `.env` file with production settings:

```env
# Security Configuration
JWT_SECRET_KEY=<generate-strong-32-char-key>
FLASK_ENV=production

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/qryti_learn
POSTGRES_PASSWORD=<secure-database-password>

# Application Configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
API_BASE_URL=https://api.yourdomain.com

# SSL Configuration (if using HTTPS)
SSL_CERT_PATH=/etc/ssl/certs/yourdomain.crt
SSL_KEY_PATH=/etc/ssl/private/yourdomain.key

# AWS Configuration (optional)
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>
S3_BUCKET_NAME=qryti-certificates
AWS_REGION=us-east-1

# Email Configuration (optional)
SMTP_SERVER=smtp.yourdomain.com
SMTP_PORT=587
SMTP_USERNAME=noreply@yourdomain.com
SMTP_PASSWORD=<email-password>

# Monitoring (optional)
SENTRY_DSN=<your-sentry-dsn>
LOG_LEVEL=INFO
```

## 🐳 **Docker Deployment**

### **Standard Deployment**

```bash
# Deploy the application
./deploy.sh

# Verify deployment
./deploy.sh status

# View logs
./deploy.sh logs
```

### **Custom Docker Compose**

For advanced configurations, modify `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./ssl:/etc/ssl
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: qryti_learn
      POSTGRES_USER: qryti_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## 🌐 **Web Server Configuration**

### **Nginx Configuration (Standalone)**

If not using Docker for frontend:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=63072000" always;

    # Frontend
    location / {
        root /var/www/qryti-learn;
        try_files $uri $uri/ /index.html;
    }

    # API Proxy
    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🗄️ **Database Setup**

### **PostgreSQL Setup**

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE qryti_learn;
CREATE USER qryti_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE qryti_learn TO qryti_user;
\q

# Configure PostgreSQL
sudo nano /etc/postgresql/15/main/postgresql.conf
# Set: listen_addresses = 'localhost'

sudo nano /etc/postgresql/15/main/pg_hba.conf
# Add: local qryti_learn qryti_user md5

sudo systemctl restart postgresql
```

### **Database Migration**

```bash
# Run database migrations
docker-compose exec backend python -c "
from src.models.user import db
from src.main import create_app
app = create_app('production')
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
```

## 🔒 **SSL/TLS Configuration**

### **Let's Encrypt (Recommended)**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **Custom SSL Certificate**

```bash
# Copy certificates
sudo cp yourdomain.crt /etc/ssl/certs/
sudo cp yourdomain.key /etc/ssl/private/
sudo chmod 600 /etc/ssl/private/yourdomain.key
```

## 📊 **Monitoring & Logging**

### **Application Monitoring**

```bash
# View application logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Monitor resource usage
docker stats

# Health checks
curl https://yourdomain.com/health
curl https://api.yourdomain.com/health
```

### **Log Management**

```bash
# Configure log rotation
sudo nano /etc/logrotate.d/qryti-learn

/var/log/qryti-learn/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        docker-compose restart backend frontend
    endscript
}
```

### **Performance Monitoring**

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor database performance
sudo -u postgres psql qryti_learn
SELECT * FROM pg_stat_activity;
```

## 🔄 **Backup & Recovery**

### **Database Backup**

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/qryti-learn"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec -T postgres pg_dump -U qryti_user qryti_learn > $BACKUP_DIR/db_$DATE.sql

# Application data backup
tar -czf $BACKUP_DIR/data_$DATE.tar.gz ./data ./uploads

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

# Schedule daily backups
sudo crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

### **Recovery Process**

```bash
# Restore database
docker-compose exec -T postgres psql -U qryti_user qryti_learn < backup_file.sql

# Restore application data
tar -xzf data_backup.tar.gz

# Restart services
docker-compose restart
```

## 🚀 **Scaling & Performance**

### **Horizontal Scaling**

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  backend:
    deploy:
      replicas: 3
    ports:
      - "5000-5002:5000"

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    depends_on:
      - backend
```

### **Load Balancer Configuration**

```nginx
upstream backend {
    server backend_1:5000;
    server backend_2:5000;
    server backend_3:5000;
}

server {
    listen 80;
    location /api/ {
        proxy_pass http://backend;
    }
}
```

### **Performance Optimization**

```bash
# Enable Redis caching
docker run -d --name redis -p 6379:6379 redis:alpine

# Configure application caching
# Add to .env:
REDIS_URL=redis://localhost:6379/0
CACHE_TIMEOUT=3600
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Service Won't Start**
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Check ports
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :5000

# Restart services
docker-compose restart
```

#### **Database Connection Issues**
```bash
# Test database connection
docker-compose exec backend python -c "
from src.models.user import db
from src.main import create_app
app = create_app('production')
with app.app_context():
    try:
        db.engine.execute('SELECT 1')
        print('Database connection successful')
    except Exception as e:
        print(f'Database connection failed: {e}')
"
```

#### **SSL Certificate Issues**
```bash
# Check certificate validity
openssl x509 -in /etc/ssl/certs/yourdomain.crt -text -noout

# Test SSL configuration
curl -I https://yourdomain.com
```

### **Performance Issues**

```bash
# Monitor resource usage
docker stats

# Check database performance
docker-compose exec postgres psql -U qryti_user qryti_learn -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
"

# Optimize database
docker-compose exec postgres psql -U qryti_user qryti_learn -c "VACUUM ANALYZE;"
```

## 📞 **Support & Maintenance**

### **Regular Maintenance Tasks**

1. **Weekly:**
   - Check application logs
   - Monitor disk space
   - Verify backups

2. **Monthly:**
   - Update system packages
   - Review security logs
   - Performance analysis

3. **Quarterly:**
   - Update application dependencies
   - Security audit
   - Disaster recovery testing

### **Emergency Procedures**

```bash
# Emergency shutdown
docker-compose down

# Emergency restart
docker-compose up -d

# Rollback deployment
git checkout previous-version
./deploy.sh

# Emergency backup
./backup.sh
```

### **Contact Information**

- **Technical Support:** support@qryti.com
- **Emergency Contact:** emergency@qryti.com
- **Documentation:** https://docs.qryti.com

---

**Last Updated:** July 4, 2025  
**Version:** 2.0.0  
**Status:** Production Ready

