# tests/unit/test_utils.py
"""Unit tests for utility modules."""
import hashlib
import zipfile
import pytest
from datetime import date, datetime
from io import BytesIO


class TestDateHelpers:
    """Tests for date_helpers utility."""

    def test_parse_date_string_iso_format(self):
        """Test parsing ISO date string."""
        from app.utils.date_helpers import parse_date_string
        
        result = parse_date_string("2024-01-15")
        assert result == date(2024, 1, 15)

    def test_parse_date_string_datetime_format(self):
        """Test parsing datetime string."""
        from app.utils.date_helpers import parse_date_string
        
        result = parse_date_string("2024-01-15T10:30:00")
        assert result == date(2024, 1, 15)

    def test_parse_date_string_none(self):
        """Test parsing None returns None."""
        from app.utils.date_helpers import parse_date_string
        
        result = parse_date_string(None)
        assert result is None

    def test_parse_date_string_empty(self):
        """Test parsing empty string returns None."""
        from app.utils.date_helpers import parse_date_string
        
        result = parse_date_string("")
        assert result is None

    def test_format_date_to_iso(self):
        """Test formatting date to ISO string."""
        from app.utils.date_helpers import format_date_to_iso
        
        result = format_date_to_iso(date(2024, 1, 15))
        assert result == "2024-01-15"

    def test_format_datetime_to_iso(self):
        """Test formatting datetime to ISO string."""
        from app.utils.date_helpers import format_date_to_iso
        
        result = format_date_to_iso(datetime(2024, 1, 15, 10, 30, 0))
        assert result == "2024-01-15"

    def test_format_date_to_iso_none(self):
        """Test formatting None returns None."""
        from app.utils.date_helpers import format_date_to_iso
        
        result = format_date_to_iso(None)
        assert result is None

    def test_get_current_year(self):
        """Test getting current year."""
        from app.utils.date_helpers import get_current_year
        
        result = get_current_year()
        assert result > 2020
        assert result < 2100

    def test_calculate_years_difference(self):
        """Test calculating years difference."""
        from app.utils.date_helpers import calculate_years_difference
        
        result = calculate_years_difference(date(2020, 1, 1), date(2024, 1, 1))
        assert result == 4


class TestChecksumCalculator:
    """Tests for checksum_calculator utility."""

    def test_calculate_sha256_with_valid_file(self, tmp_path):
        """Test SHA-256 calculation with a valid file."""
        from app.utils.checksum_calculator import calculate_sha256
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_content = b"Hello, World!"
        test_file.write_bytes(test_content)
        
        expected = hashlib.sha256(test_content).hexdigest()
        result = calculate_sha256(str(test_file))
        assert result == expected

    def test_calculate_sha256_with_large_file(self, tmp_path):
        """Test SHA-256 calculation with a larger file."""
        from app.utils.checksum_calculator import calculate_sha256
        
        # Create a larger test file
        test_file = tmp_path / "large_test.bin"
        test_content = b"x" * (2 * 1024 * 1024)  # 2MB file
        test_file.write_bytes(test_content)
        
        expected = hashlib.sha256(test_content).hexdigest()
        result = calculate_sha256(test_file)
        assert result == expected

    def test_calculate_sha256_from_stream_seekable(self):
        """Test SHA-256 calculation from a seekable stream."""
        from app.utils.checksum_calculator import calculate_sha256_from_stream
        
        test_content = b"Stream content for testing"
        stream = BytesIO(test_content)
        
        # Seek to middle to test that position is restored
        stream.seek(5)
        
        expected = hashlib.sha256(test_content).hexdigest()
        result = calculate_sha256_from_stream(stream)
        
        assert result == expected
        assert stream.tell() == 5  # Position should be restored


