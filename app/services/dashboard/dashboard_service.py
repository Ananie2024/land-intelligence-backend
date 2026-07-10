# app/services/dashboard/dashboard_service.py
"""
Dashboard Service
Land Intelligence System

Business logic for dashboard statistics and system overview.
"""

import logging
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parish import Parish
from app.models.parcel import Parcel
from app.models.document import Document
from app.schemas.dashboard_schema import (
    SystemStats,
    ParishStats,
    ParcelStats,
    UserStats,
    DocumentStats,
    DatabaseStats,
)

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Business logic layer for dashboard statistics.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_system_stats(self) -> SystemStats:
        """
        Get comprehensive system statistics for the dashboard.
        """
        # Parish statistics
        parish_result = await self.db.execute(
            select(
                func.count(Parish.id).label("total_parishes"),
                func.coalesce(func.sum(Parish.parcel_count), 0).label("total_parcels"),
            ).where(Parish.is_active)
        )
        parish_row = parish_result.first()
        if parish_row is None:
            total_parishes = 0
            total_parcels = 0
        else:
            total_parishes = parish_row.total_parishes or 0
            total_parcels = int(parish_row.total_parcels) or 0
        avg_parcels = total_parcels / total_parishes if total_parishes > 0 else 0

        parish_stats = ParishStats(
            total_parishes=total_parishes,
            total_parcels=total_parcels,
            avg_parcels_per_parish=round(avg_parcels, 2),
        )

        # Parcel statistics
        parcel_result = await self.db.execute(
            select(
                func.count(Parcel.id).label("total_parcels"),
                func.coalesce(func.sum(Parcel.area_sqm), 0).label("total_area_sqm"),
                func.coalesce(func.sum(Parcel.valuation), 0).label("total_valuation"),
                func.count(Parcel.title_deed_number).label("parcels_with_deeds"),
            ).where(Parcel.is_active)
        )
        parcel_row = parcel_result.first()

        parcel_stats = ParcelStats(
            total_parcels=parcel_row.total_parcels if parcel_row else 0,
            total_area_sqm=float(parcel_row.total_area_sqm) if parcel_row and parcel_row.total_area_sqm else 0.0,
            total_valuation=float(parcel_row.total_valuation) if parcel_row and parcel_row.total_valuation else 0.0,
            parcels_with_deeds=parcel_row.parcels_with_deeds if parcel_row else 0,
        )

        # User statistics - use raw SQL text to avoid enum casting issues
        user_result = await self.db.execute(text("""
            SELECT 
                count(users.id) AS total_users,
                count(users.id) FILTER (WHERE users.role::text = 'admin') AS admin_count,
                count(users.id) FILTER (WHERE users.role::text = 'client') AS client_count,
                count(users.id) FILTER (WHERE users.role::text = 'viewer') AS viewer_count
            FROM users 
            WHERE users.is_active
        """))
        user_row = user_result.first()

        user_stats = UserStats(
            total_users=user_row.total_users if user_row else 0,
            admin_count=user_row.admin_count if user_row else 0,
            client_count=user_row.client_count if user_row else 0,
            viewer_count=user_row.viewer_count if user_row else 0,
        )

        # Document statistics
        doc_result = await self.db.execute(
            select(
                func.count(Document.id).label("total_documents"),
                func.coalesce(func.sum(Document.file_size_bytes), 0).label("total_size_bytes"),
            ).where(Document.is_active)
        )
        doc_row = doc_result.first()

        document_stats = DocumentStats(
            total_documents=doc_row.total_documents if doc_row else 0,
            total_size_bytes=int(doc_row.total_size_bytes) if doc_row and doc_row.total_size_bytes else 0,
        )

        # Database stats
        database_stats = DatabaseStats(
            database_status="healthy",
            database_version=None,
        )

        return SystemStats(
            parishes=parish_stats,
            parcels=parcel_stats,
            users=user_stats,
            documents=document_stats,
            database=database_stats,
        )

    async def get_parish_stats(self) -> ParishStats:
        """Get parish statistics only."""
        result = await self.db.execute(
            select(
                func.count(Parish.id).label("total_parishes"),
                func.coalesce(func.sum(Parish.parcel_count), 0).label("total_parcels"),
            ).where(Parish.is_active)
        )
        row = result.first()
        
        if row is None:
            return ParishStats(
                total_parishes=0,
                total_parcels=0,
                avg_parcels_per_parish=0.0,
            )
        
        total_parishes = row.total_parishes or 0
        total_parcels = int(row.total_parcels) or 0
        avg_parcels = total_parcels / total_parishes if total_parishes > 0 else 0

        return ParishStats(
            total_parishes=total_parishes,
            total_parcels=total_parcels,
            avg_parcels_per_parish=round(avg_parcels, 2),
        )

    async def get_parcel_stats(self) -> ParcelStats:
        """Get parcel statistics only."""
        result = await self.db.execute(
            select(
                func.count(Parcel.id).label("total_parcels"),
                func.coalesce(func.sum(Parcel.area_sqm), 0).label("total_area_sqm"),
                func.coalesce(func.sum(Parcel.valuation), 0).label("total_valuation"),
                func.count(Parcel.title_deed_number).label("parcels_with_deeds"),
            ).where(Parcel.is_active)
        )
        row = result.first()

        if row is None:
            return ParcelStats(
                total_parcels=0,
                total_area_sqm=0.0,
                total_valuation=0.0,
                parcels_with_deeds=0,
            )

        return ParcelStats(
            total_parcels=row.total_parcels or 0,
            total_area_sqm=float(row.total_area_sqm) if row.total_area_sqm else 0.0,
            total_valuation=float(row.total_valuation) if row.total_valuation else 0.0,
            parcels_with_deeds=row.parcels_with_deeds or 0,
        )

    async def get_user_stats(self) -> UserStats:
        """Get user statistics only."""
        result = await self.db.execute(text("""
            SELECT 
                count(users.id) AS total_users,
                count(users.id) FILTER (WHERE users.role::text = 'admin') AS admin_count,
                count(users.id) FILTER (WHERE users.role::text = 'client') AS client_count,
                count(users.id) FILTER (WHERE users.role::text = 'viewer') AS viewer_count
            FROM users 
            WHERE users.is_active
        """))
        row = result.first()

        if row is None:
            return UserStats(
                total_users=0,
                admin_count=0,
                client_count=0,
                viewer_count=0,
            )

        return UserStats(
            total_users=row.total_users or 0,
            admin_count=row.admin_count or 0,
            client_count=row.client_count or 0,
            viewer_count=row.viewer_count or 0,
        )
