"""Show a summary of the full application pipeline."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console
from rich.table import Table

from interview_tracker.database.session import get_session
from interview_tracker.services.application_service import ApplicationService

ORDERED_STATUSES = ["applied", "screening", "interviewing", "offer", "rejected", "withdrawn"]

STATUS_COLORS = {
    "applied": "blue",
    "screening": "cyan",
    "interviewing": "yellow",
    "offer": "bold green",
    "rejected": "red",
    "withdrawn": "dim",
}

app = typer.Typer()
console = Console()


@app.command()
def main(
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    with get_session() as session:
        summary = ApplicationService(session).pipeline_summary()

    if as_json:
        print(json.dumps(summary))
        return

    if not summary:
        console.print("[dim]No applications yet.[/dim]")
        return

    table = Table(title="Pipeline Summary")
    table.add_column("Status")
    table.add_column("Count", justify="right")

    for status in ORDERED_STATUSES:
        count = summary.get(status, 0)
        if count > 0:
            color = STATUS_COLORS.get(status, "white")
            table.add_row(f"[{color}]{status}[/{color}]", str(count))

    table.add_section()
    table.add_row("[bold]Total[/bold]", f"[bold]{sum(summary.values())}[/bold]")

    console.print(table)


if __name__ == "__main__":
    app()
