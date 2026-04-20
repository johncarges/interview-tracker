from contextlib import nullcontext
from datetime import UTC, datetime

from sqlmodel import Session

from interview_tracker.database.session import get_session
from interview_tracker.repositories.contact import ContactRepository
from interview_tracker.schemas.contact import ContactCreate, ContactRead, ContactUpdate


class ContactService:
    def __init__(self, session: Session | None = None) -> None:
        self._session = session

    def _get_session(self):
        # If a session was injected (e.g. in tests), wrap it in a no-op context manager
        # so the caller retains ownership and we don't close it. Otherwise create our own.
        return nullcontext(self._session) if self._session else get_session()

    def add_contact(self, data: ContactCreate) -> ContactRead:
        with self._get_session() as session:
            contact = ContactRepository(session).create(data)
            return ContactRead.model_validate(contact, from_attributes=True)

    def get_contact(self, id: int) -> ContactRead | None:
        with self._get_session() as session:
            contact = ContactRepository(session).get_by_id(id)
            return ContactRead.model_validate(contact, from_attributes=True) if contact else None

    def list_by_company(self, company_id: int) -> list[ContactRead]:
        with self._get_session() as session:
            contacts = ContactRepository(session).list_by_company(company_id)
            return [ContactRead.model_validate(c, from_attributes=True) for c in contacts]

    def associate_with_company(self, contact_id: int, company_id: int) -> None:
        with self._get_session() as session:
            ContactRepository(session).add_to_company(contact_id, company_id)

    def disassociate_from_company(self, contact_id: int, company_id: int) -> None:
        with self._get_session() as session:
            ContactRepository(session).remove_from_company(contact_id, company_id)

    def associate_with_role(self, contact_id: int, role_id: int) -> None:
        with self._get_session() as session:
            ContactRepository(session).add_to_role(contact_id, role_id)

    def disassociate_from_role(self, contact_id: int, role_id: int) -> None:
        with self._get_session() as session:
            ContactRepository(session).remove_from_role(contact_id, role_id)

    def list_by_role(self, role_id: int) -> list[ContactRead]:
        with self._get_session() as session:
            contacts = ContactRepository(session).list_by_role(role_id)
            return [ContactRead.model_validate(c, from_attributes=True) for c in contacts]

    def list_all(self) -> list[ContactRead]:
        with self._get_session() as session:
            contacts = ContactRepository(session).list_all()
            return [ContactRead.model_validate(c, from_attributes=True) for c in contacts]

    def update_contact(
        self,
        contact_id: int,
        name: str | None = None,
        title: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        linkedin: str | None = None,
        notes: str | None = None,
    ) -> ContactRead:
        with self._get_session() as session:
            contact = ContactRepository(session).get_by_id(contact_id)
            if not contact:
                raise ValueError(f"Contact id={contact_id} not found")
            updated = ContactRepository(session).update(
                contact,
                ContactUpdate(name=name, title=title, email=email, phone=phone, linkedin_url=linkedin, notes=notes),
            )
            return ContactRead.model_validate(updated, from_attributes=True)

    def contacts_needing_followup(self, days: int = 14) -> list[ContactRead]:
        with self._get_session() as session:
            contacts = ContactRepository(session).list_needing_followup(days)
            return [ContactRead.model_validate(c, from_attributes=True) for c in contacts]

    def update_last_contacted(self, contact_id: int) -> ContactRead:
        with self._get_session() as session:
            contact = ContactRepository(session).get_by_id(contact_id)
            if not contact:
                raise ValueError(f"Contact id={contact_id} not found")
            updated = ContactRepository(session).update(contact, ContactUpdate(last_contacted_at=datetime.now(UTC)))
            return ContactRead.model_validate(updated, from_attributes=True)
