from fastapi import APIRouter, Depends, HTTPException
from ..db import init_pool
from ..crud import create_user, list_users, delete_user, get_user
from ..schemas import CreateUser, UserOut
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

async def get_pool():
    return await init_pool()

@router.post("/", response_model=UserOut)
async def register_user(payload: CreateUser, pool=Depends(get_pool)):
    row = await create_user(pool, payload.email, payload.name)
    if not row:
        raise HTTPException(status_code=400, detail="Could not create user")
    return row

@router.get("/", response_model=List[UserOut])
async def get_users(pool=Depends(get_pool)):
    rows = await list_users(pool)
    return rows

@router.delete("/{user_id}", response_model=UserOut)
async def remove_user(user_id: str, pool=Depends(get_pool)):
    row = await delete_user(pool, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return row

@router.get("/{user_id}", response_model=UserOut)
async def read_user(user_id: str, pool=Depends(get_pool)):
    row = await get_user(pool, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return row