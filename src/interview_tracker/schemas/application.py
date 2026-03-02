from datetime import datetime

from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    role_id: int
    notes: str | None = None


class ApplicationRead(BaseModel):
    id: int
    role_id: int
    status: str
    applied_at: datetime
    notes: str | None


class ApplicationReadFull(BaseModel):
    id: int
    role_id: int
    status: str
    applied_at: datetime
    notes: str | None
    role_title: str
    company_name: str


class ApplicationUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
