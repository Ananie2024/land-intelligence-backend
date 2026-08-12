# app/services/gis/data_exchange/shapefile_io.py
"""
Pure-Python Shapefile (ESRI) Import / Export Serializers
Phase 3 — Section 4.3
Land Intelligence System

Implements the ESRI Shapefile format plus the dBASE III (.dbf) attribute
table without any GDAL/Fiona dependency. Supported geometry types: Point,
MultiPoint, PolyLine, Polygon and their Z/M variants (Z/M ordinates are
parsed but not preserved).

Exposed API:
    read_shapefile(shp_bytes[, dbf_bytes]) -> (features, crs)
    write_shapefile(features) -> (shp_bytes, shx_bytes, dbf_bytes)
"""

import struct
from typing import Any, Dict, List, Optional, Tuple

from shapely.geometry import LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon
from shapely.geometry.base import BaseGeometry

from app.services.gis.data_exchange.base import GisFeature, WGS84_CRS

# Shape type codes (ESRI Shapefile specification)
SHAPETYPE_NULL = 0
SHAPETYPE_POINT = 1
SHAPETYPE_POLYLINE = 3
SHAPETYPE_POLYGON = 5
SHAPETYPE_MULTIPOINT = 8
SHAPETYPE_POINTZ = 11
SHAPETYPE_POLYLINEZ = 13
SHAPETYPE_POLYGONZ = 15
SHAPETYPE_MULTIPOINTZ = 18
SHAPETYPE_POINTM = 21
SHAPETYPE_POLYLINEM = 23
SHAPETYPE_POLYGONM = 25
SHAPETYPE_MULTIPOINTM = 28

_POINT_TYPES = {SHAPETYPE_POINT, SHAPETYPE_POINTZ, SHAPETYPE_POINTM}
_MULTIPOINT_TYPES = {SHAPETYPE_MULTIPOINT, SHAPETYPE_MULTIPOINTZ, SHAPETYPE_MULTIPOINTM}
_POLYLINE_TYPES = {SHAPETYPE_POLYLINE, SHAPETYPE_POLYLINEZ, SHAPETYPE_POLYLINEM}
_POLYGON_TYPES = {SHAPETYPE_POLYGON, SHAPETYPE_POLYGONZ, SHAPETYPE_POLYGONM}

_FILE_CODE = 9994
_VERSION = 1000


def _unpack_points(data: bytes, offset: int, count: int) -> List[Tuple[float, float]]:
    """Unpack a contiguous block of (X, Y) coordinate pairs."""
    points: List[Tuple[float, float]] = []
    for i in range(count):
        start = offset + i * 16
        x, y = struct.unpack("<2d", data[start:start + 16])
        points.append((x, y))
    return points


def _parse_record(content: bytes) -> Dict[str, Any]:
    """Parse a single feature record body into a normalized dictionary."""
    if len(content) < 4:
        return {"shape_type": SHAPETYPE_NULL, "points": [], "parts": []}

    shape_type = struct.unpack("<i", content[0:4])[0]

    if shape_type in _POINT_TYPES:
        x, y = struct.unpack("<2d", content[4:20])
        return {"shape_type": shape_type, "points": [(x, y)], "parts": []}

    if shape_type in _MULTIPOINT_TYPES:
        num_points = struct.unpack("<i", content[36:40])[0]
        points = _unpack_points(content, 40, num_points)
        return {"shape_type": shape_type, "points": points, "parts": []}

    if shape_type in _POLYLINE_TYPES or shape_type in _POLYGON_TYPES:
        num_parts = struct.unpack("<i", content[36:40])[0]
        num_points = struct.unpack("<i", content[40:44])[0]
        parts_offset = 44
        parts = list(struct.unpack(f"<{num_parts}i", content[parts_offset:parts_offset + 4 * num_parts]))
        points = _unpack_points(content, parts_offset + 4 * num_parts, num_points)
        return {"shape_type": shape_type, "points": points, "parts": parts}

    return {"shape_type": shape_type, "points": [], "parts": []}


