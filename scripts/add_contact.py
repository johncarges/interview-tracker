"""Add a new contact."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console
from rich.table import Table

from interview_tracker.database.session import get_session
from interview_tracker.schemas.contact import ContactCreate
from interview_tracker.services.company_service import CompanyService
from interview_tracker.services.contact_service import ContactService

app = typer.Typer()
console = Console()


@app.command()
def main(
    name: str = typer.Argument(..., help="Contact name"),
    company: str = typer.Option(None, help="Company name to associate with"),
    role_id: int = typer.Option(None, "--role-id", help="Role ID to associate with"),
    title: str = typer.Option(None, help="Job title"),
    email: str = typer.Option(None, help="Email address"),
    phone: str = typer.Option(None, help="Phone number"),
    linkedin: str = typer.Option(None, help="LinkedIn URL"),
    notes: str = typer.Option(None, help="Free-form notes"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    with get_session() as session:
        company_record = None
        if company:
            company_record = CompanyService(session).get_company_by_name(company)
            if not company_record:
                console.print(f"[red]Error:[/red] Company '{company}' not found")
                raise typer.Exit(1)

        contact_svc = ContactService(session)
        contact = contact_svc.add_contact(
            ContactCreate(
                name=name,
                title=title,
                email=email,
                phone=phone,
                linkedin_url=linkedin,
                notes=notes,
            )
        )

        if company_record and contact.id:
            contact_svc.associate_with_company(contact.id, company_record.id)
        if role_id and contact.id:
            contact_svc.associate_with_role(contact.id, role_id)

    if as_json:
        print(json.dumps(contact.model_dump(), default=str))
        return

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_row("[bold]ID[/bold]", str(contact.id))
    table.add_row("[bold]Name[/bold]", contact.name)
    if company_record:
        table.add_row("[bold]Company[/bold]", company)
    if role_id:
        table.add_row("[bold]Role ID[/bold]", str(role_id))
    if contact.title:
        table.add_row("[bold]Title[/bold]", contact.title)
    if contact.email:
        table.add_row("[bold]Email[/bold]", contact.email)
    if contact.linkedin_url:
        table.add_row("[bold]LinkedIn[/bold]", contact.linkedin_url)

    console.print("\n[bold green]✓ Contact added[/bold green]")
    console.print(table)


if __name__ == "__main__":
    app()
