#!/bin/bash
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
