from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from interview_tracker.models.contact_role import ContactRole

if TYPE_CHECKING:
    from interview_tracker.models.company import Company
    from interview_tracker.models.interview import Interview
    from interview_tracker.models.role import Role


class ContactCompany(SQLModel, table=True):
    contact_id: int | None = Field(default=None, foreign_key="contact.id", primary_key=True)
    company_id: int | None = Field(default=None, foreign_key="company.id", primary_key=True)



class Contact(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  # type: ignore[assignment]
    name: str
    title: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    last_contacted_at: datetime | None = None
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    companies: list["Company"] = Relationship(
        back_populates="contacts", link_model=ContactCompany
    )
    roles: list["Role"] = Relationship(back_populates="contacts", link_model=ContactRole)
    interviews: list["Interview"] = Relationship(back_populates="interviewer")
