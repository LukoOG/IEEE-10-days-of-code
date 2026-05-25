from fastapi import FastAPI, HTTPException
from app.schemas import Note, NoteCreate
from app.storage import notes_db

app = FastAPI(
    title="Notes API",
    description="IEE CS UNILAG 10 days of Code challenge",
    version="1.0.0",
)

@app.get("/")
def home():
    return {"message": "Notes API is running"}


@app.get("/notes", response_model=list[Note])
def get_notes():
    return notes_db

@app.get("/notes/{note_id}", response_model=Note)
def get_note_by_id(note_id: int):
    note = next(
        (note for note in notes_db if note["id"] == note_id),
        None
    )
    
    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )
    return note

@app.post("/notes", response_model=Note, status_code=201)
def create_note(note: NoteCreate):
    new_note = {
        "id": len(notes_db) + 1,
        "title": note.title,
        "content": note.content,
    }
    
    notes_db.append(new_note)
    return new_note

@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, updated_note: NoteCreate):
    note = next(
        (note for note in notes_db if note["id"] == note_id),
        None
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    note["title"] = updated_note.title
    note["content"] = updated_note.content

    return note

@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    note = next(
        (note for note in notes_db if note["id"] == note_id),
        None
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    notes_db.remove(note)

    return {"message": "Note deleted"}


