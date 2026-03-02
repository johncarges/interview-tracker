"""Initialize the database — create all tables."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from sqlmodel import SQLModel

from interview_tracker.database.engine import engine

# Import all models so SQLModel metadata is populated
from interview_tracker.models.application import Application  # noqa: F401
from interview_tracker.models.company import Company  # noqa: F401
from interview_tracker.models.contact import Contact  # noqa: F401
from interview_tracker.models.interview import Interview  # noqa: F401
from interview_tracker.models.role import Role  # noqa: F401
from interview_tracker.models.technology import RoleTechnology, Technology  # noqa: F401

console = Console()


def main() -> None:
    # Ensure data/ directory exists
    db_path = Path("data")
    db_path.mkdir(exist_ok=True)

    console.print("[bold blue]Initializing database...[/bold blue]")
    SQLModel.metadata.create_all(engine)
    console.print("[bold green]✓ Database initialized successfully.[/bold green]")
    console.print(f"  Tables created: {', '.join(SQLModel.metadata.tables.keys())}")


if __name__ == "__main__":
    main()