def _shape_type_label(shape_type: int) -> str:
    for label, types in (
        ("Point", _POINT_TYPES),
        ("MultiPoint", _MULTIPOINT_TYPES),
        ("PolyLine", _POLYLINE_TYPES),
        ("Polygon", _POLYGON_TYPES),
    ):
        if shape_type in types:
            return label
    return "Null"
def _parse_shp(data: bytes) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Parse the .shp main file header and all feature records."""
    if len(data) < 100:
        raise ValueError("Invalid Shapefile (.shp): file is smaller than the 100-byte header")

    file_code = struct.unpack(">i", data[0:4])[0]
    if file_code != _FILE_CODE:
        raise ValueError("Invalid Shapefile (.shp): bad file code in header")

    shape_type = struct.unpack("<i", data[32:36])[0]
    header = {"shape_type": shape_type, "shape_type_label": _shape_type_label(shape_type)}

    records: List[Dict[str, Any]] = []
    position = 100
    while position < len(data):
        if position + 8 > len(data):
            break
        content_length_words = struct.unpack(">i", data[position + 4:position + 8])[0]
        content_start = position + 8
        content_end = content_start + content_length_words * 2
        content = data[content_start:content_end]
        records.append(_parse_record(content))
        position = content_end

    return header, records


def _parts_to_rings(record: Dict[str, Any]) -> List[List[Tuple[float, float]]]:
    """Split a record's point list into rings using the parts index array."""
    parts = record.get("parts") or []
    points = record.get("points") or []
    rings: List[List[Tuple[float, float]]] = []
    for i, start in enumerate(parts):
        end = parts[i + 1] if i + 1 < len(parts) else len(points)
        rings.append(points[start:end])
    if not parts and points:
        rings.append(points)
    return rings


def _signed_area(ring: List[Tuple[float, float]]) -> float:
    """Compute the signed area of a ring (positive = counter-clockwise)."""
    if len(ring) < 3:
        return 0.0
    total = 0.0
    for i in range(len(ring)):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % len(ring)]
        total += x1 * y2 - x2 * y1
    return total / 2.0


def _ring_contains(outer_polygon: Polygon, inner_ring: List[Tuple[float, float]]) -> bool:
    """Return True when a polygon strictly contains another ring."""
    inner_polygon = Polygon(inner_ring)
    if outer_polygon.equals(inner_polygon):
        return False
    try:
        return bool(outer_polygon.covers(inner_polygon))
    except Exception:
        return False


def _build_polygons(record: Dict[str, Any]) -> List[Polygon]:
    """
    Build Shapely polygons from a shapefile polygon record.

    Outer rings and holes are resolved through spatial containment rather than
    ring orientation, so files that do not strictly follow the ESRI clockwise/
    counter-clockwise convention are still parsed correctly. A ring not
    contained by any other ring is an exterior; a ring contained by another is
    a hole of the smallest containing exterior.
    """
    rings = [ring for ring in _parts_to_rings(record) if len(ring) >= 3]
    if not rings:
        return []

    ring_polygons = [Polygon(ring) for ring in rings]
    contained_by: List[List[int]] = [[] for _ in rings]

    for index in range(len(rings)):
        for other in range(len(rings)):
            if index == other:
                continue
            if _ring_contains(ring_polygons[other], rings[index]):
                contained_by[index].append(other)

    exteriors = [i for i in range(len(rings)) if not contained_by[i]]
    assigned_holes: set = set()
    polygons: List[Polygon] = []

    for exterior_index in exteriors:
        holes: List[List[Tuple[float, float]]] = []
        for hole_index in range(len(rings)):
            if hole_index == exterior_index or hole_index in assigned_holes:
                continue
            if _ring_contains(ring_polygons[exterior_index], rings[hole_index]):
                holes.append(rings[hole_index])
                assigned_holes.add(hole_index)

        polygon = Polygon(rings[exterior_index], holes)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        if polygon.geom_type == "Polygon":
            polygons.append(polygon)
        elif polygon.geom_type == "MultiPolygon":
            polygons.extend(list(polygon.geoms))

    return polygons


