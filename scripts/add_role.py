"""Add a new role."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console
from rich.table import Table

from interview_tracker.database.session import get_session
from interview_tracker.schemas.role import RoleCreate
from interview_tracker.services.company_service import CompanyService
from interview_tracker.services.role_service import RoleService

app = typer.Typer()
console = Console()


@app.command()
def main(
    title: str = typer.Argument(..., help="Role title"),
    company: str = typer.Option(..., help="Company name"),
    url: str = typer.Option(None, help="Job listing URL"),
    salary_min: int = typer.Option(None, help="Minimum salary"),
    salary_max: int = typer.Option(None, help="Maximum salary"),
    office_days: int = typer.Option(None, help="Days in office per week (0=remote, 5=onsite)"),
    min_experience: int = typer.Option(None, help="Minimum years of experience"),
    notes: str = typer.Option(None, help="Free-form notes"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    with get_session() as session:
        company_record = CompanyService(session).get_company_by_name(company)
        if not company_record:
            console.print(f"[red]Error:[/red] Company '{company}' not found")
            raise typer.Exit(1)

        role = RoleService(session).add_role(
            RoleCreate(
                company_id=company_record.id,
                title=title,
                url=url,
                salary_min=salary_min,
                salary_max=salary_max,
                office_days_per_week=office_days,
                min_experience_years=min_experience,
                notes=notes,
            )
        )

    if as_json:
        print(json.dumps(role.model_dump(), default=str))
        return

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_row("[bold]ID[/bold]", str(role.id))
    table.add_row("[bold]Title[/bold]", role.title)
    table.add_row("[bold]Company[/bold]", company)
    if role.url:
        table.add_row("[bold]URL[/bold]", role.url)
    if role.salary_min or role.salary_max:
        lo = f"${role.salary_min:,}" if role.salary_min else "?"
        hi = f"${role.salary_max:,}" if role.salary_max else "?"
        table.add_row("[bold]Salary[/bold]", f"{lo} – {hi}")
    if role.work_arrangement:
        table.add_row("[bold]Arrangement[/bold]", role.work_arrangement)
    if role.min_experience_years is not None:
        table.add_row("[bold]Min Experience[/bold]", f"{role.min_experience_years} yrs")

    console.print("\n[bold green]✓ Role added[/bold green]")
    console.print(table)


if __name__ == "__main__":
    app()
