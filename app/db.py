"""
Database connection pool and initialization utilities for Evently.
"""

import asyncpg
from pathlib import Path
from .config import settings

_pool = None


async def init_pool():
    """
    Initialize a global asyncpg connection pool.

    Returns:
        asyncpg.pool.Pool: The created connection pool.
    """
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL, min_size=1, max_size=10)
    return _pool


async def close_pool():
    """
    Close the global connection pool and release resources.
    """
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def init_db_from_migration():
    """
    Run the initial migration (001_init.sql) to create the database schema.

    Executes the SQL file only if INIT_DB is set to True in settings.
    """
    if not settings.INIT_DB:
        return
    pool = await init_pool()
    path = Path(__file__).parent.parent / 'migrations' / '001_init.sql'
    sql = path.read_text()
    async with pool.acquire() as conn:
        await conn.execute(sql)
