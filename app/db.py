import asyncpg
import asyncio
import os
from pathlib import Path
import json
from .config import settings

_pool = None

async def init_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL, min_size=1, max_size=10)
    return _pool

async def close_pool():
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None

async def init_db_from_migration():
    """Run migrations/001_init.sql to create initial schema."""
    if not settings.INIT_DB:
        return
    pool = await init_pool()
    path = Path(__file__).parent.parent / 'migrations' / '001_init.sql'
    sql = path.read_text()
    async with pool.acquire() as conn:
        # asyncpg supports executing multi-statement SQL
        await conn.execute(sql)
