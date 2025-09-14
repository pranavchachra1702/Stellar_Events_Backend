"""
Pydantic models (schemas) used for request validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EventCreate(BaseModel):
    """Schema for creating a new event."""
    name: str
    venue: Optional[str]
    description: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    capacity: int = Field(..., ge=0)


class EventOut(BaseModel):
    """Schema for event response (with available seats)."""
    id: str
    name: str
    venue: Optional[str]
    description: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    capacity: int
    seats_available: int


class BookingRequest(BaseModel):
    """Schema for booking tickets."""
    user_id: str
    event_id: str
    quantity: int = Field(..., gt=0)
    idempotency_key: Optional[str] = None


class BookingOut(BaseModel):
    """Schema for booking response."""
    id: str
    user_id: Optional[str]
    event_id: str
    quantity: int
    status: str
    created_at: datetime


class CreateUser(BaseModel):
    """Schema for user creation."""
    email: str
    name: Optional[str] = None


class UserOut(BaseModel):
    """Schema for user response."""
    id: str
    email: str
    name: Optional[str]
    created_at: datetime


class AnalyticsRow(BaseModel):
    """Schema for analytics response row."""
    event_id: str
    name: str
    capacity: int
    total_booked: int
    utilization: Optional[float]
