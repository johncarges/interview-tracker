from datetime import UTC, datetime

from sqlmodel import Session

from interview_tracker.repositories.contact import ContactRepository
from interview_tracker.schemas.contact import ContactCreate, ContactRead, ContactUpdate


class ContactService:
    def __init__(self, session: Session) -> None:
        self.repo = ContactRepository(session)

    def add_contact(self, data: ContactCreate) -> ContactRead:
        contact = self.repo.create(data)
        return ContactRead.model_validate(contact, from_attributes=True)

    def get_contact(self, id: int) -> ContactRead | None:
        contact = self.repo.get_by_id(id)
        return ContactRead.model_validate(contact, from_attributes=True) if contact else None

    def list_by_company(self, company_id: int) -> list[ContactRead]:
        contacts = self.repo.list_by_company(company_id)
        return [ContactRead.model_validate(c, from_attributes=True) for c in contacts]

    def contacts_needing_followup(self, days: int = 14) -> list[ContactRead]:
        contacts = self.repo.list_needing_followup(days)
        return [ContactRead.model_validate(c, from_attributes=True) for c in contacts]

    def update_last_contacted(self, contact_id: int) -> ContactRead:
        contact = self.repo.get_by_id(contact_id)
        if not contact:
            raise ValueError(f"Contact id={contact_id} not found")
        updated = self.repo.update(contact, ContactUpdate(last_contacted_at=datetime.now(UTC)))
        return ContactRead.model_validate(updated, from_attributes=True)
