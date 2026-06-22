# app/api/v1/routes/tax_calculations.py
"""
Tax Calculations API Route Endpoints
Phase 3 — Section 4.2
Land Intelligence System
"""

import logging
from decimal import Decimal
from typing import List, Optional
from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_id
from app.repositories.tax_repository import TaxRepository
from app.repositories.parcel_repository import ParcelRepository
from app.repositories.parish_repository import ParishRepository
from app.models.tax_record import TaxRecord
from app.models.tax_payment import TaxPayment
from app.services.tax.tax_calculator import TaxCalculator
from app.services.tax.penalty_engine import PenaltyEngine
from app.services.tax.assessment_generator import AssessmentGenerator
from app.services.tax.payment_processor import PaymentProcessor
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

# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------

async def get_tax_repository(db: AsyncSession = Depends(get_db)) -> TaxRepository:
    return TaxRepository(db)

async def get_penalty_engine(repo: TaxRepository = Depends(get_tax_repository)) -> PenaltyEngine:
    return PenaltyEngine(repo)

async def get_tax_calculator(repo: TaxRepository = Depends(get_tax_repository)) -> TaxCalculator:
    return TaxCalculator(repo)

async def get_assessment_generator(
    repo: TaxRepository = Depends(get_tax_repository),
    calc: TaxCalculator = Depends(get_tax_calculator),
    pe: PenaltyEngine = Depends(get_penalty_engine)
) -> AssessmentGenerator:
    return AssessmentGenerator(repo, calc, pe)

