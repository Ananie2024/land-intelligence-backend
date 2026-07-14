# app/services/reports/reports_service.py
"""
Reports Service
Land Intelligence System

Business logic for generating reports in PDF and Excel formats.
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.tax.tax_service import TaxService
from app.services.parcel.parcel_service import ParcelService
from app.services.dashboard.dashboard_service import DashboardService
from app.services.reports.pdf_generator import (
    generate_tax_pdf,
    generate_parcels_pdf,
    generate_dashboard_pdf,
)
from app.services.reports.excel_generator import (
    generate_tax_excel,
    generate_parcels_excel,
    generate_dashboard_excel,
)

logger = logging.getLogger(__name__)


class ReportsService:
    """
    Service for generating reports in various formats.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.tax_service = TaxService(db)
        self.parcel_service = ParcelService(db)
        self.dashboard_service = DashboardService(db)
    
    async def generate_tax_report(
        self,
        parcel_upi: str,
        output_format: str = "pdf"
    ) -> bytes:
        """
        Generate a tax report for a specific parcel using UPI.
        
        Args:
            parcel_upi: Unique Parcel Identifier (UPI) - e.g. 1/02/02/03/1390
            output_format: Either 'pdf' or 'excel'
            
        Returns:
            Report file content as bytes
        """
        # Get outstanding tax data using UPI
        outstanding = await self.tax_service.get_outstanding_tax(parcel_upi, None)
        
        if not outstanding:
            raise ValueError(f"No tax records found for parcel {parcel_upi}")
        
        parcel_data = {
            "parcel_upi": parcel_upi,
            "upi": outstanding.get("upi", ""),
            "owner_name": "",
            "area_sqm": 0,
            "total_outstanding": outstanding.get("total_outstanding", 0),
            "overdue_amount": outstanding.get("overdue_amount", 0),
            "upcoming_amount": outstanding.get("upcoming_amount", 0),
        }
        
        # Get parcel details for owner name using UPI
        parcel = await self.parcel_service.get_parcel_by_upi(parcel_upi)
        if parcel:
            parcel_data["owner_name"] = parcel.owner_name
            parcel_data["area_sqm"] = parcel.area_sqm
        
        records = outstanding.get("records", [])
        
        if output_format == "pdf":
            return generate_tax_pdf(parcel_data, records)
        elif output_format == "excel":
            return generate_tax_excel(parcel_data, records)
        else:
            raise ValueError(f"Unsupported format: {output_format}")
    
    async def generate_parcels_report(
        self,
        parish_id: Optional[str] = None,
        output_format: str = "pdf"
    ) -> bytes:
        """
        Generate a parcels report.
        
        Args:
            parish_id: Optional parish filter
            output_format: Either 'pdf' or 'excel'
            
        Returns:
            Report file content as bytes
        """
        # Get parcels
        if parish_id:
            parcels_result = await self.parcel_service.list_parcels_by_parish(parish_id)
            parcels = parcels_result.items
        else:
            # Get all active parcels
            parcels_result = await self.parcel_service.list_parcels(1, 1000, {})
            parcels = parcels_result.items
        
        # Get statistics
        stats = {
            "total_parcels": len(parcels),
            "total_area_sqm": sum(getattr(p, "area_sqm", 0) or 0 for p in parcels),
            "total_valuation": sum(getattr(p, "valuation", 0) or 0 for p in parcels),
        }
        
        # Convert to list of dicts for report generator
        parcel_list = [
            {
                "upi": getattr(p, "upi", ""),
                "owner_name": getattr(p, "owner_name", ""),
                "area_sqm": getattr(p, "area_sqm", 0) or 0,
                "valuation": getattr(p, "valuation", None),
                "parish_name": getattr(p, "parish_name", ""),
                "land_use_category_name": getattr(p, "land_use_category_name", ""),
            }
            for p in parcels
        ]
        
        if output_format == "pdf":
            return generate_parcels_pdf(parcel_list, stats)
        elif output_format == "excel":
            return generate_parcels_excel(parcel_list, stats)
        else:
            raise ValueError(f"Unsupported format: {output_format}")
    
    async def generate_dashboard_report(
        self,
        output_format: str = "pdf"
    ) -> bytes:
        """
        Generate a dashboard statistics report.
        
        Args:
            output_format: Either 'pdf' or 'excel'
            
        Returns:
            Report file content as bytes
        """
        stats = await self.dashboard_service.get_system_stats()
        
        # Convert stats to dict
        stats_dict = stats.model_dump() if hasattr(stats, "model_dump") else stats
        
        if output_format == "pdf":
            return generate_dashboard_pdf(stats_dict)
        elif output_format == "excel":
            return generate_dashboard_excel(stats_dict)
        else:
            raise ValueError(f"Unsupported format: {output_format}")