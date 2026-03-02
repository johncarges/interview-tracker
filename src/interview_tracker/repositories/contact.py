from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from interview_tracker.models.contact import Contact
from interview_tracker.repositories.base import AbstractRepository
from interview_tracker.schemas.contact import ContactCreate, ContactUpdate


class ContactRepository(AbstractRepository[Contact]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id(self, id: int) -> Contact | None:
        return self.session.get(Contact, id)

    def list_all(self) -> list[Contact]:
        return list(self.session.exec(select(Contact)).all())

    def list_by_company(self, company_id: int) -> list[Contact]:
        return list(
            self.session.exec(select(Contact).where(Contact.company_id == company_id)).all()
        )

    def list_needing_followup(self, days: int) -> list[Contact]:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        return list(
            self.session.exec(
                select(Contact).where(
                    (Contact.last_contacted_at == None) | (Contact.last_contacted_at < cutoff)  # noqa: E711  # type: ignore[operator]
                )
            ).all()
        )

    def create(self, data: ContactCreate) -> Contact:
        contact = Contact(**data.model_dump())
        self.session.add(contact)
        self.session.commit()
        self.session.refresh(contact)
        return contact

    def update(self, contact: Contact, data: ContactUpdate) -> Contact:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(contact, field, value)
        contact.updated_at = datetime.now(UTC)
        self.session.add(contact)
        self.session.commit()
        self.session.refresh(contact)
        return contact

    def delete(self, contact: Contact) -> None:
        self.session.delete(contact)
        self.session.commit()
