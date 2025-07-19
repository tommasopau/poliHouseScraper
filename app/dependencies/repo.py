from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.manage_db import get_async_session
from app.db.repositories.base import SQLAlchemyRepository
from app.db.repositories.rental import RentalRepository


def get_rental_repository(
    db: AsyncSession = Depends(get_async_session),
) -> RentalRepository:
    return RentalRepository(db=db)
