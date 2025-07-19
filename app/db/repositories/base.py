# app/db/repositories/base.py
from typing import Generic, TypeVar, Type, List, Optional
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4

MODEL = TypeVar("MODEL", bound=SQLModel)


class SQLAlchemyRepository(Generic[MODEL]):
    def __init__(self, db: AsyncSession, model: Type[MODEL]):
        self.db = db
        self.model = model

    async def get_all(self, *, offset: int = 0, limit: int = 100) -> List[MODEL]:
        stmt = select(self.model).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, id: UUID) -> Optional[MODEL]:
        return await self.db.get(self.model, id)

    async def create(self, obj_in: MODEL) -> MODEL:
        self.db.add(obj_in)
        await self.db.commit()
        await self.db.refresh(obj_in)
        return obj_in

    async def update(self, db_obj: MODEL, obj_in: dict) -> MODEL:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: UUID) -> None:
        obj = await self.get_by_id(id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
