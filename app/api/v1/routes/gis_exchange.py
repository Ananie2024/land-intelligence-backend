# app/api/v1/routes/gis_exchange.py
"""
GIS Bulk Import / Export API Routes
Phase 3 — Section 4.3
Land Intelligence System

Endpoints for exchanging parcel data with the Rwanda Land Management and
Use Authority (RLMUA) in Shapefile, KML and GeoJSON formats.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_id
from app.services.gis.data_exchange.exchange_service import GisExchangeService
from app.services.gis.data_exchange.rlmua_profile import normalize_properties
from app.schemas.gis_exchange_schema import GisImportResponse, ImportedFeature

logger = logging.getLogger(__name__)

router = APIRouter()

_SUPPORTED_IMPORT_FORMATS = {"geojson", "json", "kml", "kmz", "shp", "shapefile"}
_SHAPEFILE_EXTENSIONS = {".shp", ".shx", ".dbf", ".prj", ".cpg"}


async def _read_upload(file: UploadFile) -> bytes:
    """Read the full contents of an uploaded file."""
    return await file.read()


def _extension(filename: str) -> str:
    return f".{(filename or '').rsplit('.', 1)[-1].lower()}"


@router.post(
    "/import",
    response_model=GisImportResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk import GIS data",
    description=(
        "Decode a Shapefile, KML or GeoJSON payload into canonical features "
        "for RLMUA integration. Provide `format`, the source CRS (`source_crs`) "
        "and the attribute mapping profile (`profile`). Shapefiles require at "
        "least a `.shp` file and optionally a `.dbf` table."
    ),
)
async def import_gis_data(
    format: str = Form(...),
    source_crs: str = Form("EPSG:4326", description="CRS of the source data"),
    profile: str = Form("rlmua", description="Attribute mapping profile"),
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    fmt = format.strip().lower()
    if fmt not in _SUPPORTED_IMPORT_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{format}'. Supported: geojson, kml, kmz, shapefile.",
        )

    try:
        if fmt in ("geojson", "json"):
            if not files:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "A GeoJSON file is required.")
            raw = await _read_upload(files[0])
            dataset = GisExchangeService.import_geojson(raw, source_crs)
        elif fmt == "kml":
            if not files:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "A KML file is required.")
            raw = await _read_upload(files[0])
            dataset = GisExchangeService.import_kml(raw, source_crs)
        elif fmt == "kmz":
            if not files:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "A KMZ file is required.")
            raw = await _read_upload(files[0])
            dataset = GisExchangeService.import_kmz(raw, source_crs)
        else:  # shapefile
            shp_bytes: Optional[bytes] = None
            dbf_bytes: Optional[bytes] = None
            for file in files:
                ext = _extension(file.filename or "")
                if ext == ".shp":
                    shp_bytes = await _read_upload(file)
                elif ext == ".dbf":
                    dbf_bytes = await _read_upload(file)
            if not shp_bytes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A .shp file is required for shapefile import.",
                )
            dataset = GisExchangeService.import_shapefile(shp_bytes, dbf_bytes, source_crs)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.error(f"GIS import failed: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to parse the uploaded GIS data: {str(exc)}",
        )

    # Map attributes onto canonical parcel fields for the caller
    response_features: List[ImportedFeature] = []
    errors: List[str] = []
    imported = 0
    skipped = 0

    for index, feature in enumerate(dataset.features):
        canonical, extra = normalize_properties(feature.properties, profile)
        normalized = {**extra, **canonical}
        geometry_type = feature.geometry.geom_type if feature.has_geometry() else None
        if geometry_type is None:
            skipped += 1
            errors.append(f"Feature {index + 1}: missing geometry, skipped.")
        else:
            imported += 1

        response_features.append(
            ImportedFeature(
                index=index,
                geometry_type=geometry_type,
                properties=feature.properties,
                normalized=normalized,
            )
        )

    return GisImportResponse(
        format=format,
        source_crs=source_crs,
        total_features=len(dataset.features),
        imported=imported,
        skipped=skipped,
        features=response_features,
        errors=errors,
    )
async def _stream_export(service: GisExchangeService, export_format: str, parish_id: Optional[str]):
    try:
        media_type, filename, payload = await service.export(export_format, parish_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.error(f"GIS export failed: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to prepare the export: {str(exc)}",
        )

    return StreamingResponse(
        iter([payload]),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/export/geojson",
    summary="Export parcels as GeoJSON",
    description="Download all active parcels as a GeoJSON FeatureCollection.",
)
async def export_parcels_geojson(
    parish_id: Optional[str] = Query(None, description="Filter by parish UUID"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    return await _stream_export(GisExchangeService(db), "geojson", parish_id)


@router.get(
    "/export/kml",
    summary="Export parcels as KML",
    description="Download all active parcels as a KML 2.2 document.",
)
async def export_parcels_kml(
    parish_id: Optional[str] = Query(None, description="Filter by parish UUID"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    return await _stream_export(GisExchangeService(db), "kml", parish_id)


@router.get(
    "/export/kmz",
    summary="Export parcels as KMZ",
    description="Download all active parcels as a Google Earth KMZ archive "
                "(a ZIP containing a KML document).",
)
async def export_parcels_kmz(
    parish_id: Optional[str] = Query(None, description="Filter by parish UUID"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    return await _stream_export(GisExchangeService(db), "kmz", parish_id)


@router.get(
    "/export/shapefile",
    summary="Export parcels as a Shapefile",
    description="Download all active parcels as a ZIP archive containing the "
                "ESRI Shapefile (.shp/.shx/.dbf/.prj) in WGS84.",
)
async def export_parcels_shapefile(
    parish_id: Optional[str] = Query(None, description="Filter by parish UUID"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    return await _stream_export(GisExchangeService(db), "shapefile", parish_id)
