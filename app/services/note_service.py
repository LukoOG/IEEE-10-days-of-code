from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note
from app.schemas.note import (
    NoteCreate,
    NoteUpdate
)


async def get_notes(
    db: AsyncSession,
    user_id: int
):
    result = await db.execute(
        select(Note).where(
            Note.owner_id == user_id
        )
    )

    return result.scalars().all()


async def get_note_by_id(
    db: AsyncSession,
    note_id: int,
    user_id: int
):
    result = await db.execute(
        select(Note).where(
            Note.id == note_id,
            Note.owner_id == user_id
        )
    )

    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return note


async def create_note(
    db: AsyncSession,
    note_data: NoteCreate,
    user_id: int
):
    new_note = Note(
        **note_data.model_dump(),
        owner_id=user_id
    )

    db.add(new_note)

    await db.commit()
    await db.refresh(new_note)

    return new_note


async def update_note(
    db: AsyncSession,
    note_id: int,
    note_data: NoteUpdate,
    user_id: int
):
    note = await get_note_by_id(
        db=db,
        note_id=note_id,
        user_id=user_id
    )

    update_data = note_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(note, key, value)

    await db.commit()
    await db.refresh(note)

    return note


async def delete_note(
    db: AsyncSession,
    note_id: int,
    user_id: int
):
    note = await get_note_by_id(
        db=db,
        note_id=note_id,
        user_id=user_id
    )

    await db.delete(note)
    await db.commit()

    return {
        "message": "Note deleted successfully"
    }