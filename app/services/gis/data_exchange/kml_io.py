# app/services/gis/data_exchange/kml_io.py
"""
KML (Keyhole Markup Language) Import / Export Serializers
Phase 3 — Section 4.3
Land Intelligence System
"""

import html
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple

from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.geometry.collection import GeometryCollection

from app.services.gis.data_exchange.base import GisDataset, WGS84_CRS

_KML_NS = "http://www.opengis.net/kml/2.2"
_GEOMETRY_TAGS = ("Point", "LineString", "Polygon", "MultiGeometry")


def _local(tag: str) -> str:
    """Return the XML tag local name regardless of namespace."""
    return tag.rsplit("}", 1)[-1]


def _find_child(element: ET.Element, name: str) -> Optional[ET.Element]:
    """Find the first direct child with the given local tag name."""
    for child in element:
        if _local(child.tag) == name:
            return child
    return None


def _find_children(element: ET.Element, name: str) -> List[ET.Element]:
    """Find all direct children with the given local tag name."""
    return [child for child in element if _local(child.tag) == name]


def _parse_coordinates(text: Optional[str]) -> List[Tuple[float, float]]:
    """
    Parse a KML <coordinates> value into (lon, lat) tuples.

    Tokens are "lon,lat[,alt]" separated by whitespace. Elevation is ignored.
    """
    coordinates: List[Tuple[float, float]] = []
    if not text:
        return coordinates
    for token in str(text).split():
        parts = token.split(",")
        if len(parts) >= 2:
            try:
                coordinates.append((float(parts[0]), float(parts[1])))
            except ValueError:
                continue
    return coordinates
def _ring_from_boundary(boundary: ET.Element) -> Optional[List[Tuple[float, float]]]:
    """Extract a closed coordinate ring from an outer/innerBoundaryIs element."""
    linear_ring = _find_child(boundary, "LinearRing")
    if linear_ring is None:
        return None
    coordinates_el = _find_child(linear_ring, "coordinates")
    if coordinates_el is None:
        return None
    return _parse_coordinates(coordinates_el.text)


def _parse_kml_polygon(element: ET.Element) -> Optional[Polygon]:
    """Parse a KML <Polygon> element into a Shapely Polygon."""
    exterior: Optional[List[Tuple[float, float]]] = None
    interiors: List[List[Tuple[float, float]]] = []

    for child in element:
        child_name = _local(child.tag)
        if child_name == "outerBoundaryIs":
            ring = _ring_from_boundary(child)
            if ring:
                exterior = ring
        elif child_name == "innerBoundaryIs":
            ring = _ring_from_boundary(child)
            if ring:
                interiors.append(ring)

    if exterior is None:
        # Fallback: some producers omit the boundary wrapper tags
        linear_ring = element.find("{*}LinearRing") or element.find("LinearRing")
        if linear_ring is not None:
            coordinates_el = _find_child(linear_ring, "coordinates")
            if coordinates_el is not None:
                exterior = _parse_coordinates(coordinates_el.text)

    if not exterior:
        return None

    polygon = Polygon(exterior, interiors)
    if not polygon.is_valid:
        polygon = polygon.buffer(0)
    if polygon.geom_type != "Polygon":
        return None
    return polygon


def _parse_geometry_element(element: ET.Element) -> Optional[BaseGeometry]:
    """Recursively parse a KML geometry element into a Shapely geometry."""
    name = _local(element.tag)

    if name == "Point":
        coordinates_el = _find_child(element, "coordinates")
        coordinates = _parse_coordinates(coordinates_el.text) if coordinates_el is not None else []
        return Point(coordinates[0]) if coordinates else None

    if name == "LineString":
        coordinates_el = _find_child(element, "coordinates")
        coordinates = _parse_coordinates(coordinates_el.text) if coordinates_el is not None else []
        return LineString(coordinates) if len(coordinates) >= 2 else None

    if name == "Polygon":
        return _parse_kml_polygon(element)

    if name == "MultiGeometry":
        geoms: List[BaseGeometry] = []
        for child in element:
            if _local(child.tag) in _GEOMETRY_TAGS:
                child_geom = _parse_geometry_element(child)
                if child_geom is not None:
                    geoms.append(child_geom)
        if not geoms:
            return None
        if len(geoms) == 1:
            return geoms[0]
        return GeometryCollection(geoms)

    return None
def _kml_properties(placemark: ET.Element) -> Dict[str, Any]:
    """
    Extract attributes from a KML Placemark.

    Reads <name>, <description> and any <Data>/<SimpleData> entries from
    the <ExtendedData> block into a flat dictionary.
    """
    properties: Dict[str, Any] = {}

    name_el = _find_child(placemark, "name")
    if name_el is not None and name_el.text:
        properties["name"] = name_el.text.strip()

    description_el = _find_child(placemark, "description")
    if description_el is not None and description_el.text:
        properties["description"] = description_el.text.strip()

    extended_data = _find_child(placemark, "ExtendedData")
    if extended_data is not None:
        for data_el in _find_children(extended_data, "Data"):
            key = data_el.get("name")
            value_el = _find_child(data_el, "value")
            if key and value_el is not None:
                properties[key] = (value_el.text or "").strip()
        for schema_data in _find_children(extended_data, "SchemaData"):
            for simple_data in schema_data.iter():
                if _local(simple_data.tag) == "SimpleData":
                    key = simple_data.get("name")
                    if key:
                        properties[key] = (simple_data.text or "").strip()

    return properties


