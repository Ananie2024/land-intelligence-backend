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

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: str) -> Optional[ModelType]:
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
        try:
            query = select(self.model).where(self.model.is_active)

            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field) and value is not None:
                        query = query.where(getattr(self.model, field) == value)

            if order_by and hasattr(self.model, order_by):
                order_field = getattr(self.model, order_by)
                query = query.order_by(order_field.desc() if descending else order_field)

            query = query.offset(skip).limit(limit)
            result = await self.db.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error listing {self.model.__name__}: {str(e)}")
            raise

    async def create(self, schema: CreateSchemaType) -> ModelType:
        try:
            if hasattr(schema, 'model_dump'):
                data = schema.model_dump(exclude_none=True)
            else:
                data = {k: v for k, v in schema.__dict__.items() if v is not None}
            instance = self.model(**data)
            self.db.add(instance)
            await self.db.flush()
            return instance
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            await self.db.rollback()
            raise

    async def create_by_dict(self, data: Dict[str, Any]) -> ModelType:
        try:
            instance = self.model(**data)
            self.db.add(instance)
            await self.db.flush()
            return instance
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model.__name__} by dict: {str(e)}")
            await self.db.rollback()
            raise

    async def update(self, id: str, schema: UpdateSchemaType) -> Optional[ModelType]:
        try:
            instance = await self.get(id)
            if not instance:
                return None
            if hasattr(schema, 'model_dump'):
                update_data = schema.model_dump(exclude_none=True)
            else:
                update_data = {k: v for k, v in schema.__dict__.items() if v is not None}
            for field, value in update_data.items():
                if hasattr(instance, field):
                    setattr(instance, field, value)
            await self.db.flush()
            await self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model.__name__} {id}: {str(e)}")
            await self.db.rollback()
            raise

    async def update_by_dict(self, id: str, data: Dict[str, Any]) -> Optional[ModelType]:
        try:
            instance = await self.get(id)
            if not instance:
                return None
            for field, value in data.items():
                if hasattr(instance, field):
                    setattr(instance, field, value)
            await self.db.flush()
            await self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model.__name__} {id} by dict: {str(e)}")
            await self.db.rollback()
            raise

    async def soft_delete(self, id: str) -> bool:
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
        try:
            query = select(func.count()).select_from(self.model).where(
                self.model.is_active
            )
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
            raise