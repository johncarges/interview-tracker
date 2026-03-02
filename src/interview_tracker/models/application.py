from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from interview_tracker.models.interview import Interview
    from interview_tracker.models.role import Role


class Application(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  # type: ignore[assignment]
    role_id: int = Field(foreign_key="role.id")
    # applied, screening, interviewing, offer, rejected, withdrawn
    status: str = Field(default="applied")
    applied_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    role: Optional["Role"] = Relationship(back_populates="applications")
    interviews: list["Interview"] = Relationship(back_populates="application")
