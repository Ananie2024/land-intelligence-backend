# app/services/gis/data_exchange/__init__.py
"""
GIS Data Exchange Utilities
Bulk import/export of Shapefile, KML and GeoJSON for seamless integration
with Rwanda Land Management and Use Authority (RLMUA) data.
"""

from app.services.gis.data_exchange.base import GisFeature, GisDataset, WGS84_CRS
from app.services.gis.data_exchange.geojson_io import geojson_to_dataset, dataset_to_geojson
from app.services.gis.data_exchange.kml_io import kml_to_dataset, dataset_to_kml
from app.services.gis.data_exchange.shapefile_io import read_shapefile, write_shapefile
from app.services.gis.data_exchange.exchange_service import GisExchangeService

__all__ = [
    "GisFeature",
    "GisDataset",
    "WGS84_CRS",
    "geojson_to_dataset",
    "dataset_to_geojson",
    "kml_to_dataset",
    "dataset_to_kml",
    "read_shapefile",
    "write_shapefile",
    "GisExchangeService",
]
