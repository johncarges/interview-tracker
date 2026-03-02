"""Record a job application."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console
from rich.table import Table

from interview_tracker.database.session import get_session
from interview_tracker.schemas.application import ApplicationCreate
from interview_tracker.services.application_service import ApplicationService
from interview_tracker.services.company_service import CompanyService
from interview_tracker.services.role_service import RoleService

app = typer.Typer()
console = Console()


@app.command()
def main(
    role_id: int = typer.Option(None, help="Role ID (use instead of --company/--role)"),
    company: str = typer.Option(None, help="Company name"),
    role: str = typer.Option(None, help="Role title (partial match)"),
    notes: str = typer.Option(None, help="Free-form notes"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    with get_session() as session:
        if role_id is None:
            if not company:
                console.print("[red]Error:[/red] Provide --role-id or --company")
                raise typer.Exit(1)
            company_record = CompanyService(session).get_company_by_name(company)
            if not company_record:
                console.print(f"[red]Error:[/red] Company '{company}' not found")
                raise typer.Exit(1)
            roles = RoleService(session).list_by_company(company_record.id)
            if role:
                roles = [r for r in roles if role.lower() in r.title.lower()]
            if not roles:
                console.print("[red]Error:[/red] No matching roles found")
                raise typer.Exit(1)
            if len(roles) > 1:
                console.print("[yellow]Multiple roles found — use --role-id:[/yellow]")
                for r in roles:
                    console.print(f"  {r.id}: {r.title}")
                raise typer.Exit(1)
            role_id = roles[0].id

        try:
            application = ApplicationService(session).add_application(
                ApplicationCreate(role_id=role_id, notes=notes)
            )
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    if as_json:
        print(json.dumps(application.model_dump(), default=str))
        return

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_row("[bold]ID[/bold]", str(application.id))
    table.add_row("[bold]Role ID[/bold]", str(application.role_id))
    table.add_row("[bold]Status[/bold]", application.status)
    table.add_row("[bold]Applied[/bold]", application.applied_at.strftime("%Y-%m-%d"))

    console.print("\n[bold green]✓ Application recorded[/bold green]")
    console.print(table)


if __name__ == "__main__":
    app()
