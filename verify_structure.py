#!/usr/bin/env python3
"""
Land Intelligence System - Project Structure Verification Script
This script verifies that all expected files and directories exist.
"""

from pathlib import Path
from typing import List, Tuple

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_exists(path: Path) -> bool:
    """Check if a path exists."""
    return path.exists()

def verify_structure() -> Tuple[int, int, List[str]]:
    """
    Verify the project structure.
    Returns: (total_items, missing_items, missing_paths)
    """
    base_path = Path(__file__).parent
    
    # Expected directories
    expected_dirs = [
        "app",
        "app/api",
        "app/api/v1",
        "app/api/v1/routes",
        "app/api/middleware",
        "app/core",
        "app/models",
        "app/schemas",
        "app/services",
        "app/services/backup",
        "app/services/backup/local",
        "app/services/backup/cloud",
        "app/services/backup/validation",
        "app/services/backup/scheduling",
        "app/services/backup/restoration",
        "app/services/backup/notifications",
        "app/services/gis",
        "app/services/document",
        "app/services/tax",
        "app/services/qr",
        "app/services/location",
        "app/repositories",
        "app/utils",
        "app/tasks",
        "alembic",
        "alembic/versions",
        "config",
        "config/backup",
        "config/desktop_app",
        "backups",
        "backups/daily",
        "backups/weekly",
        "backups/monthly",
        "backups/manifests",
        "backups/temp",
        "logs",
        "tests",
        "tests/unit",
        "tests/integration",
    ]
    
    # Expected files
    expected_files = [
        "README.md",
        "SETUP.md",
        "requirements.txt",
        "pyproject.toml",
        "alembic.ini",
        ".env.example",
        ".gitignore",
        # App files
        "app/__init__.py",
        "app/main.py",
        "app/dependencies.py",
        # API files
        "app/api/__init__.py",
        "app/api/v1/__init__.py",
        "app/api/v1/endpoints.py",
        "app/api/v1/routes/__init__.py",
        "app/api/v1/routes/parishes.py",
        "app/api/v1/routes/parcels.py",
        "app/api/v1/routes/documents.py",
        "app/api/v1/routes/gis_analysis.py",
        "app/api/v1/routes/tax_calculations.py",
        "app/api/v1/routes/qr_codes.py",
        "app/api/v1/routes/physical_locations.py",
        "app/api/v1/routes/backups.py",
        # Middleware
        "app/api/middleware/__init__.py",
        "app/api/middleware/authentication.py",
        "app/api/middleware/logging_middleware.py",
        "app/api/middleware/error_handlers.py",
        # Core
        "app/core/__init__.py",
        "app/core/config.py",
        "app/core/database.py",
        "app/core/security.py",
        "app/core/logging_config.py",
        "app/core/backup_config.py",
        # Models
        "app/models/__init__.py",
        "app/models/base.py",
        "app/models/parish.py",
        "app/models/parcel.py",
        "app/models/document.py",
        "app/models/document_type.py",
        "app/models/tax_record.py",
        "app/models/tax_payment.py",
        "app/models/land_use_category.py",
        "app/models/physical_location.py",
        "app/models/storage_cabinet.py",
        "app/models/qr_code_registry.py",
        "app/models/audit_log.py",
        "app/models/backup_job.py",
        "app/models/backup_verification.py",
        # Schemas
        "app/schemas/__init__.py",
        "app/schemas/parish_schema.py",
        "app/schemas/parcel_schema.py",
        "app/schemas/document_schema.py",
        "app/schemas/tax_schema.py",
        "app/schemas/qr_code_schema.py",
        "app/schemas/physical_location_schema.py",
        "app/schemas/gis_analysis_schema.py",
        "app/schemas/backup_job_schema.py",
        "app/schemas/backup_verification_schema.py",
        # Backup services
        "app/services/__init__.py",
        "app/services/backup/__init__.py",
        "app/services/backup/backup_orchestrator.py",
        "app/services/backup/local/__init__.py",
        "app/services/backup/local/database_backup_service.py",
        "app/services/backup/local/filesystem_backup_service.py",
        "app/services/backup/local/config_backup_service.py",
        "app/services/backup/local/local_backup_manager.py",
        "app/services/backup/cloud/__init__.py",
        "app/services/backup/cloud/cloud_storage_interface.py",
        "app/services/backup/cloud/google_cloud_storage_provider.py",
        "app/services/backup/cloud/backblaze_b2_provider.py",
        "app/services/backup/cloud/cloud_upload_service.py",
        "app/services/backup/cloud/cloud_download_service.py",
        "app/services/backup/cloud/encryption_service.py",
        "app/services/backup/validation/__init__.py",
        "app/services/backup/validation/integrity_checker.py",
        "app/services/backup/validation/backup_verifier.py",
        "app/services/backup/validation/manifest_validator.py",
        "app/services/backup/validation/restore_tester.py",
        "app/services/backup/scheduling/__init__.py",
        "app/services/backup/scheduling/backup_scheduler.py",
        "app/services/backup/scheduling/job_executor.py",
        "app/services/backup/scheduling/retry_handler.py",
        "app/services/backup/restoration/__init__.py",
        "app/services/backup/restoration/restore_orchestrator.py",
        "app/services/backup/restoration/database_restore_service.py",
        "app/services/backup/restoration/filesystem_restore_service.py",
        "app/services/backup/restoration/restore_validator.py",
        "app/services/backup/notifications/__init__.py",
        "app/services/backup/notifications/email_notifier.py",
        "app/services/backup/notifications/backup_reporter.py",
        "app/services/backup/notifications/failure_alerter.py",
        # Other services
        "app/services/gis/__init__.py",
        "app/services/gis/spatial_analyzer.py",
        "app/services/gis/polygon_intersection.py",
        "app/services/gis/area_calculator.py",
        "app/services/gis/masterplan_overlay.py",
        "app/services/document/__init__.py",
        "app/services/document/document_manager.py",
        "app/services/document/file_system_handler.py",
        "app/services/document/metadata_extractor.py",
        "app/services/document/pointer_resolver.py",
        "app/services/tax/__init__.py",
        "app/services/tax/tax_calculator.py",
        "app/services/tax/penalty_engine.py",
        "app/services/tax/assessment_generator.py",
        "app/services/tax/payment_processor.py",
        "app/services/qr/__init__.py",
        "app/services/qr/qr_generator.py",
        "app/services/qr/digital_testimony_builder.py",
        "app/services/qr/verification_service.py",
        "app/services/location/__init__.py",
        "app/services/location/physical_finder.py",
        "app/services/location/storage_mapper.py",
        "app/services/location/location_validator.py",
        # Repositories
        "app/repositories/__init__.py",
        "app/repositories/base_repository.py",
        "app/repositories/parish_repository.py",
        "app/repositories/parcel_repository.py",
        "app/repositories/document_repository.py",
        "app/repositories/tax_repository.py",
        "app/repositories/location_repository.py",
        "app/repositories/qr_registry_repository.py",
        "app/repositories/backup_job_repository.py",
        "app/repositories/backup_verification_repository.py",
        # Utils
        "app/utils/__init__.py",
        "app/utils/geometry_helpers.py",
        "app/utils/file_validators.py",
        "app/utils/date_helpers.py",
        "app/utils/coordinate_transformations.py",
        "app/utils/checksum_calculator.py",
        "app/utils/compression_helper.py",
        "app/utils/path_resolver.py",
        # Tasks
        "app/tasks/__init__.py",
        "app/tasks/celery_app.py",
        "app/tasks/scheduled_tasks.py",
        "app/tasks/background_workers.py",
        # Alembic
        "alembic/env.py",
        "alembic/script.py.mako",
        # Config files
        "config/backup/backup_schedule.yaml",
        "config/backup/cloud_providers.yaml",
        "config/backup/retention_policies.yaml",
        "config/backup/notification_rules.yaml",
        "config/desktop_app/local_paths.yaml",
        "config/desktop_app/service_settings.yaml",
        # Tests
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/unit/test_gis_services.py",
        "tests/unit/test_tax_calculator.py",
        "tests/unit/test_qr_generator.py",
        "tests/unit/test_repositories.py",
        "tests/unit/test_backup_orchestrator.py",
        "tests/unit/test_cloud_providers.py",
        "tests/unit/test_integrity_checker.py",
        "tests/integration/test_api_endpoints.py",
        "tests/integration/test_database_operations.py",
        "tests/integration/test_file_system_integration.py",
        "tests/integration/test_backup_workflow.py",
        "tests/integration/test_restore_workflow.py",
    ]
    
    total_items = len(expected_dirs) + len(expected_files)
    missing = []
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Land Intelligence System - Structure Verification{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Check directories
    print(f"{YELLOW}Checking directories...{RESET}")
    missing_dirs = 0
    for dir_path in expected_dirs:
        full_path = base_path / dir_path
        if check_exists(full_path):
            print(f"{GREEN}✓{RESET} {dir_path}")
        else:
            print(f"{RED}✗{RESET} {dir_path} {RED}(MISSING){RESET}")
            missing.append(dir_path)
            missing_dirs += 1
    
    # Check files
    print(f"\n{YELLOW}Checking files...{RESET}")
    missing_files = 0
    for file_path in expected_files:
        full_path = base_path / file_path
        if check_exists(full_path):
            print(f"{GREEN}✓{RESET} {file_path}")
        else:
            print(f"{RED}✗{RESET} {file_path} {RED}(MISSING){RESET}")
            missing.append(file_path)
            missing_files += 1
    
    # Summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Verification Summary{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"Total items checked: {total_items}")
    print(f"{GREEN}Found: {total_items - len(missing)}{RESET}")
    print(f"{RED}Missing: {len(missing)}{RESET}")
    
    if missing:
        print(f"\n{RED}Missing items:{RESET}")
        print(f"  Directories: {missing_dirs}")
        print(f"  Files: {missing_files}")
    else:
        print(f"\n{GREEN}✓ All files and directories are present!{RESET}")
        print(f"{GREEN}✓ Project structure is complete.{RESET}")
    
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    return total_items, len(missing), missing

if __name__ == "__main__":
    total, missing_count, missing_list = verify_structure()
    
    if missing_count > 0:
        print(f"{YELLOW}Note: Some files/directories are missing.{RESET}")
        print(f"{YELLOW}This might be expected if you're still setting up.{RESET}\n")
        exit(1)
    else:
        print(f"{GREEN}Ready to start development!{RESET}")
        print(f"{GREEN}Run 'pip install -r requirements.txt' to install dependencies.{RESET}\n")
        exit(0)
