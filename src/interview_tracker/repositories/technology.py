from sqlmodel import Session, select

from interview_tracker.models.technology import RoleTechnology, Technology
from interview_tracker.repositories.base import AbstractRepository
from interview_tracker.schemas.technology import TechnologyCreate


class TechnologyRepository(AbstractRepository[Technology]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id(self, id: int) -> Technology | None:
        return self.session.get(Technology, id)

    def get_by_name(self, name: str) -> Technology | None:
        return self.session.exec(select(Technology).where(Technology.name == name)).first()

    def list_all(self) -> list[Technology]:
        return list(self.session.exec(select(Technology).order_by(Technology.name)).all())  # type: ignore[arg-type]

    def list_by_role(self, role_id: int) -> list[Technology]:
        return list(
            self.session.exec(
                select(Technology)
                .join(RoleTechnology, RoleTechnology.technology_id == Technology.id)  # type: ignore[arg-type]
                .where(RoleTechnology.role_id == role_id)
            ).all()
        )

    def get_or_create(self, data: TechnologyCreate) -> tuple[Technology, bool]:
        """Return (technology, created). Normalizes name before lookup."""
        normalized = data.name.strip()
        existing = self.get_by_name(normalized)
        if existing:
            return existing, False
        technology = Technology(name=normalized)
        self.session.add(technology)
        self.session.commit()
        self.session.refresh(technology)
        return technology, True

    def add_to_role(self, role_id: int, technology_id: int) -> None:
        existing = self.session.exec(
            select(RoleTechnology)
            .where(RoleTechnology.role_id == role_id)
            .where(RoleTechnology.technology_id == technology_id)
        ).first()
        if not existing:
            link = RoleTechnology(role_id=role_id, technology_id=technology_id)
            self.session.add(link)
            self.session.commit()

    def remove_from_role(self, role_id: int, technology_id: int) -> None:
        link = self.session.exec(
            select(RoleTechnology)
            .where(RoleTechnology.role_id == role_id)
            .where(RoleTechnology.technology_id == technology_id)
        ).first()
        if link:
            self.session.delete(link)
            self.session.commit()

    def create(self, data: TechnologyCreate) -> Technology:
        technology, _ = self.get_or_create(data)
        return technology