def _shape_to_geometry(record: Dict[str, Any]) -> Optional[BaseGeometry]:
    """Convert a parsed shapefile record into a Shapely geometry."""
    shape_type = record["shape_type"]

    if shape_type in _POINT_TYPES:
        points = record.get("points") or []
        return Point(points[0]) if points else None

    if shape_type in _MULTIPOINT_TYPES:
        points = record.get("points") or []
        return MultiPoint(points) if points else None

    if shape_type in _POLYLINE_TYPES:
        rings = _parts_to_rings(record)
        lines = [LineString(ring) for ring in rings if len(ring) >= 2]
        if not lines:
            return None
        if len(lines) == 1:
            return lines[0]
        return MultiLineString(lines)

    if shape_type in _POLYGON_TYPES:
        polygons = _build_polygons(record)
        if not polygons:
            return None
        if len(polygons) == 1:
            return polygons[0]
        return MultiPolygon(polygons)

    return None
def _decode_dbf_value(raw: bytes, field_type: str) -> Any:
    """Decode a raw DBF field value according to its dBASE type."""
    if field_type == "C":
        return raw.rstrip(b" \x00").decode("latin-1")
    if field_type in ("N", "F"):
        text = raw.rstrip(b" \x00").decode("latin-1").strip()
        if not text:
            return None
        try:
            return float(text) if ("." in text or "e" in text.lower()) else int(text)
        except ValueError:
            return None
    if field_type == "L":
        flag = raw.strip().decode("latin-1").upper()[:1]
        if flag in ("T", "Y"):
            return True
        if flag in ("F", "N"):
            return False
        return None
    if field_type == "D":
        return raw.strip().decode("latin-1") or None
    return raw.rstrip(b" \x00").decode("latin-1")


def _read_dbf(data: Optional[bytes]) -> List[Dict[str, Any]]:
    """Parse a dBASE III (.dbf) table into a list of attribute dictionaries."""
    if not data or len(data) < 32:
        return []

    num_records = struct.unpack("<I", data[4:8])[0]
    header_length = struct.unpack("<H", data[8:10])[0]
    record_length = struct.unpack("<H", data[10:12])[0]
    if header_length < 33 or record_length < 1:
        return []

    fields: List[Tuple[str, str, int]] = []
    position = 32
    while position + 32 <= header_length - 1:
        raw_name = data[position:position + 11].split(b"\x00")[0]
        name = raw_name.decode("latin-1")
        field_type = chr(data[position + 11])
        field_length = data[position + 16]
        fields.append((name, field_type, field_length))
        position += 32

    records: List[Dict[str, Any]] = []
    position = header_length
    for _ in range(num_records):
        if position + record_length > len(data):
            break
        raw_record = data[position:position + record_length]
        record: Dict[str, Any] = {}
        inner = 1  # skip the deletion marker byte
        for name, field_type, field_length in fields:
            record[name] = _decode_dbf_value(raw_record[inner:inner + field_length], field_type)
            inner += field_length
        records.append(record)
        position += record_length

    return records


def read_shapefile(shp_bytes: bytes, dbf_bytes: Optional[bytes] = None) -> Tuple[List[GisFeature], str]:
    """
    Read a Shapefile into a list of GisFeature objects.

    Args:
        shp_bytes: Raw bytes of the .shp main file
        dbf_bytes: Optional raw bytes of the .dbf attribute table

    Returns:
        Tuple of (features, crs_hint). The CRS hint is parsed from a companion
        .prj file when provided by the caller via `source_crs` in the service;
        otherwise WGS84 is assumed.
    """
    header, records = _parse_shp(shp_bytes)
    attributes = _read_dbf(dbf_bytes) if dbf_bytes else None

    features: List[GisFeature] = []
    for index, record in enumerate(records):
        geometry = _shape_to_geometry(record)
        properties = attributes[index] if attributes and index < len(attributes) else {}
        features.append(GisFeature(geometry=geometry, properties=properties, feature_id=index))

    return features, header.get("crs") or WGS84_CRS
