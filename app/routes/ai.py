from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db        
from app.models.note import Note             
from app.services import groq_service

router = APIRouter(prefix="/notes", tags=["AI"])


# ---------------------------------------------------------------------------
# POST /notes/{note_id}/summary
# Main Task: Groq Integration + Caching + Error Handling
# ---------------------------------------------------------------------------

@router.post("/{note_id}/summary", status_code=status.HTTP_200_OK)
def summarize_note(note_id: int, db: Session = Depends(get_db)):
    """
    Return an AI-generated summary of a note.
    The summary is cached in the database after first generation.
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # --- Caching: return stored summary if it already exists ---
    if note.ai_summary:
        return {
            "note_id": note_id,
            "summary": note.ai_summary,
            "cached": True,
        }

    # --- Call Groq with graceful error handling ---
    try:
        summary = groq_service.generate_summary(note.content)
    except EnvironmentError as e:
        # Missing API key — server misconfiguration
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server configuration error: {e}",
        )
    except ValueError as e:
        # 4xx from Groq (bad request, invalid key, etc.)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service rejected the request: {e}",
        )
    except RuntimeError as e:
        # All retries exhausted (timeouts, rate limits, 5xx)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service is temporarily unavailable. Please try again later.",
        )
    except Exception as e:
        # Catch-all — don't crash the server
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the summary.",
        )

    # --- Persist summary to DB (cache it) ---
    note.ai_summary = summary
    db.commit()
    db.refresh(note)

    return {
        "note_id": note_id,
        "summary": summary,
        "cached": False,
    }


# ---------------------------------------------------------------------------
# POST /notes/{note_id}/tags  (Bonus: Auto-Tagging)
# ---------------------------------------------------------------------------

@router.post("/{note_id}/tags", status_code=status.HTTP_200_OK)
def tag_note(note_id: int, db: Session = Depends(get_db)):
    """
    Return AI-suggested tags for a note.
    Tags are cached in the database after first generation.
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # --- Caching ---
    if note.ai_tags:
        return {
            "note_id": note_id,
            "tags": note.ai_tags,
            "cached": True,
        }

    # --- Call Groq ---
    try:
        tags = groq_service.generate_tags(note.content)
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=f"Server configuration error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=502, detail=f"AI service rejected the request: {e}")
    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail="AI service is temporarily unavailable. Please try again later.",
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error generating tags.")

    # --- Persist ---
    note.ai_tags = tags
    db.commit()
    db.refresh(note)

    return {
        "note_id": note_id,
        "tags": tags,
        "cached": False,
    }


# ---------------------------------------------------------------------------
# DELETE /notes/{note_id}/summary  — clear cached summary (force regeneration)
# ---------------------------------------------------------------------------

@router.delete("/{note_id}/summary", status_code=status.HTTP_200_OK)
def clear_summary_cache(note_id: int, db: Session = Depends(get_db)):
    """Clear the cached AI summary so it will be regenerated on next request."""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note.ai_summary = None
    db.commit()
    return {"message": "Summary cache cleared. Next request will regenerate."}