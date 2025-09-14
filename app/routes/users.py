"""
User routes.

Provides endpoints to create, list, retrieve and delete users.
"""
from fastapi import APIRouter, Depends, HTTPException
from ..db import init_pool
from ..crud import create_user, list_users, delete_user, get_user
from ..schemas import CreateUser, UserOut
from typing import List

router = APIRouter(prefix="/users", tags=["users"])


async def get_pool():
    """
    Dependency that returns the database connection pool.

    Returns:
        asyncpg.Pool: connection pool initialized by init_pool()
    """
    return await init_pool()


@router.post("/", response_model=UserOut)
async def register_user(payload: CreateUser, pool=Depends(get_pool)):
    """
    Register (create) a new user.

    If a user with the same email already exists, the implementation
    will return the existing user record (UniqueViolation is handled in CRUD).

    Args:
        payload (CreateUser): { email, name }
        pool: DB connection pool (injected)

    Returns:
        UserOut: created (or existing) user

    Raises:
        HTTPException(400): if user cannot be created (unexpected)
    """
    row = await create_user(pool, payload.email, payload.name)
    if not row:
        raise HTTPException(status_code=400, detail="Could not create user")
    return row


@router.get("/", response_model=List[UserOut])
async def get_users(pool=Depends(get_pool)):
    """
    List users ordered by creation time descending.

    Args:
        pool: DB connection pool (injected)

    Returns:
        list[UserOut]: list of users
    """
    rows = await list_users(pool)
    return rows


@router.delete("/{user_id}", response_model=UserOut)
async def remove_user(user_id: str, pool=Depends(get_pool)):
    """
    Delete a user by ID.

    Args:
        user_id (str): UUID of the user to delete
        pool: DB connection pool (injected)

    Returns:
        UserOut: deleted user record

    Raises:
        HTTPException(404): if user not found
    """
    row = await delete_user(pool, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return row


@router.get("/{user_id}", response_model=UserOut)
async def read_user(user_id: str, pool=Depends(get_pool)):
    """
    Retrieve a single user by ID.

    Args:
        user_id (str): UUID of the user
        pool: DB connection pool (injected)

    Returns:
        UserOut: user record

    Raises:
        HTTPException(404): if user not found
    """
    row = await get_user(pool, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return row
