from sqlmodel import Session

from interview_tracker.repositories.role import RoleRepository
from interview_tracker.repositories.technology import TechnologyRepository
from interview_tracker.schemas.role import RoleCreate, RoleRead, RoleUpdate
from interview_tracker.schemas.technology import TechnologyCreate, TechnologyRead


class RoleService:
    def __init__(self, session: Session) -> None:
        self.repo = RoleRepository(session)
        self.tech_repo = TechnologyRepository(session)

    def add_role(self, data: RoleCreate) -> RoleRead:
        role = self.repo.create(data)
        return RoleRead.model_validate(role, from_attributes=True)

    def get_role(self, id: int) -> RoleRead | None:
        role = self.repo.get_by_id(id)
        return RoleRead.model_validate(role, from_attributes=True) if role else None

    def list_by_company(self, company_id: int) -> list[RoleRead]:
        roles = self.repo.list_by_company(company_id)
        return [RoleRead.model_validate(r, from_attributes=True) for r in roles]

    def update_role(self, id: int, data: RoleUpdate) -> RoleRead:
        role = self.repo.get_by_id(id)
        if not role:
            raise ValueError(f"Role id={id} not found")
        updated = self.repo.update(role, data)
        return RoleRead.model_validate(updated, from_attributes=True)

    def add_technology(self, role_id: int, name: str) -> TechnologyRead:
        role = self.repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"Role id={role_id} not found")
        technology, _ = self.tech_repo.get_or_create(TechnologyCreate(name=name))
        self.tech_repo.add_to_role(role_id, technology.id)  # type: ignore[arg-type]
        return TechnologyRead.model_validate(technology, from_attributes=True)

    def list_technologies(self, role_id: int) -> list[TechnologyRead]:
        technologies = self.tech_repo.list_by_role(role_id)
        return [TechnologyRead.model_validate(t, from_attributes=True) for t in technologies]
