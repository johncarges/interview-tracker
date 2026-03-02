"""Show upcoming interviews."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console
from rich.table import Table

from interview_tracker.database.session import get_session
from interview_tracker.services.interview_service import InterviewService

app = typer.Typer()
console = Console()


@app.command()
def main(
    days: int = typer.Option(14, help="How many days ahead to look"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    with get_session() as session:
        interviews = InterviewService(session).upcoming_interviews(days_ahead=days)

    if as_json:
        print(json.dumps([i.model_dump() for i in interviews], default=str))
        return

    if not interviews:
        console.print(f"[dim]No interviews in the next {days} days.[/dim]")
        return

    table = Table(title=f"Upcoming Interviews (next {days} days)")
    table.add_column("ID", style="dim")
    table.add_column("Date", style="cyan")
    table.add_column("Time", style="cyan")
    table.add_column("Type")
    table.add_column("Application ID", style="dim")

    for i in interviews:
        table.add_row(
            str(i.id),
            i.scheduled_at.strftime("%Y-%m-%d"),
            i.scheduled_at.strftime("%H:%M"),
            i.type.replace("_", " ").title(),
            str(i.application_id),
        )

    console.print(table)


if __name__ == "__main__":
    app()
