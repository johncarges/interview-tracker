from contextlib import nullcontext

from sqlmodel import Session

from interview_tracker.database.session import get_session
from interview_tracker.repositories.application import ApplicationRepository
from interview_tracker.repositories.company import CompanyRepository
from interview_tracker.repositories.role import RoleRepository
from interview_tracker.schemas.application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationReadFull,
    ApplicationUpdate,
)


class ApplicationService:
    def __init__(self, session: Session | None = None) -> None:
        self._session = session

    def _get_session(self):
        # If a session was injected (e.g. in tests), wrap it in a no-op context manager
        # so the caller retains ownership and we don't close it. Otherwise create our own.
        return nullcontext(self._session) if self._session else get_session()

    def add_application(self, data: ApplicationCreate) -> ApplicationRead:
        with self._get_session() as session:
            role = RoleRepository(session).get_by_id(data.role_id)
            if not role:
                raise ValueError(f"Role id={data.role_id} not found")
            application = ApplicationRepository(session).create(data)
            return ApplicationRead.model_validate(application, from_attributes=True)

    def get_application(self, id: int) -> ApplicationRead | None:
        with self._get_session() as session:
            application = ApplicationRepository(session).get_by_id(id)
            if not application:
                return None
            return ApplicationRead.model_validate(application, from_attributes=True)

    def update_status(self, application_id: int, status: str) -> ApplicationRead:
        with self._get_session() as session:
            application = ApplicationRepository(session).get_by_id(application_id)
            if not application:
                raise ValueError(f"Application id={application_id} not found")
            updated = ApplicationRepository(session).update(application, ApplicationUpdate(status=status))
            return ApplicationRead.model_validate(updated, from_attributes=True)

    def get_active_applications(self) -> list[ApplicationRead]:
        with self._get_session() as session:
            applications = ApplicationRepository(session).list_active()
            return [ApplicationRead.model_validate(a, from_attributes=True) for a in applications]

    def pipeline_summary(self) -> dict[str, int]:
        with self._get_session() as session:
            return ApplicationRepository(session).count_by_status()

    def get_application_status(
        self,
        company_name: str | None = None,
        role_title: str | None = None,
    ) -> list[ApplicationRead]:
        with self._get_session() as session:
            app_repo = ApplicationRepository(session)
            role_repo = RoleRepository(session)
            company_repo = CompanyRepository(session)

            if company_name:
                company = company_repo.get_by_name(company_name)
                if not company:
                    raise ValueError(f"Company '{company_name}' not found")
                roles = role_repo.list_by_company(company.id)  # type: ignore[arg-type]
                if role_title:
                    roles = [r for r in roles if role_title.lower() in r.title.lower()]
                role_ids = {r.id for r in roles}
                applications = [a for a in app_repo.list_all() if a.role_id in role_ids]
            elif role_title:
                all_roles = role_repo.list_all()
                role_ids = {r.id for r in all_roles if role_title.lower() in r.title.lower()}
                applications = [a for a in app_repo.list_all() if a.role_id in role_ids]
            else:
                applications = app_repo.list_active()

            return [ApplicationRead.model_validate(a, from_attributes=True) for a in applications]

    def _to_full(self, application_id: int, session) -> ApplicationReadFull | None:
        app = ApplicationRepository(session).get_by_id(application_id)
        if not app:
            return None
        role = RoleRepository(session).get_by_id(app.role_id)
        company = CompanyRepository(session).get_by_id(role.company_id) if role else None  # type: ignore[arg-type]
        return ApplicationReadFull(
            id=app.id,  # type: ignore[arg-type]
            role_id=app.role_id,
            status=app.status,
            applied_at=app.applied_at,
            notes=app.notes,
            role_title=role.title if role else "Unknown",
            company_name=company.name if company else "Unknown",
        )

    def get_application_status_full(
        self,
        company_name: str | None = None,
        role_title: str | None = None,
    ) -> list[ApplicationReadFull]:
        with self._get_session() as session:
            base = self.get_application_status(company_name=company_name, role_title=role_title)
            return [full for a in base if (full := self._to_full(a.id, session)) is not None]
