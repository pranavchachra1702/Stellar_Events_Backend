"""
Admin routes.

Contains endpoints used for administrative/analytics purposes.
"""
from fastapi import APIRouter, Depends
from ..db import init_pool
from ..crud import admin_event_stats

router = APIRouter(prefix="/admin", tags=["admin"])


async def get_pool():
    """
    Dependency that returns a database connection pool.

    Returns:
        asyncpg.Pool: a connection pool created by init_pool().
    """
    return await init_pool()


@router.get("/analytics", response_model=list)
async def analytics(pool = Depends(get_pool)):
    """
    Return analytics rows about events (booking counts, utilization, etc).

    This endpoint delegates to the `admin_event_stats` CRUD function which
    reads from a materialized view in the database.

    Args:
        pool: database connection pool (injected by Depends).

    Returns:
        list: list of analytics rows (dictionaries) - schema is defined in the DB/view.
    """
    rows = await admin_event_stats(pool)
    return rows
