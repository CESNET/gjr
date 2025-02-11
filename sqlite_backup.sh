#!/bin/bash

# Set the date format for the filename
DATE=$(date +"%Y-%m-%d")

# Path to the database and the backup directory
DB_PATH="/app/django_server_files/db.sqlite3"
BACKUP_DIR="/app/backup"
BACKUP_FILE="${BACKUP_DIR}/backup_${DATE}.sqlite3"

# Create a backup
sqlite3 $DB_PATH ".backup $BACKUP_FILE"

# Print success message
echo "Database backup created at $BACKUP_FILE"
