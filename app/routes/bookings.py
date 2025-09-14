from fastapi import APIRouter, Depends, Header, HTTPException
from ..schemas import BookingRequest, BookingOut
from ..db import init_pool
from ..crud import book_tickets, cancel_booking, get_user_bookings
from typing import Optional
router = APIRouter(prefix="/bookings", tags=["bookings"])

async def get_pool():
    return await init_pool()

@router.post("/", response_model=dict)
async def create_booking(payload: BookingRequest, idempotency_key: Optional[str] = Header(None), pool = Depends(get_pool)):
    # accept idempotency key either in header or in body
    key = payload.idempotency_key or idempotency_key
    try:
        result = await book_tickets(pool, payload.user_id, payload.event_id, payload.quantity, key)
        return result
    except Exception as e:
        if str(e) == 'NOT_ENOUGH_SEATS':
            raise HTTPException(status_code=409, detail="Not enough seats available")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{booking_id}/cancel", response_model=dict)
async def cancel_booking_endpoint(booking_id: str, pool = Depends(get_pool)):
    try:
        res = await cancel_booking(pool, booking_id)
        return res
    except Exception as e:
        if str(e) == 'CANNOT_CANCEL':
            raise HTTPException(status_code=400, detail="Cannot cancel booking")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}", response_model=list[BookingOut])
async def user_bookings(user_id: str, pool = Depends(get_pool)):
    rows = await get_user_bookings(pool, user_id)
    return rows
