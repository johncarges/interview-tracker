from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from interview_tracker.models.application import Application
    from interview_tracker.models.contact import Contact


class Interview(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  # type: ignore[assignment]
    application_id: int = Field(foreign_key="application.id")
    interviewer_id: int | None = Field(default=None, foreign_key="contact.id")
    type: str  # phone_screen, technical, system_design, behavioral, onsite, take_home
    scheduled_at: datetime
    completed_at: datetime | None = None
    outcome: str = Field(default="pending")  # passed, failed, pending
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    application: Optional["Application"] = Relationship(back_populates="interviews")
    interviewer: Optional["Contact"] = Relationship(back_populates="interviews")
