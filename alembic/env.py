import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlmodel import SQLModel

# Make sure src/ is on the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import all models so SQLModel metadata is fully populated
from interview_tracker.database.engine import engine
from interview_tracker.models.application import Application  # noqa: F401
from interview_tracker.models.company import Company  # noqa: F401
from interview_tracker.models.contact import Contact  # noqa: F401
from interview_tracker.models.interview import Interview  # noqa: F401
from interview_tracker.models.role import Role  # noqa: F401
from interview_tracker.models.technology import RoleTechnology, Technology  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (emits SQL to stdout)."""
    context.configure(
        url=str(engine.url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live DB connection."""
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
