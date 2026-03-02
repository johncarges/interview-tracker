"""Mark an interview as completed."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console

from interview_tracker.database.session import get_session
from interview_tracker.services.interview_service import InterviewService

VALID_OUTCOMES = ["passed", "failed", "pending"]

app = typer.Typer()
console = Console()


@app.command()
def main(
    interview_id: int = typer.Option(..., help="Interview ID"),
    outcome: str = typer.Option(..., help="passed | failed | pending"),
    notes: str = typer.Option(None, help="Free-form notes"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    if outcome not in VALID_OUTCOMES:
        valid = ", ".join(VALID_OUTCOMES)
        console.print(f"[red]Error:[/red] Invalid outcome. Choose from: {valid}")
        raise typer.Exit(1)

    with get_session() as session:
        try:
            interview = InterviewService(session).complete_interview(interview_id, outcome, notes)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    if as_json:
        print(json.dumps(interview.model_dump(), default=str))
        return

    color = {"passed": "green", "failed": "red", "pending": "yellow"}[outcome]
    console.print(
        f"\n[bold green]✓ Interview {interview_id} completed[/bold green] — "
        f"outcome: [bold {color}]{outcome}[/bold {color}]"
    )


if __name__ == "__main__":
    app()
