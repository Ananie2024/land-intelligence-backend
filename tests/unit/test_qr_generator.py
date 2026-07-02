"""Unit tests for QRGenerator."""
import pytest
from pathlib import Path
from uuid import uuid4

from app.services.qr.qr_generator import QRGenerator


class TestQRGenerator:
    @pytest.fixture
    def generator(self, tmp_path):
        return QRGenerator(storage_path=str(tmp_path))

    def test_generate_creates_qr_and_returns_code_and_path(self, generator):
        data = {"id": str(uuid4())}
        code, file_path = generator.generate(data, prefix="QR")
        assert code.startswith("QR_")
        assert len(code) > 10
        assert Path(file_path).exists()
        assert Path(file_path).suffix == ".png"

    def test_delete_image_removes_file(self, generator, tmp_path):
        file_path = tmp_path / "qr_123.png"
        file_path.write_bytes(b"fake")
        assert generator.delete_image(str(file_path)) is True
        assert not file_path.exists()

    def test_delete_image_missing_returns_false(self, generator):
        assert generator.delete_image("/nonexistent/path/qr.png") is False