def kml_to_dataset(raw: bytes, source_crs: str = WGS84_CRS) -> GisDataset:
    """
    Parse KML (bytes) into a GisDataset.

    Args:
        raw: UTF-8 encoded KML document
        source_crs: CRS of the document (KML is almost always WGS84)

    Returns:
        GisDataset with one GisFeature per <Placemark>
    """
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError(f"Invalid KML document: {exc}")

    placemarks: List[ET.Element] = []
    for element in root.iter():
        if _local(element.tag) == "Placemark":
            placemarks.append(element)

    dataset = GisDataset(crs=source_crs)

    for placemark in placemarks:
        geometry: Optional[BaseGeometry] = None
        for element in placemark.iter():
            if _local(element.tag) in _GEOMETRY_TAGS:
                candidate = _parse_geometry_element(element)
                if candidate is not None:
                    geometry = candidate
                    break
        properties = _kml_properties(placemark)
        dataset.add_feature(geometry, properties)

    return dataset


def _fmt(value: Any) -> str:
    """Format an attribute value for XML serialization."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.10g}"
    if isinstance(value, int):
        return str(value)
    return str(value)


def _xml_escape(value: str) -> str:
    return html.escape(value, quote=True)


def _coordinates_kml(coordinates: List[Tuple[float, float]]) -> str:
    """Serialize coordinates as KML 'lon,lat lon,lat ...'."""
    return " ".join(f"{x:0.12g},{y:0.12g}" for x, y in coordinates)


def _polygon_to_kml(polygon: Polygon) -> str:
    """Serialize a Shapely Polygon into KML <Polygon> markup."""
    parts = ["<Polygon>"]
    parts.append("<outerBoundaryIs><LinearRing><coordinates>")
    parts.append(_coordinates_kml(list(polygon.exterior.coords)))
    parts.append("</coordinates></LinearRing></outerBoundaryIs>")
    for interior in polygon.interiors:
        parts.append("<innerBoundaryIs><LinearRing><coordinates>")
        parts.append(_coordinates_kml(list(interior.coords)))
        parts.append("</coordinates></LinearRing></innerBoundaryIs>")
    parts.append("</Polygon>")
    return "".join(parts)


def _geometry_to_kml(geometry: Optional[BaseGeometry]) -> str:
    """Serialize a Shapely geometry into KML markup."""
    if geometry is None or geometry.is_empty:
        return "<Point><coordinates>0,0</coordinates></Point>"

    geom_type = geometry.geom_type

    if geom_type == "Point":
        return (
            "<Point><coordinates>"
            f"{geometry.x:0.12g},{geometry.y:0.12g}"
            "</coordinates></Point>"
        )
    if geom_type == "MultiPoint":
        children = "".join(
            f"<Point><coordinates>{p.x:0.12g},{p.y:0.12g}</coordinates></Point>"
            for p in geometry.geoms
        )
        return f"<MultiGeometry>{children}</MultiGeometry>"
    if geom_type == "LineString":
        return (
            "<LineString><coordinates>"
            f"{_coordinates_kml(list(geometry.coords))}"
            "</coordinates></LineString>"
        )
    if geom_type == "MultiLineString":
        children = "".join(
            f"<LineString><coordinates>{_coordinates_kml(list(ls.coords))}</coordinates></LineString>"
            for ls in geometry.geoms
        )
        return f"<MultiGeometry>{children}</MultiGeometry>"
    if geom_type == "Polygon":
        return _polygon_to_kml(geometry)
    if geom_type == "MultiPolygon":
        children = "".join(_polygon_to_kml(p) for p in geometry.geoms)
        return f"<MultiGeometry>{children}</MultiGeometry>"

    # Fallback for exotic geometries: emit the centroid as a point
    centroid = geometry.centroid
    return f"<Point><coordinates>{centroid.x:0.12g},{centroid.y:0.12g}</coordinates></Point>"


def dataset_to_kml(dataset: GisDataset) -> str:
    """
    Serialize a GisDataset into a KML 2.2 document string.

    Each feature becomes a <Placemark> with geometry and an
    <ExtendedData> block carrying its attribute dictionary.
    """
    document_props = dataset.properties or {}
    doc_name = document_props.get("name") or "Land Intelligence Export"
    doc_description = document_props.get("description") or "RLMUA data exchange export"

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<kml xmlns="{_KML_NS}">',
        "<Document>",
        f"<name>{_xml_escape(str(doc_name))}</name>",
        f"<description>{_xml_escape(str(doc_description))}</description>",
    ]

    for index, feature in enumerate(dataset.features):
        feature_id = feature.feature_id or f"feature_{index + 1}"
        lines.append("<Placemark>")
        lines.append(f"<name>{_xml_escape(str(feature_id))}</name>")

        properties = feature.properties or {}
        if properties:
            lines.append("<ExtendedData>")
            for key, value in properties.items():
                lines.append(f'<Data name="{_xml_escape(str(key))}">')
                lines.append(f"<value>{_xml_escape(_fmt(value))}</value>")
                lines.append("</Data>")
            lines.append("</ExtendedData>")

        lines.append(_geometry_to_kml(feature.geometry))
        lines.append("</Placemark>")

    lines.append("</Document>")
    lines.append("</kml>")
    return "\n".join(lines)


def dataset_to_kml_bytes(dataset: GisDataset) -> bytes:
    """Serialize a dataset into UTF-8 KML bytes."""
    return dataset_to_kml(dataset).encode("utf-8")