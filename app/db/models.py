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
    telegram_message_id: int
    sender_id: int
    sender_username: str
    message_date: Optional[datetime]
    telephone: Optional[str] = None
    email: Optional[str] = None
    raw_text: str
    summary: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    property_type: Optional[PropertyType]
    availability_start: Optional[date] = None
    availability_end: Optional[date] = None
    tenant_preference: Optional[TenantPreference]
    num_bedrooms: Optional[int] = None
    num_bathrooms: Optional[int] = None
    flatmates_count: Optional[int] = None


class RentalSearchRequest(SQLModel):
    """
    Request model for rental search with filters and vector search.
    """
    query: Optional[str] = None  # For vector similarity search
    location: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    property_type: Optional[PropertyType] = None
    tenant_preference: Optional[TenantPreference] = None
    limit: int = Field(default=20, le=100)
    offset: int = Field(default=0, ge=0)
