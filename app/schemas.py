from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ToneEnum(str, Enum):
    formal = "formal"
    professional = "professional"
    friendly = "friendly"
    concise = "concise"


# ── Request models ──────────────────────────────────────────────

class ComposeRequest(BaseModel):
    purpose: str = Field(..., min_length=5, max_length=500,
                         example="Request 3 days leave for a family event")
    recipient: Optional[str] = Field(None, max_length=100,
                                      example="My manager, Priya")
    context: Optional[str] = Field(None, max_length=300,
                                    example="Dates: June 20–22")
    tone: ToneEnum = ToneEnum.professional


class ReplyRequest(BaseModel):
    email: str = Field(..., min_length=10, max_length=3000,
                       example="Hi, can we schedule a meeting tomorrow at 2 PM?")
    instruction: Optional[str] = Field(None, max_length=200,
                                        example="Confirm but suggest 3 PM instead")


class ToneConvertRequest(BaseModel):
    email: str = Field(..., min_length=10, max_length=3000,
                       example="hey just wanted to know if u got my report thx")
    target_tone: ToneEnum = ToneEnum.professional


class SummarizeRequest(BaseModel):
    thread: str = Field(..., min_length=20, max_length=5000,
                        example="Long email thread goes here...")


# ── Response models ─────────────────────────────────────────────

class EmailResponse(BaseModel):
    id: int
    type: str
    output: str
    created_at: datetime

    class Config:
        from_attributes = True


class SummaryResponse(BaseModel):
    id: int
    key_points: List[str]
    action_items: List[str]
    deadlines: List[str]
    created_at: datetime


class HistoryItem(BaseModel):
    id: int
    type: str
    prompt_preview: str
    tone: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class HistoryDetailResponse(BaseModel):
    id: int
    type: str
    prompt_preview: str
    output: str
    tone: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
