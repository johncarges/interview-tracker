from sqlmodel import Session

from interview_tracker.repositories.company import CompanyRepository
from interview_tracker.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate


class CompanyService:
    def __init__(self, session: Session) -> None:
        self.repo = CompanyRepository(session)

    def add_company(self, data: CompanyCreate) -> CompanyRead:
        existing = self.repo.get_by_name(data.name)
        if existing:
            raise ValueError(f"Company '{data.name}' already exists (id={existing.id})")
        company = self.repo.create(data)
        return CompanyRead.model_validate(company, from_attributes=True)

    def get_or_create(
        self,
        name: str,
        website: str | None = None,
        industry: str | None = None,
    ) -> tuple[CompanyRead, bool]:
        """Return (company, created). Creates with provided metadata only if new."""
        existing = self.repo.get_by_name(name)
        if existing:
            return CompanyRead.model_validate(existing, from_attributes=True), False
        company = self.repo.create(CompanyCreate(name=name, website=website, industry=industry))
        return CompanyRead.model_validate(company, from_attributes=True), True

    def get_company_by_name(self, name: str) -> CompanyRead | None:
        company = self.repo.get_by_name(name)
        return CompanyRead.model_validate(company, from_attributes=True) if company else None

    def get_company(self, id: int) -> CompanyRead | None:
        company = self.repo.get_by_id(id)
        return CompanyRead.model_validate(company, from_attributes=True) if company else None

    def list_companies(self, status_filter: str | None = None) -> list[CompanyRead]:
        companies = (
            self.repo.list_by_status(status_filter) if status_filter else self.repo.list_all()
        )
        return [CompanyRead.model_validate(c, from_attributes=True) for c in companies]

    def update_company(self, id: int, data: CompanyUpdate) -> CompanyRead:
        company = self.repo.get_by_id(id)
        if not company:
            raise ValueError(f"Company id={id} not found")
        updated = self.repo.update(company, data)
        return CompanyRead.model_validate(updated, from_attributes=True)
