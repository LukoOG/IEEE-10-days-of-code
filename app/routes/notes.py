from fastapi import (
    APIRouter,
    Depends,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.note import (
    NoteCreate,
    NoteResponse,
    NoteUpdate
)
from app.core.database import get_db
from app.dependencies.auth import (
    get_current_user
)
from app.models.user import User
from app.services.note_service import (
    create_note,
    get_notes,
    get_note_by_id,
    update_note,
    delete_note
)

router = APIRouter(
    prefix="/notes",
    tags=["Notes"]
)


@router.get(
    "/",
    response_model=list[NoteResponse]
)
async def get_user_notes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    return await get_notes(
        db,
        current_user.id
    )


@router.get(
    "/{note_id}",
    response_model=NoteResponse
)
async def get_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    return await get_note_by_id(
        db,
        note_id,
        current_user.id
    )


@router.post(
    "/",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_new_note(
    note: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    return await create_note(
        db,
        note,
        current_user.id
    )


@router.put(
    "/{note_id}",
    response_model=NoteResponse
)
async def update_existing_note(
    note_id: int,
    note: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    return await update_note(
        db,
        note_id,
        note,
        current_user.id
    )


@router.delete("/{note_id}")
async def remove_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    return await delete_note(
        db,
        note_id,
        current_user.id
    )