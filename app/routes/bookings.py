"""
Bookings routes.

Endpoints for:
- creating bookings (with optional idempotency support),
- cancelling bookings, and
- listing bookings for a user.
"""
from fastapi import APIRouter, Depends, Header, HTTPException
from ..schemas import BookingRequest, BookingOut
from ..db import init_pool
from ..crud import book_tickets, cancel_booking, get_user_bookings
from typing import Optional

router = APIRouter(prefix="/bookings", tags=["bookings"])


async def get_pool():
    """
    Dependency to return the database connection pool.

    Returns:
        asyncpg.Pool: DB connection pool from init_pool()
    """
    return await init_pool()


@router.post("/", response_model=dict)
async def create_booking(payload: BookingRequest,
                         idempotency_key: Optional[str] = Header(None),
                         pool = Depends(get_pool)):
    """
    Create a booking for a user.

    Idempotency:
        This endpoint accepts an idempotency key either in the request body
        (payload.idempotency_key) or as an `Idempotency-Key` header. If provided,
        repeated requests with the same key will return the same booking instead
        of creating duplicates.

    Args:
        payload (BookingRequest): booking payload (user_id, event_id, quantity, optional idempotency_key)
        idempotency_key (Optional[str]): idempotency key passed via header (if any)
        pool: DB connection pool (injected)

    Returns:
        dict: { "id": <booking_id>, "status": "CONFIRMED" } or reused response from idempotency.

    Raises:
        HTTPException(409): if not enough seats available.
        HTTPException(400): for other errors.
    """
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
    """
    Cancel a booking.

    Only bookings in CONFIRMED state may be cancelled. The underlying
    CRUD function will update inventory and append a booking event.

    Args:
        booking_id (str): UUID of the booking to cancel
        pool: DB connection pool (injected)

    Returns:
        dict: confirmation including cancelled quantity and booking id.

    Raises:
        HTTPException(400): if booking cannot be cancelled (invalid state).
        HTTPException(500): for unexpected errors.
    """
    try:
        res = await cancel_booking(pool, booking_id)
        return res
    except Exception as e:
        if str(e) == 'CANNOT_CANCEL':
            raise HTTPException(status_code=400, detail="Cannot cancel booking")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=list[BookingOut])
async def user_bookings(user_id: str, pool = Depends(get_pool)):
    """
    List bookings for a specific user.

    Args:
        user_id (str): UUID of the user
        pool: DB connection pool (injected)

    Returns:
        list[BookingOut]: bookings belonging to the user, ordered by created_at desc.
    """
    rows = await get_user_bookings(pool, user_id)
    return rows
