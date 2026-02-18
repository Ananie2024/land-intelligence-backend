#!/bin/bash

# Create main app directory structure
mkdir -p app/api/v1/routes
mkdir -p app/api/middleware
mkdir -p app/core
mkdir -p app/models
mkdir -p app/schemas
mkdir -p app/services/backup/local
mkdir -p app/services/backup/cloud
mkdir -p app/services/backup/validation
mkdir -p app/services/backup/scheduling
mkdir -p app/services/backup/restoration
mkdir -p app/services/backup/notifications
mkdir -p app/services/gis
mkdir -p app/services/document
mkdir -p app/services/tax
mkdir -p app/services/qr
mkdir -p app/services/location
mkdir -p app/repositories
mkdir -p app/utils
mkdir -p app/tasks

# Create alembic directory
mkdir -p alembic/versions

# Create config directory
mkdir -p config/backup
mkdir -p config/desktop_app

# Create backups directory
mkdir -p backups/daily
mkdir -p backups/weekly
mkdir -p backups/monthly
mkdir -p backups/manifests
mkdir -p backups/temp

# Create logs directory
mkdir -p logs

# Create tests directory
mkdir -p tests/unit
mkdir -p tests/integration

echo "Directory structure created successfully!"