class TestFileValidators:
    """Tests for file_validators utility."""

    def test_validate_file_size_within_limit(self):
        """Test file size validation within limits."""
        from app.utils.file_validators import validate_file_size
        
        result = validate_file_size(500000, 1.0)  # 500KB, 1MB limit
        assert result is True

    def test_validate_file_size_over_limit(self):
        """Test file size validation over limit."""
        from app.utils.file_validators import validate_file_size
        
        result = validate_file_size(2 * 1024 * 1024, 1.0)  # 2MB, 1MB limit
        assert result is False

    def test_validate_mime_type_allowed(self):
        """Test MIME type validation for allowed type."""
        from app.utils.file_validators import validate_mime_type
        
        result = validate_mime_type("application/pdf", [".pdf", "application/pdf"])
        assert result is True

    def test_validate_mime_type_not_allowed(self):
        """Test MIME type validation for disallowed type."""
        from app.utils.file_validators import validate_mime_type
        
        result = validate_mime_type("text/plain", ["application/pdf", "application/doc"])
        assert result is False

    def test_is_allowed_extension_valid(self):
        """Test file extension validation for allowed extension."""
        from app.utils.file_validators import is_allowed_extension
        
        result = is_allowed_extension("test.pdf", [".pdf", ".doc"])
        assert result is True

    def test_is_allowed_extension_invalid(self):
        """Test file extension validation for disallowed extension."""
        from app.utils.file_validators import is_allowed_extension
        
        result = is_allowed_extension("test.txt", [".pdf", ".doc"])
        assert result is False

    def test_is_allowed_extension_no_dot(self):
        """Test file extension validation without leading dot."""
        from app.utils.file_validators import is_allowed_extension
        
        result = is_allowed_extension("test.pdf", ["pdf", "doc"])
        assert result is True


class TestGeometryHelpers:
    """Tests for geometry_helpers utility."""

    def test_wkb_hex_to_wkt(self):
        """Test WKB hex to WKT conversion."""
        from app.utils.geometry_helpers import wkb_hex_to_wkt, wkt_to_wkb_hex
        
        # Convert WKT to WKB hex and back - Shapely may normalize formatting
        original_wkt = "POINT(1 2)"
        wkb = wkt_to_wkb_hex(original_wkt)
        result = wkb_hex_to_wkt(wkb)
        # Compare by parsing both - Shapely normalizes to "POINT (1 2)"
        assert "POINT" in result
        assert "1" in result and "2" in result

    def test_wkt_to_wkb_hex(self):
        """Test WKT to WKB hex conversion."""
        from app.utils.geometry_helpers import wkt_to_wkb_hex
        
        wkt = "POINT(1 2)"
        result = wkt_to_wkb_hex(wkt)
        assert result is not None
        assert len(result) > 0

    def test_wkb_hex_to_wkt_empty(self):
        """Test WKB hex to WKT with empty input."""
        from app.utils.geometry_helpers import wkb_hex_to_wkt
        
        result = wkb_hex_to_wkt("")
        assert result == ""

    def test_geojson_to_geometry(self):
        """Test GeoJSON to Shapely geometry conversion."""
        from app.utils.geometry_helpers import geojson_to_geometry
        
        geojson = {"type": "Point", "coordinates": [1, 2]}
        result = geojson_to_geometry(geojson)
        assert result is not None
        assert result.wkt == "POINT (1 2)"

    def test_geometry_to_geojson(self):
        """Test Shapely geometry to GeoJSON conversion."""
        from app.utils.geometry_helpers import geometry_to_geojson
        from shapely.geometry import Point
        
        geom = Point(1, 2)
        result = geometry_to_geojson(geom)
        assert result["type"] == "Point"

    def test_create_bbox_polygon(self):
        """Test bounding box polygon creation."""
        from app.utils.geometry_helpers import create_bbox_polygon
        
        result = create_bbox_polygon(0, 0, 10, 10)
        assert result is not None
        assert result.bounds == (0, 0, 10, 10)

    def test_ensure_wkb_hex_none(self):
        """Test ensure_wkb_hex with None input."""
        from app.utils.geometry_helpers import ensure_wkb_hex
        
        result = ensure_wkb_hex(None)
        assert result is None

    def test_ensure_wkb_hex_from_geometry(self):
        """Test ensure_wkb_hex from Shapely geometry."""
        from app.utils.geometry_helpers import ensure_wkb_hex
        from shapely.geometry import Point
        
        geom = Point(1, 2)
        result = ensure_wkb_hex(geom)
        assert result is not None


