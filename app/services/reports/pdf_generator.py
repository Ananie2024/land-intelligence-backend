# app/services/reports/pdf_generator.py
"""
PDF Report Generation
Land Intelligence System

Generates PDF reports for tax records, parcels, and dashboard statistics.
"""

import io
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

logger = logging.getLogger(__name__)


def generate_tax_pdf(
    parcel_data: Dict[str, Any],
    records: List[Dict[str, Any]],
    title: str = "Tax Assessment Report"
) -> bytes:
    """
    Generate a PDF report for tax data.
    
    Args:
        parcel_data: Parcel information (id, number, owner, etc.)
        records: List of tax assessment records
        title: Report title
        
    Returns:
        PDF file content as bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title=title)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        spaceAfter=24,
        textColor=colors.darkblue,
    )
    
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        spaceBefore=12,
        spaceAfter=8,
        textColor=colors.darkblue,
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))
    
    # Generation timestamp
    elements.append(
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"])
    )
    elements.append(Spacer(1, 12))
    
# Parcel Information
    elements.append(Paragraph("Parcel Information", heading_style))
    parcel_info = [
        ["UPI", parcel_data.get("upi", "N/A")],
        ["Owner", parcel_data.get("owner_name", "N/A")],
        ["Area (sqm)", f"{parcel_data.get('area_sqm', 0):,.2f}"],
        ["Total Outstanding", f"${parcel_data.get('total_outstanding', 0):,.2f}"],
    ]
    
    table = Table(parcel_info, colWidths=[2 * inch, 4 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    
    # Tax Records Table
    if records:
        elements.append(Paragraph("Assessment Records", heading_style))
        
        # Table header
        record_data = [["Year", "Assessed Value", "Base Tax", "Penalties", "Total", "Status", "Due Date"]]
        
        for record in records:
            record_data.append([
                str(record.get("assessment_year", "")),
                f"${record.get('assessed_value', 0):,.2f}",
                f"${record.get('base_tax_amount', 0):,.2f}",
                f"${record.get('penalties_amount', 0):,.2f}",
                f"${record.get('total_amount', 0):,.2f}",
                record.get("status", ""),
                str(record.get("due_date", "")),
            ])
        
        record_table = Table(record_data, colWidths=[0.7 * inch] * 7)
        record_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (1, 1), (-2, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(record_table)
    
    doc.build(elements)
    return buffer.getvalue()


def generate_parcels_pdf(
    parcels: List[Dict[str, Any]],
    stats: Optional[Dict[str, Any]] = None,
    title: str = "Land Parcels Report"
) -> bytes:
    """
    Generate a PDF report for parcels data.
    
    Args:
        parcels: List of parcel records
        stats: Optional statistics summary
        title: Report title
        
    Returns:
        PDF file content as bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title=title)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        spaceAfter=24,
        textColor=colors.darkblue,
    )
    
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        spaceBefore=12,
        spaceAfter=8,
        textColor=colors.darkblue,
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))
    elements.append(
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"])
    )
    elements.append(Spacer(1, 12))
    
    # Statistics Summary (if provided)
    if stats:
        elements.append(Paragraph("Summary Statistics", heading_style))
        stats_data = [
            ["Total Parcels", f"{stats.get('total_parcels', 0):,}"],
            ["Total Area (sqm)", f"{stats.get('total_area_sqm', 0):,.2f}"],
            ["Total Valuation", f"${stats.get('total_valuation', 0):,.2f}"],
        ]
        
        stats_table = Table(stats_data, colWidths=[2 * inch, 4 * inch])
        stats_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 12))
    
    # Parcels Table (first page - summary)
    elements.append(PageBreak())
    elements.append(Paragraph("Parcel Summary", heading_style))
    
# Build parcel data table
    parcel_data = [["#", "UPI", "Owner", "Area (sqm)", "Valuation", "Parish"]]
    
    for i, parcel in enumerate(parcels[:50], 1):  # Limit to 50 for PDF
        parcel_data.append([
            str(i),
            parcel.get("upi", "N/A"),
            parcel.get("owner_name", "N/A")[:25] + "..." if len(parcel.get("owner_name", "")) > 25 else parcel.get("owner_name", "N/A"),
            f"{parcel.get('area_sqm', 0):,.0f}",
            f"${parcel.get('valuation', 0) or 0:,.0f}",
            parcel.get("parish_name", "N/A"),
        ])
    
    parcel_table = Table(parcel_data, colWidths=[0.4 * inch, 1.2 * inch, 2 * inch, 1.2 * inch, 1.2 * inch, 1.5 * inch])
    parcel_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
        ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(parcel_table)
    
    doc.build(elements)
    return buffer.getvalue()


def generate_dashboard_pdf(
    stats: Dict[str, Any],
    title: str = "System Dashboard Report"
) -> bytes:
    """
    Generate a PDF report for dashboard statistics.
    
    Args:
        stats: Complete system statistics
        title: Report title
        
    Returns:
        PDF file content as bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title=title)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        spaceAfter=24,
        textColor=colors.darkblue,
    )
    
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        spaceBefore=12,
        spaceAfter=8,
        textColor=colors.darkblue,
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))
    elements.append(
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"])
    )
    elements.append(Spacer(1, 24))
    
    # Parish Statistics
    elements.append(Paragraph("Parish Statistics", heading_style))
    parish_stats = stats.get("parishes", {})
    parish_data = [
        ["Total Parishes", f"{parish_stats.get('total_parishes', 0):,}"],
        ["Total Parcels in Parishes", f"{parish_stats.get('total_parcels', 0):,}"],
        ["Avg Parcels/Parish", f"{parish_stats.get('avg_parcels_per_parish', 0):,.2f}"],
    ]
    
    parish_table = Table(parish_data, colWidths=[2.5 * inch, 2.5 * inch])
    parish_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(parish_table)
    elements.append(Spacer(1, 12))
    
    # Parcel Statistics
    elements.append(Paragraph("Parcel Statistics", heading_style))
    parcel_stats = stats.get("parcels", {})
    parcel_data = [
        ["Total Parcels", f"{parcel_stats.get('total_parcels', 0):,}"],
        ["Total Area (sqm)", f"{parcel_stats.get('total_area_sqm', 0):,.2f}"],
        ["Total Valuation", f"${parcel_stats.get('total_valuation', 0):,.2f}"],
        ["Parcels with Deeds", f"{parcel_stats.get('parcels_with_deeds', 0):,}"],
    ]
    
    parcel_table = Table(parcel_data, colWidths=[2.5 * inch, 2.5 * inch])
    parcel_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(parcel_table)
    elements.append(Spacer(1, 12))
    
    # User Statistics
    elements.append(Paragraph("User Statistics", heading_style))
    user_stats = stats.get("users", {})
    user_data = [
        ["Total Users", f"{user_stats.get('total_users', 0):,}"],
        ["Admin Users", f"{user_stats.get('admin_count', 0):,}"],
        ["Client Users", f"{user_stats.get('client_count', 0):,}"],
        ["Viewer Users", f"{user_stats.get('viewer_count', 0):,}"],
    ]
    
    user_table = Table(user_data, colWidths=[2.5 * inch, 2.5 * inch])
    user_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(user_table)
    
    doc.build(elements)
    return buffer.getvalue()