async def get_payment_processor(
    repo: TaxRepository = Depends(get_tax_repository),
    pe: PenaltyEngine = Depends(get_penalty_engine)
) -> PaymentProcessor:
    return PaymentProcessor(repo, pe)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

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
    calculator: TaxCalculator = Depends(get_tax_calculator),
    repo: TaxRepository = Depends(get_tax_repository)
):
    try:
        parcel_repo = ParcelRepository(db)
        parcel = await parcel_repo.get(payload.parcel_id)
        if not parcel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parcel with ID '{payload.parcel_id}' not found."
            )
            
        override_category = None
        category_name = "Unassigned"
        if payload.land_use_category_id:
            from app.models.land_use_category import LandUseCategory
            res = await db.execute(
                select(LandUseCategory).where(
                    LandUseCategory.id == payload.land_use_category_id,
                    LandUseCategory.is_active
                )
            )
            override_category = res.scalar_one_or_none()
            if not override_category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Land use category override '{payload.land_use_category_id}' not found."
                )
            category_name = override_category.name
        else:
            if parcel.land_use_category_id:
                from app.models.land_use_category import LandUseCategory
                res = await db.execute(
                    select(LandUseCategory).where(
                        LandUseCategory.id == parcel.land_use_category_id,
                        LandUseCategory.is_active
                    )
                )
                cat = res.scalar_one_or_none()
                if cat:
                    category_name = cat.name
                    
        calc_result = await calculator.calculate_tax(
            parcel=parcel,
            assessment_year=payload.assessment_year,
            land_use_category=override_category
        )
        
        penalties = Decimal("0.00")
        due_date = date(int(payload.assessment_year), 12, 31)  # Default due date to Dec 31
        
        if payload.include_penalties:
            from app.services.tax.penalty_engine import PenaltyEngine
            pe = PenaltyEngine(repo)
            today = date.today()
            if today > due_date:
                pen_res = await pe.calculate_penalty_on_balance(
                    calc_result["base_tax_amount"],
                    due_date,
                    today
                )
                penalties = pen_res["base_penalty"] + pen_res["interest_accrued"]
                
        total_tax_amount = calc_result["base_tax_amount"] + penalties
        
        return TaxCalculationResponse(
            parcel_id=str(parcel.id),
            parcel_number=parcel.parcel_number,
            assessment_year=payload.assessment_year,
            land_use_category_name=category_name,
            area_sqm=parcel.area_sqm,
            assessed_value=float(calc_result["assessed_value"]),
            tax_rate=float(calc_result["tax_rate_applied"]),
            base_tax_amount=float(calc_result["base_tax_amount"]),
            penalties_amount=float(penalties),
            total_amount=float(total_tax_amount),
            due_date=due_date
        )
    except HTTPException:
        raise
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
    generator: AssessmentGenerator = Depends(get_assessment_generator),
    repo: TaxRepository = Depends(get_tax_repository)
):
    try:
        parcel_repo = ParcelRepository(db)
        parcel = await parcel_repo.get(payload.parcel_id)
        if not parcel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parcel with ID '{payload.parcel_id}' not found."
            )
            
        # Verify assessment doesn't already exist
        existing = await repo.get_by_parcel_and_year(payload.parcel_id, payload.assessment_year)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tax assessment record already exists for parcel '{payload.parcel_id}' and year '{payload.assessment_year}'."
            )
            
        record = await generator.generate_assessment(parcel, int(payload.assessment_year))
        await db.commit()
        await db.refresh(record)
        
        logger.info(f"Tax assessment generated for parcel {payload.parcel_id} year {payload.assessment_year} by user {user_id}")
        return record
    except HTTPException:
        raise
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
    generator: AssessmentGenerator = Depends(get_assessment_generator)
):
    try:
        parish_repo = ParishRepository(db)
        parish = await parish_repo.get(parish_id)
        if not parish:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parish '{parish_id}' not found."
            )
            
        result = await generator.generate_assessments_for_parish(
            UUID(parish_id),
            int(assessment_year)
        )
        await db.commit()
        
        logger.info(f"Batch tax assessments generated for parish {parish_id} year {assessment_year} by user {user_id}")
        return {
            "success": True,
            "message": f"Successfully completed batch assessment generation for parish '{parish_id}' year {assessment_year}.",
            "summary": result
        }
    except HTTPException:
        raise
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
    processor: PaymentProcessor = Depends(get_payment_processor),
    repo: TaxRepository = Depends(get_tax_repository)
):
    try:
        record = await repo.get(payload.tax_record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tax record with ID '{payload.tax_record_id}' not found."
            )
            
        res = await processor.record_payment(
            parcel_id=UUID(record.parcel_id),
            assessment_year=int(record.assessment_year),
            amount_paid=Decimal(str(payload.payment_amount)),
            payment_method=payload.payment_method,
            reference_number=payload.payment_reference,
            payment_date=payload.payment_date,
            received_by=user_id
        )
        
        if not res["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=res.get("error", "Failed to process payment")
            )
            
        # Commit transaction and fetch payment object to return
        await db.commit()
        payment_id = res["payment_id"]
        created_payment = await repo.get_payment(payment_id)
        
        logger.info(f"Tax payment recorded: {payment_id} amount {payload.payment_amount} by user {user_id}")
        return created_payment
    except HTTPException:
        raise
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
    repo: TaxRepository = Depends(get_tax_repository)
):
    try:
        parcel_repo = ParcelRepository(db)
        parcel = await parcel_repo.get(parcel_id)
        if not parcel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parcel with ID '{parcel_id}' not found."
            )
            
        records = await repo.get_all_assessments_for_parcel(parcel_id)
        
        total_outstanding = 0.0
        overdue_amount = 0.0
        upcoming_amount = 0.0
        today = date.today()
        
        for record in records:
            if record.status == "paid":
                continue
                
            total_paid = await repo.get_total_paid_for_assessment(record.id)
            
            # Outstanding = principal + current accrued penalty - total paid
            # Let's check accrued penalties using PenaltyEngine if overdue
            # Since the db columns are updated on payment, we check if penalties_amount needs dynamic updating.
            from app.services.tax.penalty_engine import PenaltyEngine
            pe = PenaltyEngine(repo)
            
            penalty = Decimal("0.00")
            if today > record.due_date:
                remaining_principal = Decimal(str(record.total_amount)) - Decimal(str(total_paid))
                if remaining_principal > 0:
                    pen_res = await pe.calculate_penalty_on_balance(
                        remaining_principal,
                        record.due_date,
                        today
                    )
                    penalty = pen_res["base_penalty"] + pen_res["interest_accrued"]
                    
            outstanding = float(Decimal(str(record.total_amount)) + penalty - Decimal(str(total_paid)))
            if outstanding > 0:
                total_outstanding += outstanding
                if record.due_date < today:
                    overdue_amount += outstanding
                else:
                    upcoming_amount += outstanding
                    
        return OutstandingBalanceResponse(
            parcel_id=str(parcel.id),
            parcel_number=parcel.parcel_number,
            total_outstanding=round(total_outstanding, 2),
            overdue_amount=round(overdue_amount, 2),
            upcoming_amount=round(upcoming_amount, 2),
            records=records
        )
    except HTTPException:
        raise
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
    repo: TaxRepository = Depends(get_tax_repository)
):
    try:
        parcel_repo = ParcelRepository(db)
        parcel = await parcel_repo.get(parcel_id)
        if not parcel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parcel with ID '{parcel_id}' not found."
            )
            
        return await repo.get_payment_history(parcel_id, skip=skip, limit=limit)
    except HTTPException:
        raise
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
    repo: TaxRepository = Depends(get_tax_repository)
):
    try:
        record = await repo.get(record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tax record with ID '{record_id}' not found."
            )
        return record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching tax record: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal database query error: {str(e)}"
        )
