from datetime import datetime

from pydantic import BaseModel


class InterviewCreate(BaseModel):
    application_id: int
    type: str
    scheduled_at: datetime
    interviewer_id: int | None = None
    notes: str | None = None


class InterviewRead(BaseModel):
    id: int
    application_id: int
    interviewer_id: int | None
    type: str
    scheduled_at: datetime
    completed_at: datetime | None
    outcome: str
    notes: str | None


class InterviewUpdate(BaseModel):
    outcome: str | None = None
    completed_at: datetime | None = None
    notes: str | None = None
