from datetime import UTC, datetime

from sqlmodel import Session, select

from interview_tracker.models.application import Application
from interview_tracker.repositories.base import AbstractRepository
from interview_tracker.schemas.application import ApplicationCreate, ApplicationUpdate


class ApplicationRepository(AbstractRepository[Application]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id(self, id: int) -> Application | None:
        return self.session.get(Application, id)

    def list_all(self) -> list[Application]:
        return list(self.session.exec(select(Application)).all())

    def list_by_role(self, role_id: int) -> list[Application]:
        return list(
            self.session.exec(select(Application).where(Application.role_id == role_id)).all()
        )

    def list_by_status(self, status: str) -> list[Application]:
        return list(
            self.session.exec(select(Application).where(Application.status == status)).all()
        )

    def list_active(self) -> list[Application]:
        return list(
            self.session.exec(
                select(Application).where(Application.status.notin_(["rejected", "withdrawn"]))  # type: ignore[union-attr]
            ).all()
        )

    def count_by_status(self) -> dict[str, int]:
        applications = self.list_all()
        counts: dict[str, int] = {}
        for app in applications:
            counts[app.status] = counts.get(app.status, 0) + 1
        return counts

    def create(self, data: ApplicationCreate) -> Application:
        application = Application(**data.model_dump())
        self.session.add(application)
        self.session.commit()
        self.session.refresh(application)
        return application

    def update(self, application: Application, data: ApplicationUpdate) -> Application:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(application, field, value)
        application.updated_at = datetime.now(UTC)
        self.session.add(application)
        self.session.commit()
        self.session.refresh(application)
        return application

    def delete(self, application: Application) -> None:
        self.session.delete(application)
        self.session.commit()
