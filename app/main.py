import uvicorn
from fastapi import FastAPI
from .routes import events, bookings, admin, users
from .db import init_pool, close_pool, init_db_from_migration
from .config import settings

app = FastAPI(title='Evently')

app.include_router(events.router)
app.include_router(bookings.router)
app.include_router(admin.router)
app.include_router(users.router)

@app.on_event('startup')
async def on_startup():
    await init_pool()
    # initialize DB schema if requested (INIT_DB=true)
    await init_db_from_migration()

@app.on_event('shutdown')
async def on_shutdown():
    await close_pool()

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