def _bbox(points: List[Tuple[float, float]]) -> bytes:
    """Pack a bounding box (Xmin, Ymin, Xmax, Ymax) from points."""
    if not points:
        return struct.pack("<4d", 0.0, 0.0, 0.0, 0.0)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return struct.pack("<4d", min(xs), min(ys), max(xs), max(ys))


def _parts_record(shape_type: int, parts: List[List[Tuple[float, float]]]) -> Dict[str, Any]:
    """Build a PolyLine/Polygon record body and bounding box from rings."""
    points: List[Tuple[float, float]] = []
    part_indices: List[int] = []
    for ring in parts:
        part_indices.append(len(points))
        points.extend(ring)

    content = struct.pack("<i", shape_type)
    content += _bbox(points)
    content += struct.pack("<2i", len(parts), len(points))
    content += struct.pack(f"<{len(part_indices)}i", *part_indices)
    for x, y in points:
        content += struct.pack("<2d", x, y)

    return {"shape_type": shape_type, "content": content, "bbox": _bbox(points)}


def _point_to_record(geometry: BaseGeometry) -> Dict[str, Any]:
    """Convert a Point/MultiPoint geometry into a Point shapefile record."""
    if geometry.geom_type == "MultiPoint":
        coords = list(geometry.geoms)
        coord = coords[0].coords[0] if coords else (0.0, 0.0)
    else:
        coord = geometry.coords[0]

    content = struct.pack("<i", SHAPETYPE_POINT)
    content += struct.pack("<2d", coord[0], coord[1])
    return {"shape_type": SHAPETYPE_POINT, "content": content, "bbox": _bbox([coord])}


def _line_to_record(geometry: BaseGeometry) -> Dict[str, Any]:
    """Convert a LineString/MultiLineString geometry into a PolyLine record."""
    if geometry.geom_type == "LineString":
        parts = [list(geometry.coords)]
    elif geometry.geom_type == "MultiLineString":
        parts = [list(ls.coords) for ls in geometry.geoms]
    elif geometry.geom_type in ("Polygon", "MultiPolygon"):
        parts = []
        for poly in ([geometry] if geometry.geom_type == "Polygon" else list(geometry.geoms)):
            parts.append(list(poly.exterior.coords))
            for interior in poly.interiors:
                parts.append(list(interior.coords))
    else:
        return {"shape_type": SHAPETYPE_NULL, "content": b"", "bbox": _bbox([])}

    return _parts_record(SHAPETYPE_POLYLINE, parts)


def _polygon_to_record(geometry: BaseGeometry) -> Dict[str, Any]:
    """Convert a Polygon/MultiPolygon geometry into a Polygon shapefile record."""
    parts: List[List[Tuple[float, float]]] = []
    if geometry.geom_type == "Polygon":
        parts.append(list(geometry.exterior.coords))
        for interior in geometry.interiors:
            parts.append(list(interior.coords))
    elif geometry.geom_type == "MultiPolygon":
        for poly in geometry.geoms:
            parts.append(list(poly.exterior.coords))
            for interior in poly.interiors:
                parts.append(list(interior.coords))
    else:
        return {"shape_type": SHAPETYPE_NULL, "content": b"", "bbox": _bbox([])}

    return _parts_record(SHAPETYPE_POLYGON, parts)


