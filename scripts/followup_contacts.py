"""Show contacts that need a follow-up."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console
from rich.table import Table

from interview_tracker.database.session import get_session
from interview_tracker.services.contact_service import ContactService

app = typer.Typer()
console = Console()


@app.command()
def main(
    days: int = typer.Option(14, help="Flag contacts not reached in this many days"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    with get_session() as session:
        contacts = ContactService(session).contacts_needing_followup(days=days)

    if as_json:
        print(json.dumps([c.model_dump() for c in contacts], default=str))
        return

    if not contacts:
        console.print("[dim]No contacts needing follow-up.[/dim]")
        return

    table = Table(title=f"Contacts Needing Follow-up (>{days} days)")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Title", style="dim")
    table.add_column("Last Contacted", style="yellow")

    for c in contacts:
        last = (
            c.last_contacted_at.strftime("%Y-%m-%d") if c.last_contacted_at else "[dim]never[/dim]"
        )
        table.add_row(str(c.id), c.name, c.title or "", last)

    console.print(table)


if __name__ == "__main__":
    app()
