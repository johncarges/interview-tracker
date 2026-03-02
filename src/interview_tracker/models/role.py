from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from interview_tracker.models.application import Application
    from interview_tracker.models.company import Company


class Role(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  # type: ignore[assignment]
    company_id: int = Field(foreign_key="company.id")
    title: str
    url: str | None = None
    description: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    status: str = Field(default="open")  # open, closed, filled
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    company: Optional["Company"] = Relationship(back_populates="roles")
    applications: list["Application"] = Relationship(back_populates="role")
