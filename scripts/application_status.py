"""Show the status of one or more applications."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console
from rich.table import Table

from interview_tracker.database.session import get_session
from interview_tracker.services.application_service import ApplicationService

STATUS_COLORS = {
    "applied": "blue",
    "screening": "cyan",
    "interviewing": "yellow",
    "offer": "green",
    "rejected": "red",
    "withdrawn": "dim",
}

app = typer.Typer()
console = Console()


@app.command()
def main(
    company: str = typer.Option(None, help="Filter by company name"),
    role: str = typer.Option(None, help="Filter by role title (partial match)"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    with get_session() as session:
        try:
            applications = ApplicationService(session).get_application_status(
                company_name=company, role_title=role
            )
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    if as_json:
        print(json.dumps([a.model_dump() for a in applications], default=str))
        return

    if not applications:
        console.print("[dim]No applications found.[/dim]")
        return

    table = Table(title="Application Status")
    table.add_column("ID", style="dim")
    table.add_column("Role ID", style="dim")
    table.add_column("Status")
    table.add_column("Applied", style="dim")

    for a in applications:
        color = STATUS_COLORS.get(a.status, "white")
        table.add_row(
            str(a.id),
            str(a.role_id),
            f"[{color}]{a.status}[/{color}]",
            a.applied_at.strftime("%Y-%m-%d"),
        )

    console.print(table)


if __name__ == "__main__":
    app()