def _choose_shape_type(features: List[GisFeature]) -> int:
    """Pick the dominant geometry category for the output shapefile."""
    categories: set = set()
    for feature in features:
        geometry = feature.geometry
        if geometry is None or geometry.is_empty:
            continue
        geom_type = geometry.geom_type
        if geom_type in ("Point", "MultiPoint"):
            categories.add(1)
        elif geom_type in ("LineString", "MultiLineString"):
            categories.add(3)
        elif geom_type in ("Polygon", "MultiPolygon"):
            categories.add(5)
    if 5 in categories:
        return SHAPETYPE_POLYGON
    if 3 in categories:
        return SHAPETYPE_POLYLINE
    return SHAPETYPE_POINT


def _geometry_to_record(geometry: Optional[BaseGeometry], target_type: int) -> Dict[str, Any]:
    """Convert a Shapely geometry to a shapefile record for the target type."""
    if geometry is None or geometry.is_empty:
        return {"shape_type": SHAPETYPE_NULL, "content": b"", "bbox": _bbox([])}

    if target_type == SHAPETYPE_POLYGON:
        return _polygon_to_record(geometry)
    if target_type == SHAPETYPE_POLYLINE:
        return _line_to_record(geometry)
    return _point_to_record(geometry)
def _sanitize_field_name(name: str) -> str:
    """Restrict a property key to a valid dBASE field name (<=10 chars)."""
    sanitized = "".join(ch for ch in str(name) if ch.isalnum() or ch == "_")
    sanitized = sanitized[:10]
    if not sanitized or sanitized[0].isdigit():
        sanitized = "F" + sanitized
    return sanitized


def _infer_dbf_field(values: List[Any]) -> Tuple[str, int]:
    """Infer a dBASE field type and width for a column of values."""
    non_none = [v for v in values if v is not None]
    if not non_none:
        return "C", 50
    if all(isinstance(v, bool) for v in non_none):
        return "L", 1
    if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in non_none):
        max_width = max(len(str(v)) for v in non_none)
        return "N", max(18, max_width + 1)
    if all(isinstance(v, str) for v in non_none):
        max_width = max(len(v) for v in non_none)
        return "C", max(50, max_width + 1)
    max_width = max(len(str(v)) for v in non_none)
    return "C", max(50, max_width + 1)


def _encode_dbf_value(value: Any, field_type: str, width: int) -> bytes:
    """Encode a single value into a fixed-width DBF field."""
    if value is None:
        return b" " * width
    if field_type == "C":
        text = str(value)[:width]
        return text.encode("latin-1", "replace").ljust(width, b" ")
    if field_type == "N":
        text = str(value)[:width]
        return text.encode("latin-1").rjust(width, b" ")
    if field_type == "L":
        flag = b"T" if value is True else b"F" if value is False else b"?"
        return flag.ljust(width, b" ")
    if field_type == "D":
        return str(value)[:8].encode("latin-1").ljust(width, b" ")
    return str(value).encode("latin-1", "replace")[:width].ljust(width, b" ")


def _write_dbf(features: List[GisFeature]) -> bytes:
    """Serialize feature properties into a dBASE III (.dbf) table."""
    records = [dict(feature.properties or {}) for feature in features]
    if not records:
        records = [{}]

    # Column ordering: order of first appearance, RLMUA canonical fields first
    field_names: List[str] = []
    for record in records:
        for key in record:
            if key not in field_names:
                field_names.append(key)
    if not field_names:
        field_names = ["Row"]
        records = [{**record, "Row": index + 1} for index, record in enumerate(records)]

    fields: List[Tuple[str, str, int]] = []
    for name in field_names:
        values = [record.get(name) for record in records]
        field_type, width = _infer_dbf_field(values)
        fields.append((_sanitize_field_name(name), field_type, width))

    num_records = len(records)
    header_length = 32 + 32 * len(fields) + 1
    record_length = 1 + sum(width for _, _, width in fields)

    import datetime
    today = datetime.date.today()

    out = bytearray()
    out += b"\x03"  # dBASE III version
    out += struct.pack("<BBB", today.year - 1900, today.month, today.day)
    out += struct.pack("<I", num_records)
    out += struct.pack("<H", header_length)
    out += struct.pack("<H", record_length)
    out += b"\x00" * 20  # reserved bytes 12-31

    for name, field_type, width in fields:
        raw_name = name.encode("latin-1", "replace")[:11]
        out += raw_name + b"\x00" * (11 - len(raw_name))
        out += field_type.encode("latin-1")
        out += b"\x00" * 4
        out += struct.pack("<B", width)
        out += struct.pack("<B", 0)  # decimal count
        out += b"\x00" * 14

    out += b"\x0D"  # header terminator

    for record in records:
        out += b" "  # active record marker
        for name, field_type, width in fields:
            out += _encode_dbf_value(record.get(name), field_type, width)

    out += b"\x1A"  # end-of-file marker
    return bytes(out)
