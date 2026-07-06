from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from app.database import get_db, EmailHistory
from app.schemas import HistoryItem, HistoryDetailResponse, SummaryResponse

router = APIRouter()


# ── GET /api/history ─────────────────────────────────────────────
@router.get("/", response_model=List[HistoryItem], summary="List all saved emails")
async def list_history(
    limit: int = 20,
    offset: int = 0,
    type_filter: str = None,
    db: Session = Depends(get_db),
):
    """
    Return a paginated list of saved emails (newest first).
    Filter by type: compose | reply | tone | summary
    """
    query = db.query(EmailHistory).order_by(EmailHistory.created_at.desc())
    if type_filter:
        query = query.filter(EmailHistory.type == type_filter)
    records = query.offset(offset).limit(limit).all()
    return [
        HistoryItem(
            id=r.id,
            type=r.type,
            prompt_preview=r.prompt_preview,
            tone=r.tone,
            created_at=r.created_at,
        )
        for r in records
    ]


# ── GET /api/history/{id} ────────────────────────────────────────
@router.get("/{email_id}", response_model=HistoryDetailResponse,
            summary="Get a saved email by ID")
async def get_email(email_id: int, db: Session = Depends(get_db)):
    record = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Email with id={email_id} not found.")
    return HistoryDetailResponse(
        id=record.id,
        type=record.type,
        prompt_preview=record.prompt_preview,
        output=record.output,
        tone=record.tone,
        created_at=record.created_at,
    )


# ── DELETE /api/history/{id} ─────────────────────────────────────
@router.delete("/{email_id}", summary="Delete a saved email")
async def delete_email(email_id: int, db: Session = Depends(get_db)):
    record = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Email with id={email_id} not found.")
    db.delete(record)
    db.commit()
    return {"message": f"Email {email_id} deleted successfully."}


# ── DELETE /api/history/ ─────────────────────────────────────────
@router.delete("/", summary="Clear all history")
async def clear_history(db: Session = Depends(get_db)):
    deleted = db.query(EmailHistory).delete()
    db.commit()
    return {"message": f"Deleted {deleted} record(s)."}
