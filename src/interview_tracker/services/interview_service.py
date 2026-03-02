from sqlmodel import Session

from interview_tracker.repositories.application import ApplicationRepository
from interview_tracker.repositories.interview import InterviewRepository
from interview_tracker.schemas.interview import InterviewCreate, InterviewRead, InterviewUpdate

ACTIVE_STATUSES = {"applied", "screening", "interviewing"}


class InterviewService:
    def __init__(self, session: Session) -> None:
        self.repo = InterviewRepository(session)
        self.app_repo = ApplicationRepository(session)

    def schedule_interview(self, data: InterviewCreate) -> InterviewRead:
        application = self.app_repo.get_by_id(data.application_id)
        if not application:
            raise ValueError(f"Application id={data.application_id} not found")
        interview = self.repo.create(data)
        return InterviewRead.model_validate(interview, from_attributes=True)

    def upcoming_interviews(self, days_ahead: int = 14) -> list[InterviewRead]:
        interviews = self.repo.list_upcoming(days_ahead)
        return [InterviewRead.model_validate(i, from_attributes=True) for i in interviews]

    def complete_interview(
        self, interview_id: int, outcome: str, notes: str | None = None
    ) -> InterviewRead:
        from datetime import UTC, datetime

        interview = self.repo.get_by_id(interview_id)
        if not interview:
            raise ValueError(f"Interview id={interview_id} not found")

        updated = self.repo.update(
            interview,
            InterviewUpdate(outcome=outcome, completed_at=datetime.now(UTC), notes=notes),
        )

        # Bump application to "interviewing" if outcome passed and status is still early-stage
        if outcome == "passed":
            application = self.app_repo.get_by_id(interview.application_id)
            if application and application.status in {"applied", "screening"}:
                from interview_tracker.schemas.application import ApplicationUpdate
                self.app_repo.update(application, ApplicationUpdate(status="interviewing"))

        return InterviewRead.model_validate(updated, from_attributes=True)

    def get_interview(self, id: int) -> InterviewRead | None:
        interview = self.repo.get_by_id(id)
        return InterviewRead.model_validate(interview, from_attributes=True) if interview else None
