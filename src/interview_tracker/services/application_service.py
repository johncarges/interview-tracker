from sqlmodel import Session

from interview_tracker.repositories.application import ApplicationRepository
from interview_tracker.repositories.company import CompanyRepository
from interview_tracker.repositories.role import RoleRepository
from interview_tracker.schemas.application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
)


class ApplicationService:
    def __init__(self, session: Session) -> None:
        self.repo = ApplicationRepository(session)
        self.role_repo = RoleRepository(session)
        self.company_repo = CompanyRepository(session)

    def add_application(self, data: ApplicationCreate) -> ApplicationRead:
        role = self.role_repo.get_by_id(data.role_id)
        if not role:
            raise ValueError(f"Role id={data.role_id} not found")
        application = self.repo.create(data)
        return ApplicationRead.model_validate(application, from_attributes=True)

    def get_application(self, id: int) -> ApplicationRead | None:
        application = self.repo.get_by_id(id)
        if not application:
            return None
        return ApplicationRead.model_validate(application, from_attributes=True)

    def update_status(self, application_id: int, status: str) -> ApplicationRead:
        application = self.repo.get_by_id(application_id)
        if not application:
            raise ValueError(f"Application id={application_id} not found")
        updated = self.repo.update(application, ApplicationUpdate(status=status))
        return ApplicationRead.model_validate(updated, from_attributes=True)

    def get_active_applications(self) -> list[ApplicationRead]:
        applications = self.repo.list_active()
        return [ApplicationRead.model_validate(a, from_attributes=True) for a in applications]

    def pipeline_summary(self) -> dict[str, int]:
        return self.repo.count_by_status()

    def get_application_status(
        self,
        company_name: str | None = None,
        role_title: str | None = None,
    ) -> list[ApplicationRead]:
        if company_name:
            company = self.company_repo.get_by_name(company_name)
            if not company:
                raise ValueError(f"Company '{company_name}' not found")
            roles = self.role_repo.list_by_company(company.id)  # type: ignore[arg-type]
            if role_title:
                roles = [r for r in roles if role_title.lower() in r.title.lower()]
            role_ids = {r.id for r in roles}
            applications = [a for a in self.repo.list_all() if a.role_id in role_ids]
        elif role_title:
            all_roles = self.role_repo.list_all()
            role_ids = {r.id for r in all_roles if role_title.lower() in r.title.lower()}
            applications = [a for a in self.repo.list_all() if a.role_id in role_ids]
        else:
            applications = self.repo.list_active()

        return [ApplicationRead.model_validate(a, from_attributes=True) for a in applications]
