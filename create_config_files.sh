#!/bin/bash

# Create YAML configuration files with comments

# Backup schedule configuration
cat > config/backup/backup_schedule.yaml << 'YAML_EOF'
# =============================================================================
# BACKUP SCHEDULE CONFIGURATION
# =============================================================================
# Define automated backup schedules using cron expressions
# Format: "minute hour day month day_of_week"
# =============================================================================

schedules:
  # Daily incremental backup
  daily_incremental:
    enabled: true
    backup_type: INCREMENTAL
    tiers: 
      - LOCAL
      - CLOUD
    cron: "0 3 * * *"  # Every day at 3:00 AM
    retention_days: 30
    description: "Daily incremental backup of changed files and data"
    
  # Weekly full backup
  weekly_full:
    enabled: true
    backup_type: FULL
    tiers:
      - LOCAL
      - CLOUD
    cron: "0 2 * * 0"  # Every Sunday at 2:00 AM
    retention_days: 84  # 12 weeks
    description: "Complete system backup including database and documents"
    
  # Monthly archive
  monthly_archive:
    enabled: true
    backup_type: ARCHIVE
    tiers:
      - CLOUD
    cron: "0 2 1 * *"  # 1st day of every month at 2:00 AM
    retention_days: 2555  # ~7 years for legal compliance
    description: "Long-term archival backup for compliance"

# Global backup settings
global_settings:
  max_concurrent_backups: 1
  timeout_minutes: 120
  verify_after_backup: true
  notify_on_completion: true
  notify_on_failure: true
YAML_EOF

# Cloud providers configuration
cat > config/backup/cloud_providers.yaml << 'YAML_EOF'
# =============================================================================
# CLOUD STORAGE PROVIDERS CONFIGURATION
# =============================================================================
# Configure cloud backup destinations
# =============================================================================

# Active provider selection
active_provider: google_cloud_storage  # Options: google_cloud_storage, backblaze_b2

providers:
  google_cloud_storage:
    enabled: true
    project_id: "church-land-intelligence"
    bucket_name: "land-intelligence-backups"
    credentials_path: "/path/to/service-account-key.json"
    region: "us-central1"
    storage_class: "STANDARD"  # Options: STANDARD, NEARLINE, COLDLINE, ARCHIVE
    
    # Client-side encryption (optional)
    encryption:
      enabled: false
      key_path: "/secure/encryption.key"
      algorithm: "AES256"
    
    # Lifecycle management
    lifecycle:
      enabled: true
      transition_to_nearline_days: 90
      transition_to_coldline_days: 365
      delete_after_days: 2555  # 7 years
    
  backblaze_b2:
    enabled: false
    account_id: "your_account_id"
    application_key_path: "/path/to/b2-key.txt"
    bucket_name: "church-backups"
    
    # Encryption
    encryption:
      enabled: false
      key_path: "/secure/b2-encryption.key"
    
    # Lifecycle rules
    lifecycle:
      enabled: true
      keep_days: 2555

# Upload settings
upload_settings:
  chunk_size_mb: 10
  max_retries: 3
  retry_delay_seconds: 60
  use_compression: true
  verify_checksums: true
YAML_EOF

# Retention policies
cat > config/backup/retention_policies.yaml << 'YAML_EOF'
# =============================================================================
# BACKUP RETENTION POLICIES
# =============================================================================
# Define how long backups are kept in different storage tiers
# =============================================================================

retention:
  # Daily incremental backups
  daily_incremental:
    local: 7  # Keep for 7 days locally
    cloud: 30  # Keep for 30 days in cloud
    description: "Quick recovery for recent changes"
    
  # Weekly full backups
  weekly_full:
    local: 28  # Keep for 4 weeks locally
    cloud: 84  # Keep for 12 weeks in cloud
    description: "Medium-term recovery point"
    
  # Monthly archives
  monthly_archive:
    local: 90  # Keep for 3 months locally
    cloud: 2555  # Keep forever in cloud (~7 years)
    description: "Long-term compliance and disaster recovery"
    
  # Special retention
  verification_logs:
    retention_days: 365
    description: "Keep verification logs for 1 year"
    
  audit_logs:
    retention_days: 2555
    description: "Legal compliance requirement - 7 years"

# Cleanup settings
cleanup:
  enabled: true
  schedule: "0 4 * * *"  # Daily at 4:00 AM
  grace_period_days: 7  # Keep expired backups for 7 extra days
  notify_before_deletion: true
YAML_EOF

# Notification rules
cat > config/backup/notification_rules.yaml << 'YAML_EOF'
# =============================================================================
# NOTIFICATION RULES CONFIGURATION
# =============================================================================
# Configure email alerts and notifications for backup events
# =============================================================================

