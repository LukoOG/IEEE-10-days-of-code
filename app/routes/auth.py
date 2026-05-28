from fastapi import (
    APIRouter,
    Depends,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import (
    RegisterSchema,
    LoginSchema
)
from app.services.auth_service import (
    login_user,
    register_user,
    
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
async def register(
    user: RegisterSchema,
    db: AsyncSession = Depends(get_db)
):
    return await register_user(db, user)


@router.post("/login")
async def login(
    user: LoginSchema,
    db: AsyncSession = Depends(get_db)
):
    return await login_user(db, user)


@router.post("/refresh")
async def refresh_token():
    pass