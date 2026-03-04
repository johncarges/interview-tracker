"""Add a new role, optionally creating the company and recording an application."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console
from rich.table import Table

from interview_tracker.database.session import get_session
from interview_tracker.schemas.application import ApplicationCreate
from interview_tracker.schemas.role import RoleCreate
from interview_tracker.services.application_service import ApplicationService
from interview_tracker.services.company_service import CompanyService
from interview_tracker.services.role_service import RoleService

app = typer.Typer()
console = Console()


@app.command()
def main(
    title: str = typer.Argument(..., help="Role title"),
    company: str = typer.Option(..., help="Company name"),
    website: str = typer.Option(None, help="Company website (used only if company is new)"),
    industry: str = typer.Option(None, help="Company industry (used only if company is new)"),
    url: str = typer.Option(None, help="Job listing URL"),
    description: str = typer.Option(None, help="Full job posting text"),
    salary_min: int = typer.Option(None, help="Minimum salary"),
    salary_max: int = typer.Option(None, help="Maximum salary"),
    office_days: int = typer.Option(None, help="Days in office per week (0=remote, 5=onsite)"),
    min_experience: int = typer.Option(None, help="Minimum years of experience"),
    notes: str = typer.Option(None, help="Free-form notes"),
    apply: bool = typer.Option(False, "--apply", help="Also record an application"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    with get_session() as session:
        company_record, company_created = CompanyService(session).get_or_create(
            name=company, website=website, industry=industry
        )

        role = RoleService(session).add_role(
            RoleCreate(
                company_id=company_record.id,
                title=title,
                url=url,
                description=description,
                salary_min=salary_min,
                salary_max=salary_max,
                office_days_per_week=office_days,
                min_experience_years=min_experience,
                notes=notes,
            )
        )

        application = None
        if apply:
            application = ApplicationService(session).add_application(
                ApplicationCreate(role_id=role.id)
            )

    if as_json:
        out = {"role": role.model_dump(mode="json"), "company_created": company_created}
        if application:
            out["application"] = application.model_dump(mode="json")
        print(json.dumps(out, default=str))
        return

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_row("[bold]Role ID[/bold]", str(role.id))
    table.add_row("[bold]Title[/bold]", role.title)
    company_label = f"{company} [dim](new)[/dim]" if company_created else company
    table.add_row("[bold]Company[/bold]", company_label)
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
    if application:
        table.add_row("[bold]Application[/bold]", f"ID {application.id} · applied")

    console.print("\n[bold green]✓ Role added[/bold green]")
    console.print(table)


if __name__ == "__main__":
    app()
