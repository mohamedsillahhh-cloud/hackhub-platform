from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
from sqlalchemy import select, func, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: UUID) -> Optional[ModelType]:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        descending: bool = False,
    ) -> tuple[List[ModelType], int]:
        query = select(self.model)
        count_query = select(func.count(self.model.id))

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    column = getattr(self.model, field)
                    if isinstance(value, list):
                        query = query.where(column.in_(value))
                        count_query = count_query.where(column.in_(value))
                    else:
                        query = query.where(column == value)
                        count_query = count_query.where(column == value)

        if order_by and hasattr(self.model, order_by):
            order_column = getattr(self.model, order_by)
            if descending:
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column)

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, **kwargs) -> ModelType:
        obj = self.model(**kwargs)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, id: UUID, **kwargs) -> Optional[ModelType]:
        obj = await self.get(id)
        if obj is None:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(obj, key):
                setattr(obj, key, value)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, id: UUID) -> bool:
        obj = await self.get(id)
        if obj is None:
            return False
        await self.db.delete(obj)
        await self.db.flush()
        return True
