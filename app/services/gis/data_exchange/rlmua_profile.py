# app/services/gis/data_exchange/rlmua_profile.py
"""
RLMUA Data Exchange Profile
Phase 3 — Section 4.3
Land Intelligence System

Maps attribute field names used by the Rwanda Land Management and Use
Authority (RLMUA) cadastral exports onto the canonical parcel fields of the
Land Intelligence System. Kept as a data-driven profile so future authority
field-name variations can be added without touching serializer code.
"""

from typing import Any, Dict, List, Tuple

# Canonical Land Intelligence parcel attributes
CANONICAL_FIELDS = [
    "upi",
    "owner_name",
    "owner_contact",
    "area_sqm",
    "land_use",
    "location_description",
    "valuation",
    "valuation_date",
]

# Source alias -> canonical field. Aliases are matched case-insensitively.
RLMUA_ALIASES: Dict[str, List[str]] = {
    "upi": [
        "upi", "ParcelUPI", "parcel_upi", "PARCEL_UPI", "PlotNo", "PLOT_NO",
        "plot_no", "Plot_No", "ParcelID", "parcel_id", "Parcel_No",
    ],
    "owner_name": [
        "owner_name", "OwnerName", "OWNER_NAME", "owner", "Owner", "OWNER",
        "Owners", "owners", "Proprietaire", "NomProprietaire", "prop_name",
        "Owner_Name", "LANDHOLDER", "landholder",
    ],
    "owner_contact": [
        "owner_contact", "OwnerContact", "OWNER_CONTACT", "contact", "Contact",
        "CONTACT", "phone", "Phone", "PHONE", "phone_number", "tel",
    ],
    "area_sqm": [
        "area_sqm", "area", "Area", "AREA", "Shape_Area", "SHAPE_AREA",
        "shape_area", "area_m2", "AreaSqm", "Size", "land_size", "PARCEL_AREA",
    ],
    "land_use": [
        "land_use", "LandUse", "LAND_USE", "land_use_category", "LandUseCategory",
        "LandUseType", "use_code", "USE_CODE", "landuse", "LandUseCode",
    ],
    "location_description": [
        "location_description", "Location", "LOCATION", "location_desc", "address",
        "Address", "Village", "village", "VILLAGE", "Cell", "cell", "CELL",
        "Sector", "sector", "Umurenge", "Akarere", "site",
    ],
    "valuation": [
        "valuation", "Valuation", "VALUATION", "value", "Value", "VALUE",
        "price", "Price", "Amount", "amount", "land_value",
    ],
    "valuation_date": [
        "valuation_date", "ValuationDate", "VALUATION_DATE", "val_date",
    ],
}

# Canonical field -> export column name (used when writing RLMUA-oriented files)
EXPORT_FIELD_NAMES: Dict[str, str] = {
    "upi": "UPI",
    "owner_name": "OwnerName",
    "owner_contact": "OwnerContact",
    "area_sqm": "AreaSqm",
    "land_use": "LandUse",
    "location_description": "Location",
    "valuation": "Valuation",
    "valuation_date": "ValuationDate",
}


def _build_alias_lookup() -> Dict[str, str]:
    lookup: Dict[str, str] = {}
    for canonical, aliases in RLMUA_ALIASES.items():
        for alias in aliases:
            lookup[alias.strip().lower()] = canonical
        lookup[canonical.lower()] = canonical
    return lookup


_ALIAS_LOOKUP = _build_alias_lookup()


def _to_float(value: Any) -> Any:
    """Best-effort numeric coercion for metric/cadastral values."""
    if isinstance(value, bool) or value is None:
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def normalize_properties(
    properties: Dict[str, Any],
    profile: str = "rlmua",
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Map source attribute names onto canonical parcel fields.

    Args:
        properties: Raw attribute dictionary from an imported feature
        profile: Mapping profile name ('rlmua' is the only built-in profile)

    Returns:
        Tuple of (canonical_fields, extra_fields). Extra fields keep their
        original keys so no data is lost during import.
    """
    if profile not in ("rlmua", "rlmu", "default"):
        raise ValueError(f"Unsupported import profile: {profile!r}")

    canonical: Dict[str, Any] = {}
    extra: Dict[str, Any] = {}

    for key, value in properties.items():
        canonical_key = _ALIAS_LOOKUP.get(str(key).strip().lower())
        if canonical_key:
            canonical[canonical_key] = value
        else:
            extra[key] = value

    # Coerce numeric cadastral fields for downstream parcel creation
    for numeric_field in ("area_sqm", "valuation"):
        if numeric_field in canonical:
            canonical[numeric_field] = _to_float(canonical[numeric_field])

    return canonical, extra


def export_field_name(canonical_field: str) -> str:
    """Return the RLMUA-oriented column name used when exporting parcels."""
    return EXPORT_FIELD_NAMES.get(canonical_field, canonical_field)
