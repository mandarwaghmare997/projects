#!/bin/bash
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
tar -czf $BACKUP_FILE \
    -C /opt/qryti-learn backend/src/database \
    -C /opt/qryti-learn certificates \
    -C /opt/qryti-learn uploads

# Restart services
sudo systemctl start qryti-learn-api

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "qryti-backup-*.tar.gz" -mtime +7 -delete

echo "✅ Backup completed: $BACKUP_FILE"
