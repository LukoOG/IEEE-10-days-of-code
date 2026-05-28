from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import (
    RegisterSchema,
    LoginSchema
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    hash_password
)

async def register_user(
    db: AsyncSession,
    user_data: RegisterSchema
):
    result = await db.execute(
        select(User).where(
            User.email == user_data.email
        )
    )

    existing_user = (
        result.scalar_one_or_none()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
        email=user_data.email,
        password_hash=hash_password(
            user_data.password
        )
    )

    db.add(new_user)

    await db.commit()

    await db.refresh(new_user)

    return new_user


async def login_user(
    db: AsyncSession,
    user_data: LoginSchema
):
    result = await db.execute(
        select(User).where(
            User.email == user_data.email
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    is_valid_password = (
        verify_password(
            user_data.password,
            user.password_hash
        )
    )

    if not is_valid_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = (
        create_access_token(user.id)
    )

    refresh_token = (
        create_refresh_token(user.id)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

