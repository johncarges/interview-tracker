from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from interview_tracker.models.contact import Contact, ContactCompany
from interview_tracker.models.contact_role import ContactRole
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
            self.session.exec(
                select(Contact)
                .join(ContactCompany, ContactCompany.contact_id == Contact.id)  # type: ignore[arg-type]
                .where(ContactCompany.company_id == company_id)
            ).all()
        )

    def add_to_company(self, contact_id: int, company_id: int) -> None:
        existing = self.session.get(ContactCompany, (contact_id, company_id))
        if not existing:
            self.session.add(ContactCompany(contact_id=contact_id, company_id=company_id))
            self.session.commit()

    def remove_from_company(self, contact_id: int, company_id: int) -> None:
        link = self.session.get(ContactCompany, (contact_id, company_id))
        if link:
            self.session.delete(link)
            self.session.commit()

    def list_by_role(self, role_id: int) -> list[Contact]:
        return list(
            self.session.exec(
                select(Contact)
                .join(ContactRole, ContactRole.contact_id == Contact.id)  # type: ignore[arg-type]
                .where(ContactRole.role_id == role_id)
            ).all()
        )

    def add_to_role(self, contact_id: int, role_id: int) -> None:
        existing = self.session.get(ContactRole, (contact_id, role_id))
        if not existing:
            self.session.add(ContactRole(contact_id=contact_id, role_id=role_id))
            self.session.commit()

    def remove_from_role(self, contact_id: int, role_id: int) -> None:
        link = self.session.get(ContactRole, (contact_id, role_id))
        if link:
            self.session.delete(link)
            self.session.commit()

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
