"""Schedule an interview."""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console
from rich.table import Table

from interview_tracker.database.session import get_session
from interview_tracker.schemas.interview import InterviewCreate
from interview_tracker.services.interview_service import InterviewService

VALID_TYPES = ["phone_screen", "technical", "system_design", "behavioral", "onsite", "take_home"]

app = typer.Typer()
console = Console()


@app.command()
def main(
    application_id: int = typer.Option(..., help="Application ID"),
    type: str = typer.Option(..., help=f"Interview type: {', '.join(VALID_TYPES)}"),
    scheduled_at: str = typer.Option(..., help="Datetime e.g. '2026-03-15 14:00'"),
    contact_id: int = typer.Option(None, help="Interviewer contact ID"),
    notes: str = typer.Option(None, help="Free-form notes"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    if type not in VALID_TYPES:
        console.print(f"[red]Error:[/red] Invalid type. Choose from: {', '.join(VALID_TYPES)}")
        raise typer.Exit(1)

    try:
        scheduled = datetime.fromisoformat(scheduled_at)
    except ValueError:
        console.print("[red]Error:[/red] Invalid datetime. Use ISO format e.g. '2026-03-15 14:00'")
        raise typer.Exit(1)

    with get_session() as session:
        try:
            interview = InterviewService(session).schedule_interview(
                InterviewCreate(
                    application_id=application_id,
                    type=type,
                    scheduled_at=scheduled,
                    interviewer_id=contact_id,
                    notes=notes,
                )
            )
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    if as_json:
        print(json.dumps(interview.model_dump(), default=str))
        return

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_row("[bold]ID[/bold]", str(interview.id))
    table.add_row("[bold]Type[/bold]", interview.type.replace("_", " ").title())
    table.add_row("[bold]Scheduled[/bold]", interview.scheduled_at.strftime("%Y-%m-%d %H:%M"))

    console.print("\n[bold green]✓ Interview scheduled[/bold green]")
    console.print(table)


if __name__ == "__main__":
    app()
