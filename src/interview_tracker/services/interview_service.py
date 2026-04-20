from contextlib import nullcontext

from sqlmodel import Session

from interview_tracker.database.session import get_session
from interview_tracker.repositories.application import ApplicationRepository
from interview_tracker.repositories.interview import InterviewRepository
from interview_tracker.schemas.interview import InterviewCreate, InterviewRead, InterviewUpdate


class InterviewService:
    def __init__(self, session: Session | None = None) -> None:
        self._session = session

    def _get_session(self):
        # If a session was injected (e.g. in tests), wrap it in a no-op context manager
        # so the caller retains ownership and we don't close it. Otherwise create our own.
        return nullcontext(self._session) if self._session else get_session()

    def schedule_interview(self, data: InterviewCreate) -> InterviewRead:
        with self._get_session() as session:
            application = ApplicationRepository(session).get_by_id(data.application_id)
            if not application:
                raise ValueError(f"Application id={data.application_id} not found")
            interview = InterviewRepository(session).create(data)
            return InterviewRead.model_validate(interview, from_attributes=True)

    def upcoming_interviews(self, days_ahead: int = 14) -> list[InterviewRead]:
        with self._get_session() as session:
            interviews = InterviewRepository(session).list_upcoming(days_ahead)
            return [InterviewRead.model_validate(i, from_attributes=True) for i in interviews]

    def complete_interview(
        self, interview_id: int, outcome: str, notes: str | None = None
    ) -> InterviewRead:
        from datetime import UTC, datetime

        with self._get_session() as session:
            interview = InterviewRepository(session).get_by_id(interview_id)
            if not interview:
                raise ValueError(f"Interview id={interview_id} not found")

            updated = InterviewRepository(session).update(
                interview,
                InterviewUpdate(outcome=outcome, completed_at=datetime.now(UTC), notes=notes),
            )

            # Bump application to "interviewing" if outcome passed and status is still early-stage
            if outcome == "passed":
                application = ApplicationRepository(session).get_by_id(interview.application_id)
                if application and application.status in {"applied", "screening"}:
                    from interview_tracker.schemas.application import ApplicationUpdate
                    ApplicationRepository(session).update(application, ApplicationUpdate(status="interviewing"))

            return InterviewRead.model_validate(updated, from_attributes=True)

    def update_interview(
        self,
        interview_id: int,
        interview_type: str | None = None,
        scheduled_at: str | None = None,
        contact_id: int | None = None,
        notes: str | None = None,
    ) -> InterviewRead:
        from datetime import datetime
        with self._get_session() as session:
            interview = InterviewRepository(session).get_by_id(interview_id)
            if not interview:
                raise ValueError(f"Interview id={interview_id} not found")
            update_data: dict = {}
            if interview_type is not None:
                update_data["type"] = interview_type
            if scheduled_at is not None:
                update_data["scheduled_at"] = datetime.fromisoformat(scheduled_at)
            if contact_id is not None:
                update_data["interviewer_id"] = contact_id
            if notes is not None:
                update_data["notes"] = notes
            updated = InterviewRepository(session).update(interview, InterviewUpdate(**update_data))
            return InterviewRead.model_validate(updated, from_attributes=True)

    def get_interview(self, id: int) -> InterviewRead | None:
        with self._get_session() as session:
            interview = InterviewRepository(session).get_by_id(id)
            return InterviewRead.model_validate(interview, from_attributes=True) if interview else None
