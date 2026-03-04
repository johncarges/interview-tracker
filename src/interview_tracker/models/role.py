from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from interview_tracker.models.contact_role import ContactRole
from interview_tracker.models.technology import RoleTechnology

if TYPE_CHECKING:
    from interview_tracker.models.application import Application
    from interview_tracker.models.company import Company
    from interview_tracker.models.contact import Contact
    from interview_tracker.models.technology import Technology


class Role(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  # type: ignore[assignment]
    company_id: int = Field(foreign_key="company.id")
    title: str
    url: str | None = None
    description: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    status: str = Field(default="open")  # open, closed, filled
    office_days_per_week: int | None = None  # 0=remote, 1-4=hybrid, 5=onsite
    min_experience_years: int | None = None
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    company: Optional["Company"] = Relationship(back_populates="roles")
    applications: list["Application"] = Relationship(back_populates="role")
    contacts: list["Contact"] = Relationship(back_populates="roles", link_model=ContactRole)
    technologies: list["Technology"] = Relationship(
        back_populates="roles", link_model=RoleTechnology
    )
