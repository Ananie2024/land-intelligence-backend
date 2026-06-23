"""
Base Repository
Phase 2 — Section 3.2
Land Intelligence System
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models.base import Base

logger = logging.getLogger(__name__)

# Generic type for SQLAlchemy models
ModelType = TypeVar("ModelType", bound=Base)
# Generic type for Pydantic schemas
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic base repository with async CRUD operations.
    
    Provides standard database operations for any model.
    """
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialize repository with model class and database session.
        
        Args:
            model: SQLAlchemy model class
            db: Async database session
        """
        self.model = model
        self.db = db
    
    async def get(self, id: str) -> Optional[ModelType]:
        """
        Get a single record by UUID.
        
        Args:
            id: UUID of the record
            
        Returns:
            Model instance if found, None otherwise
        """
        try:
            result = await self.db.execute(
                select(self.model).where(
                    self.model.id == id,
                    self.model.is_active
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by id {id}: {str(e)}")
            raise
    
    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        descending: bool = False
    ) -> List[ModelType]:
        """
        List records with optional filters.
        
        Args:
            filters: Dictionary of field:value filters
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            order_by: Field name to order by
            descending: Whether to order descending
            
        Returns:
            List of model instances
        """
        try:
            query = select(self.model).where(self.model.is_active)
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field) and value is not None:
                        query = query.where(getattr(self.model, field) == value)
            
            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                order_field = getattr(self.model, order_by)
                if descending:
                    query = query.order_by(order_field.desc())
                else:
                    query = query.order_by(order_field)
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error listing {self.model.__name__}: {str(e)}")
            raise
    
    async def create(self, schema: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        
        Args:
            schema: Pydantic schema with creation data
            
        Returns:
            Created model instance
        """
        try:
            # Convert schema to dict, excluding None values
            if hasattr(schema, 'model_dump'):
                data = schema.model_dump(exclude_none=True)
            else:
                data = {k: v for k, v in schema.__dict__.items() if v is not None}
            
            # Create model instance
            instance = self.model(**data)
            
            # Add to database
            self.db.add(instance)
            await self.db.flush()
            
            return instance
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            await self.db.rollback()
            raise
    
    async def update(self, id: str, schema: UpdateSchemaType) -> Optional[ModelType]:
        """
        Update an existing record.
        
        Args:
            id: UUID of the record to update
            schema: Pydantic schema with update data
            
        Returns:
            Updated model instance if found, None otherwise
        """
        try:
            # Get existing record
            instance = await self.get(id)
            if not instance:
                return None
            
            # Update fields
            if hasattr(schema, 'model_dump'):
                update_data = schema.model_dump(exclude_none=True)
            else:
                update_data = {k: v for k, v in schema.__dict__.items() if v is not None}
            
            for field, value in update_data.items():
                if hasattr(instance, field):
                    setattr(instance, field, value)
            
            # Flush changes
            await self.db.flush()
            await self.db.refresh(instance)
            
            return instance
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model.__name__} {id}: {str(e)}")
            await self.db.rollback()
            raise
    
    async def soft_delete(self, id: str) -> bool:
        """
        Soft delete a record (set is_active=False).
        
        Args:
            id: UUID of the record to delete
            
        Returns:
            True if record was deleted, False if not found
        """
        try:
            instance = await self.get(id)
            if not instance:
                return False
            
            instance.is_active = False
            await self.db.flush()
            
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error soft deleting {self.model.__name__} {id}: {str(e)}")
            await self.db.rollback()
            raise
    
    async def hard_delete(self, id: str) -> bool:
        """
        Permanently delete a record (for testing/cleanup only).
        
        Args:
            id: UUID of the record to delete
            
        Returns:
            True if record was deleted, False if not found
        """
        try:
            instance = await self.get(id)
            if not instance:
                return False
            
            await self.db.delete(instance)
            await self.db.flush()
            
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error hard deleting {self.model.__name__} {id}: {str(e)}")
            await self.db.rollback()
            raise
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filters.
        
        Args:
            filters: Dictionary of field:value filters
            
        Returns:
            Total count of active records matching filters
        """
        try:
            query = select(func.count()).select_from(self.model).where(
                self.model.is_active
            )
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field) and value is not None:
                        query = query.where(getattr(self.model, field) == value)
            
            result = await self.db.execute(query)
            return result.scalar_one()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            raise
    
    async def exists(self, id: str) -> bool:
        """
        Check if a record exists.
        
        Args:
            id: UUID of the record
            
        Returns:
            True if record exists and is active, False otherwise
        """
        try:
            result = await self.db.execute(
                select(func.count()).select_from(self.model).where(
                    self.model.id == id,
                    self.model.is_active
                )
            )
            return result.scalar_one() > 0
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__} {id}: {str(e)}")
            raise# app/repositories/base_repository.py
