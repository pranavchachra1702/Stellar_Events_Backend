from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..schemas import EventCreate, EventOut
from ..db import init_pool
from ..crud import list_events, get_event, create_event, update_event, delete_event

router = APIRouter(prefix="/events", tags=["events"])

async def get_pool():
    return await init_pool()

@router.get("/", response_model=List[EventOut])
async def read_events(limit: int = 25, offset: int = 0, pool = Depends(get_pool)):
    rows = await list_events(pool, limit, offset)
    return rows

@router.get("/{event_id}", response_model=EventOut)
async def read_event(event_id: str, pool = Depends(get_pool)):
    row = await get_event(pool, event_id)
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")
    return row

@router.post("/", response_model=EventOut)
async def create_new_event(payload: EventCreate, pool = Depends(get_pool)):
    row = await create_event(pool, payload.model_dump())
    return row

@router.put("/{event_id}", response_model=EventOut)
async def update_existing_event(event_id: str, payload: EventCreate, pool=Depends(get_pool)):
    row = await update_event(pool, event_id, payload.model_dump())
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")
    return row

@router.delete("/{event_id}", response_model=EventOut)
async def remove_event(event_id: str, pool=Depends(get_pool)):
    row = await delete_event(pool, event_id)
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")
    return row