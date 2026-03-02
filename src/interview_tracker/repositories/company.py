from datetime import UTC, datetime

from sqlmodel import Session, select

from interview_tracker.models.company import Company
from interview_tracker.repositories.base import AbstractRepository
from interview_tracker.schemas.company import CompanyCreate, CompanyUpdate


class CompanyRepository(AbstractRepository[Company]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id(self, id: int) -> Company | None:
        return self.session.get(Company, id)

    def get_by_name(self, name: str) -> Company | None:
        return self.session.exec(select(Company).where(Company.name == name)).first()

    def list_all(self) -> list[Company]:
        return list(self.session.exec(select(Company)).all())

    def list_by_status(self, status: str) -> list[Company]:
        return list(self.session.exec(select(Company).where(Company.status == status)).all())

    def create(self, data: CompanyCreate) -> Company:
        company = Company(**data.model_dump())
        self.session.add(company)
        self.session.commit()
        self.session.refresh(company)
        return company

    def update(self, company: Company, data: CompanyUpdate) -> Company:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(company, field, value)
        company.updated_at = datetime.now(UTC)
        self.session.add(company)
        self.session.commit()
        self.session.refresh(company)
        return company

    def delete(self, company: Company) -> None:
        self.session.delete(company)
        self.session.commit()