class TestPathResolver:
    """Tests for path_resolver utility."""

    def test_resolve_safe_path_relative(self, tmp_path):
        """Test safe path resolution with relative path."""
        from app.utils.path_resolver import resolve_safe_path
        
        base_dir = tmp_path / "storage"
        base_dir.mkdir()
        
        result = resolve_safe_path(base_dir, "file.txt")
        assert result is not None
        assert result.name == "file.txt"

    def test_resolve_safe_path_absolute_within_base(self, tmp_path):
        """Test safe path resolution with absolute path within base."""
        from app.utils.path_resolver import resolve_safe_path
        
        base_dir = tmp_path / "storage"
        base_dir.mkdir()
        
        result = resolve_safe_path(base_dir, base_dir / "subdir" / "file.txt")
        assert result is not None

    def test_resolve_safe_path_outside_base_raises(self, tmp_path):
        """Test safe path resolution raises error for path outside base."""
        from app.utils.path_resolver import resolve_safe_path
        
        base_dir = tmp_path / "storage"
        base_dir.mkdir()
        
        with pytest.raises(ValueError, match="Path security violation"):
            resolve_safe_path(base_dir, "../outside.txt")


class TestCompressionHelper:
    """Tests for compression_helper utility."""

    def test_decompress_archive_success(self, tmp_path):
        """Test successful archive decompression."""
        from app.utils.compression_helper import decompress_archive
        
        # Create a test zip file
        zip_path = tmp_path / "test.zip"
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(test_file, arcname="test.txt")
        
        # Decompress
        extract_dir = tmp_path / "extracted"
        decompress_archive(zip_path, extract_dir)
        
        # Verify output
        extracted_file = extract_dir / "test.txt"
        assert extracted_file.exists()
        assert extracted_file.read_text() == "Hello, World!"

    def test_decompress_archive_not_exists_raises(self, tmp_path):
        """Test decompression raises error for missing zip file."""
        from app.utils.compression_helper import decompress_archive
        
        with pytest.raises(FileNotFoundError):
            decompress_archive(tmp_path / "nonexistent.zip", tmp_path / "out")

    def test_decompress_archive_bad_zip_raises(self, tmp_path):
        """Test decompression raises error for invalid zip file."""
        from app.utils.compression_helper import decompress_archive
        
        # Create a non-zip file
        bad_zip = tmp_path / "bad.zip"
        bad_zip.write_text("Not a zip file")
        
        with pytest.raises(zipfile.BadZipFile):
            decompress_archive(bad_zip, tmp_path / "out")

    def test_compress_file_success(self, tmp_path):
        """Test successful file compression."""
        from app.utils.compression_helper import compress_file
        
        # Create a test file
        source_file = tmp_path / "source.txt"
        source_file.write_text("Compress me!")
        
        zip_path = tmp_path / "output.zip"
        compress_file(source_file, zip_path)
        
        assert zip_path.exists()
        with zipfile.ZipFile(zip_path, "r") as zf:
            assert "source.txt" in zf.namelist()

    def test_compress_file_not_exists_raises(self, tmp_path):
        """Test compression raises error for missing source file."""
        from app.utils.compression_helper import compress_file
        
        with pytest.raises(FileNotFoundError):
            compress_file(tmp_path / "missing.txt", tmp_path / "out.zip")

    def test_compress_directory_success(self, tmp_path):
        """Test successful directory compression."""
        from app.utils.compression_helper import compress_directory
        
        # Create test directory structure
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("File 1")
        (source_dir / "file2.txt").write_text("File 2")
        
        zip_path = tmp_path / "output.zip"
        compress_directory(source_dir, zip_path)
        
        assert zip_path.exists()
        with zipfile.ZipFile(zip_path, "r") as zf:
            assert len(zf.namelist()) == 2

    def test_compress_directory_not_exists_raises(self, tmp_path):
        """Test directory compression raises error for missing directory."""
        from app.utils.compression_helper import compress_directory
        
        with pytest.raises(FileNotFoundError):
            compress_directory(tmp_path / "missing", tmp_path / "out.zip")