def _build_shp(records: List[Dict[str, Any]], shape_type: int) -> bytes:
    """Assemble the .shp main file bytes from prepared records."""
    body = bytearray()
    for index, record in enumerate(records):
        content = record["content"]
        content_length_words = len(content) // 2
        body += struct.pack(">2i", index + 1, content_length_words)
        body += content

    file_length_words = (100 + len(body)) // 2

    header = bytearray(100)
    header[0:4] = struct.pack(">i", _FILE_CODE)
    header[24:28] = struct.pack(">i", file_length_words)
    header[28:32] = struct.pack("<i", _VERSION)
    header[32:36] = struct.pack("<i", shape_type)

    bboxes = [record["bbox"] for record in records if record["shape_type"] != SHAPETYPE_NULL]
    if bboxes:
        header[36:68] = struct.pack(
            "<4d",
            min(b[0] for b in bboxes),
            min(b[1] for b in bboxes),
            max(b[2] for b in bboxes),
            max(b[3] for b in bboxes),
        )
    else:
        header[36:68] = struct.pack("<4d", 0.0, 0.0, 0.0, 0.0)

    return bytes(header) + bytes(body)


def _build_shx(records: List[Dict[str, Any]], shape_type: int) -> bytes:
    """Assemble the .shx index file bytes from prepared records."""
    body = bytearray()
    byte_offset = 100
    for record in records:
        content = record["content"]
        content_length_words = len(content) // 2
        body += struct.pack(">2i", byte_offset // 2, content_length_words)
        byte_offset += 8 + len(content)

    file_length_words = (100 + len(body)) // 2

    header = bytearray(100)
    header[0:4] = struct.pack(">i", _FILE_CODE)
    header[24:28] = struct.pack(">i", file_length_words)
    header[28:32] = struct.pack("<i", _VERSION)
    header[32:36] = struct.pack("<i", shape_type)

    bboxes = [record["bbox"] for record in records if record["shape_type"] != SHAPETYPE_NULL]
    if bboxes:
        header[36:68] = struct.pack(
            "<4d",
            min(b[0] for b in bboxes),
            min(b[1] for b in bboxes),
            max(b[2] for b in bboxes),
            max(b[3] for b in bboxes),
        )
    else:
        header[36:68] = struct.pack("<4d", 0.0, 0.0, 0.0, 0.0)

    return bytes(header) + bytes(body)


def write_shapefile(features: List[GisFeature]) -> Tuple[bytes, bytes, bytes]:
    """
    Serialize features into a complete ESRI Shapefile.

    Args:
        features: Features with WGS84 geometries and attribute dictionaries

    Returns:
        Tuple of (shp_bytes, shx_bytes, dbf_bytes)
    """
    shape_type = _choose_shape_type(features)
    records = [_geometry_to_record(feature.geometry, shape_type) for feature in features]
    shp = _build_shp(records, shape_type)
    shx = _build_shx(records, shape_type)
    dbf = _write_dbf(features)
    return shp, shx, dbf