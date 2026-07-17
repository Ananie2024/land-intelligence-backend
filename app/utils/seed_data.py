# app/utils/seed_data.py
"""
Seed Data for Initial Document Types
Land Intelligence System
"""

from typing import TypedDict, List

from app.models.enums import DocumentType


class DocumentTypeSeed(TypedDict):
    code: str
    name: str
    description: str
    requires_verification: bool
    retention_years: str


# Default document types for Land Registry
# These are the standard document types used in the land management system
DOCUMENT_TYPE_SEEDS: List[DocumentTypeSeed] = [
    {
        "code": DocumentType.LAND_TITLES.value,
        "name": "Land Titles",
        "description": "Official land title documents proving ownership of property",
        "requires_verification": True,
        "retention_years": "PERMANENT",
    },
    {
        "code": DocumentType.LAND_DEEDS.value,
        "name": "Land Deeds",
        "description": "Legal deeds and conveyances for land transfers",
        "requires_verification": True,
        "retention_years": "PERMANENT",
    },
    {
        "code": DocumentType.LETTERS.value,
        "name": "Letters",
        "description": "Official correspondence related to land matters",
        "requires_verification": False,
        "retention_years": "PERMANENT",
    },
    {
        "code": DocumentType.LAND_LEASES.value,
        "name": "Land Leases",
        "description": "Lease agreements for land and property rental",
        "requires_verification": True,
        "retention_years": "PERMANENT",
    },
    {
        "code": DocumentType.REPORTS.value,
        "name": "Reports",
        "description": "Assessment reports, valuation reports, and other land-related reports",
        "requires_verification": False,
        "retention_years": "PERMANENT",
    },
    {
        "code": DocumentType.SURVEYS.value,
        "name": "Surveys (Mapping)",
        "description": "Survey maps and land measurement documents",
        "requires_verification": True,
        "retention_years": "PERMANENT",
    },
    {
        "code": DocumentType.CESSION.value,
        "name": "Contrat de Cession Gratuite",
        "description": "Documents for free transfer of property (deed of gift)",
        "requires_verification": True,
        "retention_years": "PERMANENT",
    },
    {
        "code": DocumentType.OTHERS.value,
        "name": "Others",
        "description": "Other document types not specifically categorized",
        "requires_verification": False,
        "retention_years": "PERMANENT",
    },
    {
        "code": DocumentType.UNSPECIFIED.value,
        "name": "Unspecified",
        "description": "Documents that do not fit into other categories",
        "requires_verification": False,
        "retention_years": "PERMANENT",
    },
]