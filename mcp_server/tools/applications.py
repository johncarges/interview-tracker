import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from interview_tracker.schemas.application import ApplicationCreate
from interview_tracker.services.application_service import ApplicationService
from interview_tracker.services.company_service import CompanyService
from interview_tracker.services.role_service import RoleService


def register(mcp):
    @mcp.tool()
    def pipeline_summary() -> str:
        """Show a count of applications grouped by status. Use this to get a quick overview
        of where all job applications currently stand."""
        summary = ApplicationService().pipeline_summary()
        if not summary:
            return "No applications yet."
        lines = [f"{status}: {count}" for status, count in sorted(summary.items())]
        return "Pipeline summary:\n" + "\n".join(lines)

    @mcp.tool()
    def application_status(company: str | None = None, role: str | None = None) -> str:
        """Get detailed application status. Optionally filter by company name and/or partial role
        title. Returns all active applications if no filters are provided."""
        applications = ApplicationService().get_application_status_full(
            company_name=company, role_title=role
        )
        if not applications:
            return "No applications found."
        lines = [
            f"#{a.id} {a.company_name} — {a.role_title} | status={a.status} | applied={a.applied_at.strftime('%Y-%m-%d')}"  # noqa: E501
            + (f" | notes={a.notes}" if a.notes else "")
            for a in applications
        ]
        return "\n".join(lines)

    @mcp.tool()
    def add_application(company: str, role: str | None = None, notes: str | None = None) -> str:
        """Record a new job application. Looks up the role by company name and optional partial
        role title. If multiple roles match, returns them so you can be more specific."""
        company_record = CompanyService().get_company_by_name(company)
        if not company_record:
            return f"Error: Company '{company}' not found. Add it first."
        roles = RoleService().list_by_company(company_record.id)
        if role:
            roles = [r for r in roles if role.lower() in r.title.lower()]
        if not roles:
            return f"Error: No matching roles found at {company}. Add the role first."
        if len(roles) > 1:
            options = "\n".join(f"  #{r.id}: {r.title}" for r in roles)
            return f"Multiple roles match — be more specific:\n{options}"
        try:
            application = ApplicationService().add_application(ApplicationCreate(role_id=roles[0].id, notes=notes))  # noqa: E501
        except ValueError as e:
            return f"Error: {e}"
        return f"Recorded application #{application.id} for {roles[0].title} at {company} (status={application.status})"  # noqa: E501

    @mcp.tool()
    def update_application_status(application_id: int, status: str) -> str:
        """Update the status of an application.
        Valid statuses: applied, screening, interviewing, offer, rejected, withdrawn."""
        try:
            application = ApplicationService().update_status(application_id, status)
            return f"Application #{application_id} status updated to '{application.status}'"
        except ValueError as e:
            return f"Error: {e}"

    @mcp.tool()
    def update_application(application_id: int, notes: str) -> str:
        """Update the notes on an existing application."""
        try:
            ApplicationService().update_notes(application_id, notes)
            return f"Application #{application_id} notes updated."
        except ValueError as e:
            return f"Error: {e}"
