"""Unit tests for backup integrity checker and verifier."""
import pytest
import hashlib
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

from app.models.backup_job import BackupJobStatus
from app.services.backup.validation.integrity_checker import IntegrityChecker
from app.services.backup.validation.backup_verifier import BackupVerifier
from app.services.backup.validation.manifest_validator import ManifestValidator
from app.services.backup.validation.restore_tester import RestoreTester


@pytest.fixture
def completed_job(tmp_path):
    """Create a mock backup job pointing to a real file."""
    archive = tmp_path / "backup.zip"
    archive.write_bytes(b"dummy backup content")
    job = MagicMock()
    job.id = str(uuid4())
    job.status = BackupJobStatus.COMPLETED.value
    job.destination_path = str(archive)
    job.checksum = hashlib.sha256(b"dummy backup content").hexdigest()
    return job


@pytest.fixture
def failed_job():
    job = MagicMock()
    job.id = str(uuid4())
    job.status = BackupJobStatus.FAILED.value
    job.destination_path = "/nonexistent/backup.zip"
    job.checksum = "abc123"
    return job


class TestIntegrityChecker:
    def test_check_success(self, completed_job):
        checker = IntegrityChecker()
        assert checker.check(completed_job) is True

    def test_check_failed_status(self, failed_job):
        checker = IntegrityChecker()
        assert checker.check(failed_job) is False

    def test_check_missing_file(self):
        checker = IntegrityChecker()
        job = MagicMock()
        job.status = BackupJobStatus.COMPLETED.value
        job.destination_path = "/nonexistent/backup.zip"
        job.checksum = None
        assert checker.check(job) is False

    def test_check_checksum_mismatch(self, tmp_path):
        archive = tmp_path / "backup.zip"
        archive.write_bytes(b"original content")
        checker = IntegrityChecker()
        job = MagicMock()
        job.status = BackupJobStatus.COMPLETED.value
        job.destination_path = str(archive)
        job.checksum = "0" * 64  # wrong checksum
        assert checker.check(job) is False


class TestBackupVerifier:
    def test_verify_success(self, completed_job, tmp_path):
        """Successful verification requires valid zip + checksum match."""
        import zipfile
        zip_path = tmp_path / "valid.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("data.txt", "test")
        job = MagicMock()
        job.id = str(uuid4())
        job.status = BackupJobStatus.COMPLETED.value
        job.destination_path = str(zip_path)
        job.checksum = hashlib.sha256(Path(str(zip_path)).read_bytes()).hexdigest()
        verifier = BackupVerifier()
        assert verifier.verify(job) is True

    def test_verify_failed_status(self, failed_job):
        verifier = BackupVerifier()
        assert verifier.verify(failed_job) is False

    def test_verify_not_a_zip(self, tmp_path):
        txt = tmp_path / "backup.txt"
        txt.write_bytes(b"not a zip")
        job = MagicMock()
        job.status = BackupJobStatus.COMPLETED.value
        job.destination_path = str(txt)
        verifier = BackupVerifier()
        assert verifier.verify(job) is False


class TestManifestValidator:
    def test_validate_success(self, tmp_path):
        archive = tmp_path / "archive.zip"
        archive.write_bytes(b"data")
        checksum = hashlib.sha256(b"data").hexdigest()
        manifest = tmp_path / "manifest.json"
        manifest.write_text('{"archive_path":"' + str(archive).replace('\\', '/') + '","archive_checksum_sha256":"' + checksum + '","files":["f1"]}', encoding='utf-8')
        validator = ManifestValidator()
        assert validator.validate(str(manifest)) is True

    def test_validate_file_not_found(self):
        validator = ManifestValidator()
        assert validator.validate("/nonexistent/manifest.json") is False

    def test_validate_invalid_json(self, tmp_path):
        manifest = tmp_path / "manifest.json"
        manifest.write_bytes(b"invalid json")
        validator = ManifestValidator()
        assert validator.validate(str(manifest)) is False

    def test_validate_checksum_mismatch(self, tmp_path):
        archive = tmp_path / "archive.zip"
        archive.write_bytes(b"data")
        manifest = tmp_path / "manifest.json"
        manifest.write_text('{"archive_path":"' + str(archive).replace('\\', '/') + '","archive_checksum_sha256":"' + '0' * 64 + '","files":["f1"]}', encoding='utf-8')
        validator = ManifestValidator()
        assert validator.validate(str(manifest), expected_checksum="abc") is False


class TestRestoreTester:
    def test_dry_run_success(self):
        tester = RestoreTester()
        job = MagicMock()
        job.id = str(uuid4())
        assert tester.dry_run(job) is True