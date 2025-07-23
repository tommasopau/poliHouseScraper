from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from app.db.models import Rental, RentalResponse, RentalSearchRequest, PropertyType, TenantPreference
from app.dependencies.repo import get_rental_repository
from app.db.repositories.rental import RentalRepository
from app.middleware.rate_limiter import limiter


router = APIRouter(prefix="/rentals", tags=["rentals"])


@router.get("/", response_model=List[RentalResponse])
@limiter.limit("100/minute")
async def search_rentals(
    request: Request,
    location: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    property_type: Optional[PropertyType] = Query(None),
    tenant_preference: Optional[TenantPreference] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    repo: RentalRepository = Depends(get_rental_repository),
):
    rentals: List[Rental] = await repo.search(
        location=location,
        min_price=min_price,
        max_price=max_price,
        property_type=property_type,
        tenant_preference=tenant_preference,
        offset=offset,
        limit=limit,
    )

    return [
        RentalResponse(
            id=rental.id,
            telegram_message_id=rental.telegram_message_id,
            sender_id=rental.sender_id,
            sender_username=rental.sender_username,
            raw_text=rental.raw_text,
            message_date=rental.message_date,
            telephone=rental.telephone,
            email=rental.email,
            price=rental.price,
            location=rental.location,
            property_type=rental.property_type,
            tenant_preference=rental.tenant_preference,
            availability_start=rental.availability_start,
            availability_end=rental.availability_end,
            num_bedrooms=rental.num_bedrooms,
            num_bathrooms=rental.num_bathrooms,
            flatmates_count=rental.flatmates_count,
        )
        for rental in rentals
    ]
