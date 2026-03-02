"""Update an application's status."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console

from interview_tracker.database.session import get_session
from interview_tracker.services.application_service import ApplicationService

VALID_STATUSES = ["applied", "screening", "interviewing", "offer", "rejected", "withdrawn"]

app = typer.Typer()
console = Console()


@app.command()
def main(
    application_id: int = typer.Option(..., help="Application ID"),
    status: str = typer.Option(..., help=f"New status: {', '.join(VALID_STATUSES)}"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    if status not in VALID_STATUSES:
        console.print(f"[red]Error:[/red] Invalid status. Choose from: {', '.join(VALID_STATUSES)}")
        raise typer.Exit(1)

    with get_session() as session:
        try:
            application = ApplicationService(session).update_status(application_id, status)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    if as_json:
        print(json.dumps(application.model_dump(), default=str))
        return

    console.print(
        f"\n[bold green]✓ Application {application_id} status → [/bold green][bold]{status}[/bold]"
    )


if __name__ == "__main__":
    app()
