from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from interview_tracker.models.company import Company
    from interview_tracker.models.interview import Interview


class Contact(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  # type: ignore[assignment]
    company_id: int = Field(foreign_key="company.id")
    name: str
    title: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    last_contacted_at: datetime | None = None
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    company: Optional["Company"] = Relationship(back_populates="contacts")
    interviews: list["Interview"] = Relationship(back_populates="interviewer")
