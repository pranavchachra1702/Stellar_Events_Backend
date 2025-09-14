from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class EventCreate(BaseModel):
    name: str
    venue: Optional[str]
    description: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    capacity: int = Field(..., ge=0)

class EventOut(BaseModel):
    id: str
    name: str
    venue: Optional[str]
    description: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    capacity: int
    seats_available: int

class BookingRequest(BaseModel):
    user_id: str
    event_id: str
    quantity: int = Field(..., gt=0)
    idempotency_key: Optional[str] = None

class BookingOut(BaseModel):
    id: str
    user_id: Optional[str]
    event_id: str
    quantity: int
    status: str
    created_at: datetime

class CreateUser(BaseModel):
    email: str
    name: Optional[str] = None

class UserOut(BaseModel):
    id: str
    email: str
    name: Optional[str]
    created_at: datetime

class AnalyticsRow(BaseModel):
    event_id: str
    name: str
    capacity: int
    total_booked: int
    utilization: Optional[float]
