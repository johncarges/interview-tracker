import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from interview_tracker.schemas.interview import InterviewCreate
from interview_tracker.services.application_service import ApplicationService
from interview_tracker.services.interview_service import InterviewService


def register(mcp):
    @mcp.tool()
    def upcoming_interviews(days: int = 14) -> str:
        """List interviews scheduled in the next N days (default 14)."""
        interviews = InterviewService().upcoming_interviews(days_ahead=days)
        if not interviews:
            return f"No interviews scheduled in the next {days} days."
        app_service = ApplicationService()
        lines = []
        for i in interviews:
            app = app_service.get_application_full(i.application_id)
            label = f"{app.company_name} — {app.role_title}" if app else f"application #{i.application_id}"  # noqa: E501
            lines.append(
                f"#{i.id} {i.type.replace('_', ' ').title()} | {label} | {i.scheduled_at.strftime('%Y-%m-%d %H:%M')}"  # noqa: E501
            )
        return f"Upcoming interviews (next {days} days):\n" + "\n".join(lines)

    @mcp.tool()
    def interview_details(interview_id: int) -> str:
        """Get full details for a specific interview, including notes, schedule, and interviewers."""  # noqa: E501
        interview = InterviewService().get_interview(interview_id)
        if not interview:
            return f"Error: Interview #{interview_id} not found."
        app = ApplicationService().get_application_full(interview.application_id)
        label = f"{app.company_name} — {app.role_title}" if app else f"application #{interview.application_id}"  # noqa: E501
        lines = [
            f"Interview #{interview_id} — {label}",
            f"Type:      {interview.type.replace('_', ' ').title()}",
            f"Scheduled: {interview.scheduled_at.strftime('%Y-%m-%d %H:%M')}",
            f"Outcome:   {interview.outcome}",
        ]
        if interview.notes:
            lines.append(f"\nNotes:\n{interview.notes}")
        return "\n".join(lines)

    @mcp.tool()
    def add_interview(
        application_id: int,
        interview_type: str,
        scheduled_at: str,
        contact_id: int | None = None,
        notes: str | None = None,
    ) -> str:
        """Schedule an interview for an application.
        interview_type: phone_screen, technical, system_design, behavioral, onsite, take_home.
        scheduled_at: ISO 8601 string e.g. '2026-04-15T14:00:00'.
        contact_id: optional ID of the interviewer contact.
        notes: optional details e.g. location, schedule, interviewers."""
        from datetime import datetime
        try:
            scheduled = datetime.fromisoformat(scheduled_at)
        except ValueError:
            return f"Error: Could not parse scheduled_at='{scheduled_at}'. Use ISO 8601 format: YYYY-MM-DDTHH:MM:SS"  # noqa: E501
        try:
            interview = InterviewService().schedule_interview(
                InterviewCreate(
                    application_id=application_id,
                    type=interview_type,
                    scheduled_at=scheduled,
                    interviewer_id=contact_id,
                    notes=notes,
                )
            )
            return f"Scheduled {interview_type} interview #{interview.id} for application #{application_id} on {scheduled.strftime('%Y-%m-%d %H:%M')}"  # noqa: E501
        except ValueError as e:
            return f"Error: {e}"

    @mcp.tool()
    def update_interview(
        interview_id: int,
        interview_type: str | None = None,
        scheduled_at: str | None = None,
        contact_id: int | None = None,
        notes: str | None = None,
    ) -> str:
        """Update a scheduled interview. All fields are optional — only provided fields are changed.
        interview_type: phone_screen, technical, system_design, behavioral, onsite, take_home.
        scheduled_at: ISO 8601 string e.g. '2026-04-15T14:00:00'."""
        try:
            InterviewService().update_interview(
                interview_id,
                interview_type=interview_type,
                scheduled_at=scheduled_at,
                contact_id=contact_id,
                notes=notes,
            )
            return f"Interview #{interview_id} updated."
        except ValueError as e:
            return f"Error: {e}"

    @mcp.tool()
    def complete_interview(interview_id: int, outcome: str, notes: str | None = None) -> str:
        """Mark an interview as complete.
        outcome: passed, failed, pending.
        If outcome is 'passed' and the application is in applied/screening, it will be
        automatically advanced to 'interviewing'."""
        try:
            interview = InterviewService().complete_interview(interview_id, outcome, notes)
            return f"Interview #{interview_id} marked complete — outcome={interview.outcome}"
        except ValueError as e:
            return f"Error: {e}"
