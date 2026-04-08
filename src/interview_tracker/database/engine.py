from pathlib import Path

from sqlmodel import SQLModel, create_engine

import interview_tracker.models  # noqa: F401 — ensures all models are registered with SQLAlchemy
from interview_tracker.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)


def init_db() -> None:
    """Create all tables if they don't exist. Safe to call on every startup."""
    Path("data").mkdir(exist_ok=True)
    SQLModel.metadata.create_all(engine)
