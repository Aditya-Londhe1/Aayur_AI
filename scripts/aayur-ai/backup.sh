#!/bin/bash
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Creating backup in $BACKUP_DIR..."

# Backup database
cp database/aayurai.db "$BACKUP_DIR/"

# Backup uploads
cp -r uploads "$BACKUP_DIR/"

# Backup reports
cp -r reports "$BACKUP_DIR/"

# Backup logs
cp -r logs "$BACKUP_DIR/"

# Create backup info
cat > "$BACKUP_DIR/backup-info.txt" << INFO
Backup Date: $(date)
Backup Directory: $BACKUP_DIR
Database Size: $(du -h database/aayurai.db | cut -f1)
Uploads Size: $(du -sh uploads | cut -f1)
Reports Size: $(du -sh reports | cut -f1)
INFO

echo "Backup completed: $BACKUP_DIR"
