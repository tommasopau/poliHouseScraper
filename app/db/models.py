"""
SQLModel database models - Simplified approach.
"""
from datetime import datetime, date
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from enum import Enum

from sqlmodel import SQLModel, Field, BigInteger

from app.core.config import settings


class PropertyType(str, Enum):
    camera_singola = "camera_singola"
    camera_doppia = "camera_doppia"
    appartamento = "appartamento"
    monolocale = "monolocale"


class TenantPreference(str, Enum):
    ragazzo = "ragazzo"
    ragazza = "ragazza"
    indifferente = "indifferente"


class Rental(SQLModel, table=True):
    """
    Rental property model - Pure SQLModel approach.
    """
    __tablename__ = "rentals"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Raw Telegram data (all indexed for fast queries)
    telegram_message_id: Optional[int] = Field(
        default=None, index=True, sa_type=BigInteger)
    sender_id: Optional[int] = Field(
        default=None, index=True, sa_type=BigInteger)
    sender_username: Optional[str] = Field(default=None, index=True)
    message_date: Optional[datetime] = Field(default=None, index=True)
    telephone: Optional[str] = Field(default=None, index=True)
    email: Optional[str] = Field(default=None, index=True)

    # Message content
    raw_text: str
    summary: Optional[str] = None

    # Core rental attributes (indexed for filtering)
    price: Optional[float] = Field(default=None, index=True)
    has_extra_expenses: Optional[bool] = Field(
        default=None, description="True if extra expenses are mentioned")
    extra_expenses_details: Optional[str] = Field(
        default=None, description="Details of extra expenses, if any")
    location: Optional[str] = Field(default=None, index=True)
    property_type: Optional[PropertyType] = Field(default=None, index=True)

    # Availability dates
    availability_start: Optional[date] = Field(default=None, index=True)
    availability_end: Optional[date] = Field(default=None, index=True)

    # Preferences and counts
    tenant_preference: Optional[TenantPreference] = Field(
        default=None, index=True)
    num_bedrooms: Optional[int] = Field(default=None, index=True)
    num_bathrooms: Optional[int] = Field(default=None, index=True)
    flatmates_count: Optional[int] = Field(default=None, index=True)


class TelegramMessageData(SQLModel):
    """
    Pydantic model for Telegram message data from client.
    """
    id: int
    text: str
    date: datetime
    sender_id: Optional[int] = None
    sender_username: Optional[str] = None
    has_media: bool = False


class RentalResponse(SQLModel):
    """
    Response model for rental API endpoints.
    """
    id: UUID
    telegram_message_id: Optional[int] = None
    sender_id: Optional[int] = None
    sender_username: Optional[str] = None
    message_date: Optional[datetime]
    telephone: Optional[str] = None
    email: Optional[str] = None
    raw_text: str
    summary: Optional[str] = None
    price: Optional[float] = None
    has_extra_expenses: Optional[bool] = None
    extra_expenses_details: Optional[str] = None
    location: Optional[str] = None
    property_type: Optional[PropertyType]
    availability_start: Optional[date] = None
    availability_end: Optional[date]
