from fastapi import APIRouter, Depends
from ..db import init_pool
from ..crud import admin_event_stats

router = APIRouter(prefix="/admin", tags=["admin"])

async def get_pool():
    return await init_pool()

@router.get("/analytics", response_model=list)
async def analytics(pool = Depends(get_pool)):
    rows = await admin_event_stats(pool)
    return rows
