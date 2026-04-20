import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from interview_tracker.schemas.contact import ContactCreate
from interview_tracker.services.company_service import CompanyService
from interview_tracker.services.contact_service import ContactService


def register(mcp):
    @mcp.tool()
    def list_contacts() -> str:
        """List all contacts with their ID, name, title, email, and last contacted date."""
        contacts = ContactService().list_all()
        if not contacts:
            return "No contacts found."
        lines = []
        for c in contacts:
            last = c.last_contacted_at.strftime("%Y-%m-%d") if c.last_contacted_at else "never"
            parts = [f"#{c.id} {c.name}"]
            if c.title:
                parts.append(c.title)
            if c.email:
                parts.append(c.email)
            parts.append(f"last contacted={last}")
            lines.append(" | ".join(parts))
        return "\n".join(lines)

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
            ContactCreate(name=name, title=title, email=email, phone=phone, linkedin_url=linkedin, notes=notes)  # noqa: E501
        )
        if company:
            company_record = CompanyService().get_company_by_name(company)
            if not company_record:
                return f"Added contact #{contact.id}: {contact.name}, but company '{company}' not found — not associated."  # noqa: E501
            ContactService().associate_with_company(contact.id, company_record.id)
            return f"Added contact #{contact.id}: {contact.name}, associated with {company}"
        return f"Added contact #{contact.id}: {contact.name}"

    @mcp.tool()
    def update_contact(
        contact_id: int,
        name: str | None = None,
        title: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        linkedin: str | None = None,
        notes: str | None = None,
    ) -> str:
        """Update fields on an existing contact. All fields are optional — only provided fields are changed."""  # noqa: E501
        try:
            contact = ContactService().update_contact(
                contact_id, name=name, title=title, email=email, phone=phone, linkedin=linkedin, notes=notes  # noqa: E501
            )
            return f"Contact #{contact_id} ({contact.name}) updated."
        except ValueError as e:
            return f"Error: {e}"

    @mcp.tool()
    def mark_contacted(contact_id: int) -> str:
        """Record that you reached out to a contact today. Updates their last_contacted_at timestamp."""  # noqa: E501
        try:
            contact = ContactService().update_last_contacted(contact_id)
            return f"Marked contact #{contact_id} ({contact.name}) as contacted today."
        except ValueError as e:
            return f"Error: {e}"

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
