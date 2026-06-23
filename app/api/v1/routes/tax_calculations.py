# app/api/v1/routes/tax_calculations.py
"""
Tax Calculations API Route Endpoints
Phase 3 — Section 4.2
Land Intelligence System
"""

import logging
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_id
from app.services.tax.tax_service import TaxService
from app.schemas.tax_schema import (
    TaxCalculationRequest,
    TaxCalculationResponse,
    TaxRecordResponse,
    TaxPaymentRequest,
    TaxPaymentResponse,
    OutstandingBalanceResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/calculate",
    response_model=TaxCalculationResponse,
    summary="Simulate tax calculation",
    description="Calculate gross tax liability, accrued penalties, and net amount due for a parcel without storing a record."
)
async def calculate_tax(
    payload: TaxCalculationRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        service = TaxService(db)
        result = await service.calculate_tax(
            parcel_id=payload.parcel_id,
            assessment_year=payload.assessment_year,
            land_use_category_id=payload.land_use_category_id,
            include_penalties=payload.include_penalties
        )
        
        return TaxCalculationResponse(
            parcel_id=result["parcel_id"],
            parcel_number=result["parcel_number"],
            assessment_year=result["assessment_year"],
            land_use_category_name=result["land_use_category_name"],
            area_sqm=result["area_sqm"],
            assessed_value=result["assessed_value"],
            tax_rate=result["tax_rate"],
            base_tax_amount=result["base_tax_amount"],
            penalties_amount=result["penalties_amount"],
            total_amount=result["total_amount"],
            due_date=result["due_date"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error calculating tax: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal tax calculation error: {str(e)}"
        )


@router.post(
    "/assess",
    response_model=TaxRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create tax assessment record",
    description="Generate a permanent annual tax assessment record for a parcel."
)
async def generate_assessment(
    payload: TaxCalculationRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        service = TaxService(db)
        record = await service.generate_assessment(
            parcel_id=payload.parcel_id,
            assessment_year=payload.assessment_year,
            user_id=user_id
        )
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Failed to generate assessment."
            )
        
        await db.commit()
        await db.refresh(record)
        
        logger.info(f"Tax assessment generated for parcel {payload.parcel_id} year {payload.assessment_year} by user {user_id}")
        return record
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating tax assessment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal assessment generation error: {str(e)}"
        )


@router.post(
    "/assess/parish/{parish_id}",
    summary="Batch assess parish parcels",
    description="Generate tax assessments for all active parcels belonging to a specific parish."
)
async def generate_parish_assessments(
    parish_id: str,
    assessment_year: str = Query(..., pattern=r"^\d{4}$", description="Assessment year"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        service = TaxService(db)
        result = await service.generate_parish_assessments(
            parish_id=parish_id,
            assessment_year=assessment_year,
            user_id=user_id
        )
        await db.commit()
        
        logger.info(f"Batch tax assessments generated for parish {parish_id} year {assessment_year} by user {user_id}")
        return {
            "success": True,
            "message": f"Successfully completed batch assessment generation for parish '{parish_id}' year '{assessment_year}'.",
            "summary": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error batch assessing parish: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal batch assessment error: {str(e)}"
        )


@router.post(
    "/payments",
    response_model=TaxPaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record tax payment",
    description="Post a tax payment transaction against an annual assessment record, handling penalty priorities."
)
async def record_tax_payment(
    payload: TaxPaymentRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        service = TaxService(db)
        res = await service.record_tax_payment(
            tax_record_id=payload.tax_record_id,
            payment_amount=payload.payment_amount,
            payment_method=payload.payment_method,
            payment_reference=payload.payment_reference,
            payment_date=payload.payment_date,
            user_id=user_id
        )
        
        if not res["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=res.get("error", "Failed to process payment")
            )
            
        # Commit transaction and fetch payment object to return
        await db.commit()
        payment_id = res["payment_id"]
        
        logger.info(f"Tax payment recorded: {payment_id} amount {payload.payment_amount} by user {user_id}")
        return res
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing tax payment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal payment processing error: {str(e)}"
        )


@router.get(
    "/outstanding/{parcel_id}",
    response_model=OutstandingBalanceResponse,
    summary="Get outstanding tax balance",
    description="Calculate the breakdown of outstanding, overdue, and upcoming tax liabilities for a parcel."
)
async def get_outstanding_tax(
    parcel_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        service = TaxService(db)
        result = await service.get_outstanding_tax(parcel_id, _)
        
        return OutstandingBalanceResponse(
            parcel_id=result["parcel_id"],
            parcel_number=result["parcel_number"],
            total_outstanding=result["total_outstanding"],
            overdue_amount=result["overdue_amount"],
            upcoming_amount=result["upcoming_amount"],
            records=result["records"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching outstanding balance: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal tax data retrieval error: {str(e)}"
        )


@router.get(
    "/history/{parcel_id}",
    response_model=List[TaxPaymentResponse],
    summary="Get payment history",
    description="Retrieve all historical payment transactions posted for a parcel's assessments."
)
async def get_payment_history(
    parcel_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        service = TaxService(db)
        result = await service.get_payment_history(parcel_id, skip=skip, limit=limit, user_id=_)
        
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching payment history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal payment query error: {str(e)}"
        )


@router.get(
    "/record/{record_id}",
    response_model=TaxRecordResponse,
    summary="Get tax assessment record detail",
    description="Fetch details of a single tax record by UUID."
)
async def get_tax_record(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        service = TaxService(db)
        record = await service.get_tax_record(record_id, _)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tax record with ID '{record_id}' not found."
            )
        return record
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching tax record: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal database query error: {str(e)}"
        )