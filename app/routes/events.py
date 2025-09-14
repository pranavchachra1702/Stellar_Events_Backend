"""
Event routes.

CRUD endpoints for events:
- list events
- get a single event
- create an event
- update an event
- delete an event
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..schemas import EventCreate, EventOut
from ..db import init_pool
from ..crud import list_events, get_event, create_event, update_event, delete_event

router = APIRouter(prefix="/events", tags=["events"])


async def get_pool():
    """
    Dependency to provide database connection pool.

    Returns:
        asyncpg.Pool: the pool created by init_pool()
    """
    return await init_pool()


@router.get("/", response_model=List[EventOut])
async def read_events(limit: int = 25, offset: int = 0, pool = Depends(get_pool)):
    """
    List events with pagination.

    Args:
        limit (int): maximum number of events to return (default 25)
        offset (int): offset for pagination (default 0)
        pool: DB connection pool (injected)

    Returns:
        list[EventOut]: list of events with availability information
    """
    rows = await list_events(pool, limit, offset)
    return rows


@router.get("/{event_id}", response_model=EventOut)
async def read_event(event_id: str, pool = Depends(get_pool)):
    """
    Get a single event by ID.

    Args:
        event_id (str): UUID of the event
        pool: DB connection pool (injected)

    Returns:
        EventOut: event details including seats_available

    Raises:
        HTTPException(404): if event not found
    """
    row = await get_event(pool, event_id)
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")
    return row


@router.post("/", response_model=EventOut)
async def create_new_event(payload: EventCreate, pool = Depends(get_pool)):
    """
    Create a new event.

    Args:
        payload (EventCreate): event creation payload
        pool: DB connection pool (injected)

    Returns:
        EventOut: newly created event record (includes seats_available)
    """
    row = await create_event(pool, payload.model_dump())
    return row


@router.put("/{event_id}", response_model=EventOut)
async def update_existing_event(event_id: str, payload: EventCreate, pool=Depends(get_pool)):
    """
    Update an existing event.

    Args:
        event_id (str): UUID of the event to update
        payload (EventCreate): event payload with new values
        pool: DB connection pool (injected)

    Returns:
        EventOut: updated event

    Raises:
        HTTPException(404): if event not found
    """
    row = await update_event(pool, event_id, payload.model_dump())
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")
    return row


@router.delete("/{event_id}", response_model=EventOut)
async def remove_event(event_id: str, pool=Depends(get_pool)):
    """
    Delete an event and its inventory.

    Args:
        event_id (str): UUID of the event to delete
        pool: DB connection pool (injected)

    Returns:
        EventOut: deleted event record

    Raises:
        HTTPException(404): if event not found
    """
    row = await delete_event(pool, event_id)
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")
    return row
