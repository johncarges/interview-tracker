"""Add a new company."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console
from rich.table import Table

from interview_tracker.database.session import get_session
from interview_tracker.schemas.company import CompanyCreate
from interview_tracker.services.company_service import CompanyService

app = typer.Typer()
console = Console()


@app.command()
def main(
    name: str = typer.Argument(..., help="Company name"),
    website: str = typer.Option(None, help="Company website"),
    industry: str = typer.Option(None, help="Industry (e.g. edtech, fintech)"),
    status: str = typer.Option("active", help="active | inactive | rejected"),
    notes: str = typer.Option(None, help="Free-form notes"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    with get_session() as session:
        service = CompanyService(session)
        try:
            company = service.add_company(
                CompanyCreate(
                    name=name, website=website, industry=industry, status=status, notes=notes
                )
            )
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    if as_json:
        print(json.dumps(company.model_dump(), default=str))
        return

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_row("[bold]ID[/bold]", str(company.id))
    table.add_row("[bold]Name[/bold]", company.name)
    if company.website:
        table.add_row("[bold]Website[/bold]", company.website)
    if company.industry:
        table.add_row("[bold]Industry[/bold]", company.industry)
    table.add_row("[bold]Status[/bold]", company.status)

    console.print("\n[bold green]✓ Company added[/bold green]")
    console.print(table)


if __name__ == "__main__":
    app()
