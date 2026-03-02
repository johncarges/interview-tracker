from datetime import UTC, datetime

from sqlmodel import Session, select

from interview_tracker.models.role import Role
from interview_tracker.repositories.base import AbstractRepository
from interview_tracker.schemas.role import RoleCreate, RoleUpdate


class RoleRepository(AbstractRepository[Role]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id(self, id: int) -> Role | None:
        return self.session.get(Role, id)

    def list_all(self) -> list[Role]:
        return list(self.session.exec(select(Role)).all())

    def list_by_company(self, company_id: int) -> list[Role]:
        return list(self.session.exec(select(Role).where(Role.company_id == company_id)).all())

    def create(self, data: RoleCreate) -> Role:
        role = Role(**data.model_dump())
        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)
        return role

    def update(self, role: Role, data: RoleUpdate) -> Role:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(role, field, value)
        role.updated_at = datetime.now(UTC)
        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)
        return role

    def delete(self, role: Role) -> None:
        self.session.delete(role)
        self.session.commit()
