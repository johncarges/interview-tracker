from contextlib import nullcontext

from sqlmodel import Session

from interview_tracker.database.session import get_session
from interview_tracker.repositories.company import CompanyRepository
from interview_tracker.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate


class CompanyService:
    def __init__(self, session: Session | None = None) -> None:
        self._session = session

    def _get_session(self):
        # If a session was injected (e.g. in tests), wrap it in a no-op context manager
        # so the caller retains ownership and we don't close it. Otherwise create our own.
        return nullcontext(self._session) if self._session else get_session()

    def add_company(self, data: CompanyCreate) -> CompanyRead:
        with self._get_session() as session:
            existing = CompanyRepository(session).get_by_name(data.name)
            if existing:
                raise ValueError(f"Company '{data.name}' already exists (id={existing.id})")
            company = CompanyRepository(session).create(data)
            return CompanyRead.model_validate(company, from_attributes=True)

    def get_or_create(
        self,
        name: str,
        website: str | None = None,
        industry: str | None = None,
    ) -> tuple[CompanyRead, bool]:
        """Return (company, created). Creates with provided metadata only if new."""
        with self._get_session() as session:
            existing = CompanyRepository(session).get_by_name(name)
            if existing:
                return CompanyRead.model_validate(existing, from_attributes=True), False
            company = CompanyRepository(session).create(CompanyCreate(name=name, website=website, industry=industry))
            return CompanyRead.model_validate(company, from_attributes=True), True

    def get_company_by_name(self, name: str) -> CompanyRead | None:
        with self._get_session() as session:
            company = CompanyRepository(session).get_by_name(name)
            return CompanyRead.model_validate(company, from_attributes=True) if company else None

    def get_company(self, id: int) -> CompanyRead | None:
        with self._get_session() as session:
            company = CompanyRepository(session).get_by_id(id)
            return CompanyRead.model_validate(company, from_attributes=True) if company else None

    def list_companies(self, status_filter: str | None = None) -> list[CompanyRead]:
        with self._get_session() as session:
            companies = (
                CompanyRepository(session).list_by_status(status_filter)
                if status_filter
                else CompanyRepository(session).list_all()
            )
            return [CompanyRead.model_validate(c, from_attributes=True) for c in companies]

    def update_company(self, id: int, data: CompanyUpdate) -> CompanyRead:
        with self._get_session() as session:
            company = CompanyRepository(session).get_by_id(id)
            if not company:
                raise ValueError(f"Company id={id} not found")
            updated = CompanyRepository(session).update(company, data)
            return CompanyRead.model_validate(updated, from_attributes=True)