notifications:
  email:
    enabled: true
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    use_tls: true
    sender: "backup-system@church.org"
    sender_name: "Land Intelligence Backup System"
    
    # Recipients
    recipients:
      - email: "it-admin@church.org"
        name: "IT Administrator"
        role: "admin"
      - email: "land-records-officer@church.org"
        name: "Land Records Officer"
        role: "user"
    
  # Event-based notifications
  events:
    backup_success:
      enabled: true
      send_to: ["admin"]
      include_details: true
      
    backup_failure:
      enabled: true
      send_to: ["admin", "user"]
      priority: "high"
      include_logs: true
      
    verification_failure:
      enabled: true
      send_to: ["admin"]
      priority: "high"
      
    weekly_summary:
      enabled: true
      send_to: ["admin", "user"]
      schedule: "0 9 * * 1"  # Monday 9:00 AM
      
    storage_quota_warning:
      enabled: true
      send_to: ["admin"]
      threshold_percent: 80
      
    restore_completed:
      enabled: true
      send_to: ["admin", "user"]
      priority: "high"
  
  # Email templates
  templates:
    success_subject: "✅ Backup Successful - {date}"
    failure_subject: "❌ BACKUP FAILED - {date} - Action Required"
    verification_failure_subject: "⚠️ Backup Verification Failed - {date}"
    weekly_summary_subject: "📊 Weekly Backup Summary - Week of {date}"
    
  # Notification throttling
  throttling:
    enabled: true
    max_emails_per_hour: 10
    min_interval_minutes: 15
YAML_EOF

# Desktop app paths
cat > config/desktop_app/local_paths.yaml << 'YAML_EOF'
# =============================================================================
# DESKTOP APPLICATION - LOCAL PATHS CONFIGURATION
# =============================================================================
# Single-machine deployment path settings
# =============================================================================

application:
  mode: "desktop"  # Single-machine mode
  deployment_type: "standalone"

# Network settings (localhost only)
network:
  database:
    host: "localhost"
    port: 3306
    
  fastapi:
    host: "127.0.0.1"
    port: 8000
    workers: 1

# File system paths
# IMPORTANT: Update these paths based on your operating system
paths:
  # Windows paths (uncomment for Windows)
  # storage_root: "C:/LandIntelligence"
  # documents: "C:/LandIntelligence/documents"
  # backups_local: "C:/LandIntelligence/backups"
  # logs: "C:/LandIntelligence/logs"
  # temp: "C:/LandIntelligence/temp"
  # qr_codes: "C:/LandIntelligence/qr-codes"
  # gis_data: "C:/LandIntelligence/gis-data"
  
  # Linux paths (uncomment for Linux)
  storage_root: "/home/user/LandIntelligence"
  documents: "/home/user/LandIntelligence/documents"
  backups_local: "/home/user/LandIntelligence/backups"
  logs: "/home/user/LandIntelligence/logs"
  temp: "/home/user/LandIntelligence/temp"
  qr_codes: "/home/user/LandIntelligence/qr-codes"
  gis_data: "/home/user/LandIntelligence/gis-data"

# Auto-create directories on startup
auto_create_directories: true
directory_permissions: "755"  # Linux only
YAML_EOF

# Service settings
cat > config/desktop_app/service_settings.yaml << 'YAML_EOF'
# =============================================================================
# DESKTOP APPLICATION - SERVICE SETTINGS
# =============================================================================
# Local service configuration for single-machine deployment
# =============================================================================

# FastAPI service
fastapi:
  host: "127.0.0.1"
  port: 8000
  reload: true  # Set to false in production
  workers: 1
  log_level: "info"
  access_log: true

# MySQL service
mysql:
  host: "localhost"
  port: 3306
  socket: null  # Use socket on Linux: "/var/run/mysqld/mysqld.sock"
  charset: "utf8mb4"
  collation: "utf8mb4_unicode_ci"

# Service management
service_management:
  # Windows
  windows:
    mysql_service_name: "MySQL80"
    fastapi_service_name: "LandIntelligenceAPI"
    use_nssm: true  # Use NSSM for Windows service management
    
  # Linux
  linux:
    mysql_service_name: "mysql"
    fastapi_service_name: "land-intelligence-api"
    use_systemd: true

# Startup behavior
startup:
  auto_start_services: true
  wait_for_database: true
  database_timeout_seconds: 30
  run_migrations_on_startup: false  # Set to true for development

# Shutdown behavior
shutdown:
  graceful_timeout_seconds: 30
  backup_on_shutdown: false
YAML_EOF

echo "All YAML configuration files created!"
