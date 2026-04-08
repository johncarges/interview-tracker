"""MCP server for Interview Tracker."""

from mcp.server.fastmcp import FastMCP

from interview_tracker.database.engine import init_db
from interview_tracker.schemas.application import ApplicationCreate
from interview_tracker.schemas.company import CompanyCreate
from interview_tracker.schemas.contact import ContactCreate
from interview_tracker.schemas.interview import InterviewCreate
from interview_tracker.schemas.role import RoleCreate
from interview_tracker.services.application_service import ApplicationService
from interview_tracker.services.company_service import CompanyService
from interview_tracker.services.contact_service import ContactService
from interview_tracker.services.interview_service import InterviewService
from interview_tracker.services.role_service import RoleService

init_db()

mcp = FastMCP("Interview Tracker")


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
        f"#{a.id} {a.company_name} — {a.role_title} | status={a.status} | applied={a.applied_at.strftime('%Y-%m-%d')}"
        for a in applications
    ]
    return "\n".join(lines)


@mcp.tool()
def upcoming_interviews(days: int = 14) -> str:
    """List interviews scheduled in the next N days (default 14)."""
    interviews = InterviewService().upcoming_interviews(days_ahead=days)
    if not interviews:
        return f"No interviews scheduled in the next {days} days."
    lines = [
        f"#{i.id} {i.type.replace('_', ' ').title()} | application #{i.application_id} | {i.scheduled_at.strftime('%Y-%m-%d %H:%M')}"
        for i in interviews
    ]
    return f"Upcoming interviews (next {days} days):\n" + "\n".join(lines)


@mcp.tool()
def followup_contacts(days: int = 14) -> str:
    """List contacts who haven't been contacted in the last N days (default 14).
    Use this to stay on top of networking outreach."""
    contacts = ContactService().contacts_needing_followup(days=days)
    if not contacts:
        return f"No contacts needing follow-up in the last {days} days."
    lines = []
    for c in contacts:
        last = c.last_contacted_at.strftime("%Y-%m-%d") if c.last_contacted_at else "never"
        lines.append(f"#{c.id} {c.name} | {c.title or 'no title'} | last contacted={last}")
    return "Contacts needing follow-up:\n" + "\n".join(lines)


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
        application = ApplicationService().add_application(ApplicationCreate(role_id=roles[0].id, notes=notes))
    except ValueError as e:
        return f"Error: {e}"
    return f"Recorded application #{application.id} for {roles[0].title} at {company} (status={application.status})"


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
def add_interview(
    application_id: int,
    interview_type: str,
    scheduled_at: str,
    contact_id: int | None = None,
) -> str:
    """Schedule an interview for an application.
    interview_type: phone_screen, technical, system_design, behavioral, onsite, take_home.
    scheduled_at: ISO 8601 string e.g. '2026-04-15T14:00:00'.
    contact_id: optional ID of the interviewer contact."""
    from datetime import datetime
    try:
        scheduled = datetime.fromisoformat(scheduled_at)
    except ValueError:
        return f"Error: Could not parse scheduled_at='{scheduled_at}'. Use ISO 8601 format: YYYY-MM-DDTHH:MM:SS"
    try:
        interview = InterviewService().schedule_interview(
            InterviewCreate(
                application_id=application_id,
                type=interview_type,
                scheduled_at=scheduled,
                interviewer_id=contact_id,
            )
        )
        return f"Scheduled {interview_type} interview #{interview.id} for application #{application_id} on {scheduled.strftime('%Y-%m-%d %H:%M')}"
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


@mcp.tool()
def add_company(
    name: str,
    industry: str | None = None,
    website: str | None = None,
    notes: str | None = None,
) -> str:
    """Add a new company to track. Raises an error if the company already exists."""
    try:
        company = CompanyService().add_company(
            CompanyCreate(name=name, industry=industry, website=website, notes=notes)
        )
        return f"Added company #{company.id}: {company.name} (industry={company.industry})"
    except ValueError as e:
        return f"Error: {e}"


@mcp.tool()
def add_role(
    title: str,
    company: str,
    url: str | None = None,
    description: str | None = None,
    salary_min: int | None = None,
    salary_max: int | None = None,
    office_days: int | None = None,
    notes: str | None = None,
) -> str:
    """Add a new role at a company. The company will be created if it doesn't exist.
    salary_min and salary_max are annual figures in dollars.
    office_days is days per week in office (0=remote, 5=onsite)."""
    company_record, created = CompanyService().get_or_create(name=company)
    role = RoleService().add_role(
        RoleCreate(
            title=title,
            company_id=company_record.id,
            url=url,
            description=description,
            salary_min=salary_min,
            salary_max=salary_max,
            office_days_per_week=office_days,
            notes=notes,
        )
    )
    company_note = " (company created)" if created else ""
    salary = f"${role.salary_min:,}–${role.salary_max:,}" if role.salary_min and role.salary_max else "no salary info"
    return f"Added role #{role.id}: {role.title} at {company}{company_note} ({salary})"


@mcp.tool()
def add_contact(
    name: str,
    company: str | None = None,
    title: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    linkedin: str | None = None,
    notes: str | None = None,
) -> str:
    """Add a new contact, optionally associating them with a company by name."""
    contact = ContactService().add_contact(
        ContactCreate(name=name, title=title, email=email, phone=phone, linkedin_url=linkedin, notes=notes)
    )
    if company:
        company_record = CompanyService().get_company_by_name(company)
        if not company_record:
            return f"Added contact #{contact.id}: {contact.name}, but company '{company}' not found — not associated."
        ContactService().associate_with_company(contact.id, company_record.id)
        return f"Added contact #{contact.id}: {contact.name}, associated with {company}"
    return f"Added contact #{contact.id}: {contact.name}"


@mcp.tool()
def mark_contacted(contact_id: int) -> str:
    """Record that you reached out to a contact today. Updates their last_contacted_at timestamp."""
    try:
        contact = ContactService().update_last_contacted(contact_id)
        return f"Marked contact #{contact_id} ({contact.name}) as contacted today."
    except ValueError as e:
        return f"Error: {e}"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
