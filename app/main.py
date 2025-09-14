"""
FastAPI entrypoint for the Evently backend.

Defines application lifecycle, routes, and health check endpoints.
"""

import uvicorn
from fastapi import FastAPI
from .routes import events, bookings, admin, users
from .db import init_pool, close_pool, init_db_from_migration

app = FastAPI(title='Evently')

# Register API routers
app.include_router(events.router)
app.include_router(bookings.router)
app.include_router(admin.router)
app.include_router(users.router)


@app.get("/")
async def root():
    """
    Root endpoint for Render health check and service information.
    """
    return {"message": "Stellar Events Backend is running"}


@app.get("/healthz")
async def health_check():
    """
    Dedicated health check endpoint to verify service status.
    """
    return {"status": "ok"}


@app.on_event('startup')
async def on_startup():
    """
    Startup hook:
    - Initializes database connection pool.
    - Runs DB migration if INIT_DB is enabled.
    """
    await init_pool()
    await init_db_from_migration()


@app.on_event('shutdown')
async def on_shutdown():
    """
    Shutdown hook:
    - Closes database connection pool.
    """
    await close_pool()


if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
