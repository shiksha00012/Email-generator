from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.database import get_db, EmailHistory
from app.schemas import (
    ComposeRequest, ReplyRequest, ToneConvertRequest, SummarizeRequest,
    EmailResponse, SummaryResponse,
)
from app import gemini_service as ai

router = APIRouter()


def _save(db: Session, type_: str, preview: str, output: str, tone: str = None) -> EmailHistory:
    entry = EmailHistory(
        type=type_,
        prompt_preview=preview[:200],
        output=output,
        tone=tone,
        created_at=datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


# ── POST /api/emails/compose ─────────────────────────────────────
@router.post("/compose", response_model=EmailResponse, summary="Generate a new email")
async def compose(req: ComposeRequest, db: Session = Depends(get_db)):
    """
    Generate a professional email from a purpose, optional recipient,
    optional context, and a tone selection.
    """
    output = ai.compose_email(req.purpose, req.recipient, req.context, req.tone)
    entry = _save(db, "compose", req.purpose, output, req.tone.value)
    return EmailResponse(id=entry.id, type=entry.type, output=output,
                         created_at=entry.created_at)


# ── POST /api/emails/reply ───────────────────────────────────────
@router.post("/reply", response_model=EmailResponse, summary="Generate a smart reply")
async def reply(req: ReplyRequest, db: Session = Depends(get_db)):
    """
    Paste a received email and get a ready-to-send professional reply.
    Optionally include instructions (e.g. "suggest a different time").
    """
    output = ai.generate_reply(req.email, req.instruction)
    preview = req.email[:100].replace("\n", " ")
    entry = _save(db, "reply", preview, output)
    return EmailResponse(id=entry.id, type=entry.type, output=output,
                         created_at=entry.created_at)


# ── POST /api/emails/convert-tone ───────────────────────────────
@router.post("/convert-tone", response_model=EmailResponse, summary="Convert email tone")
async def convert_tone(req: ToneConvertRequest, db: Session = Depends(get_db)):
    """
    Rewrite an email in a different tone: formal, professional, friendly, or concise.
    """
    output = ai.convert_tone(req.email, req.target_tone)
    preview = req.email[:100].replace("\n", " ")
    entry = _save(db, "tone", preview, output, req.target_tone.value)
    return EmailResponse(id=entry.id, type=entry.type, output=output,
                         created_at=entry.created_at)


# ── POST /api/emails/summarize ───────────────────────────────────
@router.post("/summarize", response_model=SummaryResponse, summary="Summarize an email thread")
async def summarize(req: SummarizeRequest, db: Session = Depends(get_db)):
    """
    Paste a long email thread and receive structured key points,
    action items, and deadlines.
    """
    result = ai.summarize_thread(req.thread)
    preview = req.thread[:100].replace("\n", " ")
    entry = _save(db, "summary", preview, json.dumps(result))
    return SummaryResponse(
        id=entry.id,
        key_points=result.get("key_points", []),
        action_items=result.get("action_items", []),
        deadlines=result.get("deadlines", []),
        created_at=entry.created_at,
    )
