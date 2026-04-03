from contextlib import nullcontext

from sqlmodel import Session

from interview_tracker.database.session import get_session
from interview_tracker.repositories.application import ApplicationRepository
from interview_tracker.repositories.role import RoleRepository
from interview_tracker.repositories.technology import TechnologyRepository
from interview_tracker.schemas.role import RoleCreate, RoleRead, RoleUpdate
from interview_tracker.schemas.technology import TechnologyCreate, TechnologyRead


class RoleService:
    def __init__(self, session: Session | None = None) -> None:
        self._session = session

    def _get_session(self):
        # If a session was injected (e.g. in tests), wrap it in a no-op context manager
        # so the caller retains ownership and we don't close it. Otherwise create our own.
        return nullcontext(self._session) if self._session else get_session()

    def _to_read(self, role, session) -> RoleRead:
        applications = ApplicationRepository(session).list_by_role(role.id)
        latest_status = applications[-1].status if applications else None
        return RoleRead.model_validate(role, from_attributes=True).model_copy(
            update={"application_status": latest_status}
        )

    def add_role(self, data: RoleCreate) -> RoleRead:
        with self._get_session() as session:
            role = RoleRepository(session).create(data)
            return self._to_read(role, session)

    def get_role(self, id: int) -> RoleRead | None:
        with self._get_session() as session:
            role = RoleRepository(session).get_by_id(id)
            return self._to_read(role, session) if role else None

    def list_by_company(self, company_id: int) -> list[RoleRead]:
        with self._get_session() as session:
            roles = RoleRepository(session).list_by_company(company_id)
            return [self._to_read(r, session) for r in roles]

    def update_role(self, id: int, data: RoleUpdate) -> RoleRead:
        with self._get_session() as session:
            role = RoleRepository(session).get_by_id(id)
            if not role:
                raise ValueError(f"Role id={id} not found")
            updated = RoleRepository(session).update(role, data)
            return RoleRead.model_validate(updated, from_attributes=True)

    def add_technology(self, role_id: int, name: str) -> TechnologyRead:
        with self._get_session() as session:
            role = RoleRepository(session).get_by_id(role_id)
            if not role:
                raise ValueError(f"Role id={role_id} not found")
            technology, _ = TechnologyRepository(session).get_or_create(TechnologyCreate(name=name))
            TechnologyRepository(session).add_to_role(role_id, technology.id)  # type: ignore[arg-type]
            return TechnologyRead.model_validate(technology, from_attributes=True)

    def list_technologies(self, role_id: int) -> list[TechnologyRead]:
        with self._get_session() as session:
            technologies = TechnologyRepository(session).list_by_role(role_id)
            return [TechnologyRead.model_validate(t, from_attributes=True) for t in technologies]
