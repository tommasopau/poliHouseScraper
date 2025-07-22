# app/db/repositories/rental.py
from typing import List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Rental, TenantPreference, PropertyType
from app.db.repositories.base import SQLAlchemyRepository


class RentalRepository(SQLAlchemyRepository[Rental]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Rental)

    async def find_by_location(
        self, location: str, offset: int = 0, limit: int = 20
    ) -> List[Rental]:
        stmt = (
            select(Rental)
            .where(Rental.location == location)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_by_price_range(
        self, min_price: float, max_price: float, offset: int = 0, limit: int = 20
    ) -> List[Rental]:
        stmt = (
            select(Rental)
            .where(Rental.price >= min_price, Rental.price <= max_price)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_by_telegram_id(self, telegram_message_id: int) -> Optional[Rental]:
        """Find rental by Telegram message ID to check for duplicates."""
        stmt = select(Rental).where(
            Rental.telegram_message_id == telegram_message_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def search(
        self,
        location: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        property_type: Optional[PropertyType] = None,
        tenant_preference: Optional[TenantPreference] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> List[Rental]:
        stmt = select(Rental)
        filters = []
        if location:
            filters.append(Rental.location == location)
        if min_price is not None:
            filters.append(Rental.price >= min_price)
        if max_price is not None:
            filters.append(Rental.price <= max_price)
        if property_type:
            filters.append(Rental.property_type == property_type)
        if filters:
            stmt = stmt.where(*filters)
        if tenant_preference:
            stmt = stmt.where(Rental.tenant_preference == tenant_preference)
        stmt = stmt.order_by(Rental.message_date.desc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
