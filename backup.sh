#!/bin/bash

export PGPASSWORD=$DB_PASSWORD
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER

# Директория для бэкапов
BACKUP_DIR="/backups"
mkdir -p $BACKUP_DIR

# Имя файла бэкапа
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
BACKUP_FILE="$BACKUP_DIR/$DB_NAME-$TIMESTAMP.sql"

# Создание бэкапа
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -F c -b -v > $BACKUP_FILE

# Логирование
echo "Backup created: $BACKUP_FILE"

# Удаление бэкапов старше 7 дней
find $BACKUP_DIR -type f -mtime +7 -exec rm {} \;
echo "Old backups deleted."
