from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from interview_tracker.models.interview import Interview
from interview_tracker.repositories.base import AbstractRepository
from interview_tracker.schemas.interview import InterviewCreate, InterviewUpdate


class InterviewRepository(AbstractRepository[Interview]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id(self, id: int) -> Interview | None:
        return self.session.get(Interview, id)

    def list_all(self) -> list[Interview]:
        return list(self.session.exec(select(Interview)).all())

    def list_by_application(self, application_id: int) -> list[Interview]:
        return list(
            self.session.exec(
                select(Interview).where(Interview.application_id == application_id)
            ).all()
        )

    def list_upcoming(self, days_ahead: int = 14) -> list[Interview]:
        now = datetime.now(UTC)
        cutoff = now + timedelta(days=days_ahead)
        return list(
            self.session.exec(
                select(Interview)
                .where(Interview.scheduled_at >= now)
                .where(Interview.scheduled_at <= cutoff)
                .where(Interview.completed_at == None)  # noqa: E711
                .order_by(Interview.scheduled_at)  # type: ignore[arg-type]
            ).all()
        )

    def create(self, data: InterviewCreate) -> Interview:
        interview = Interview(**data.model_dump())
        self.session.add(interview)
        self.session.commit()
        self.session.refresh(interview)
        return interview

    def update(self, interview: Interview, data: InterviewUpdate) -> Interview:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(interview, field, value)
        interview.updated_at = datetime.now(UTC)
        self.session.add(interview)
        self.session.commit()
        self.session.refresh(interview)
        return interview

    def delete(self, interview: Interview) -> None:
        self.session.delete(interview)
        self.session.commit()
