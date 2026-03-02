from datetime import datetime

from pydantic import BaseModel


class ContactCreate(BaseModel):
    company_id: int
    name: str
    title: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    notes: str | None = None


class ContactRead(BaseModel):
    id: int
    company_id: int
    name: str
    title: str | None
    email: str | None
    phone: str | None
    linkedin_url: str | None
    last_contacted_at: datetime | None
    notes: str | None


class ContactUpdate(BaseModel):
    name: str | None = None
    title: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    last_contacted_at: datetime | None = None
    notes: str | None = None
