from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from interview_tracker.models.contact import ContactCompany

if TYPE_CHECKING:
    from interview_tracker.models.contact import Contact
    from interview_tracker.models.role import Role


class Company(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  # type: ignore[assignment]
    name: str = Field(index=True, unique=True)
    website: str | None = None
    industry: str | None = None
    status: str = Field(default="active")  # active, inactive, rejected
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    roles: list["Role"] = Relationship(back_populates="company")
    contacts: list["Contact"] = Relationship(
        back_populates="companies", link_model=ContactCompany
    )
