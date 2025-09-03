#!/bin/bash

BACKUP_DIR="/app/backup"
DAYS_TO_KEEP=3
CURRENT_DATE=$(date +%Y-%m-%d)

# Find and delete backups older than $DAYS_TO_KEEP days based on their filename date
find "$BACKUP_DIR" -type f -name 'backup_*.sqlite3' | while read -r file; do
    # Extract the date from the filename (assuming format 'backup_YYYY-MM-DD.sqlite3')
    filename=$(basename "$file")
    file_date=$(echo "$filename" | awk -F'[_.]' '{print $2}')

    # Check if the file is older than the specified number of days
    if [[ "$file_date" < $(date -d "$CURRENT_DATE - $DAYS_TO_KEEP days" +%Y-%m-%d) ]]; then
        echo "Deleting old backup: $file"
        rm "$file"
    fi
done