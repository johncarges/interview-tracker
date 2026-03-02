from sqlmodel import create_engine

import interview_tracker.models  # noqa: F401 — ensures all models are registered with SQLAlchemy
from interview_tracker.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
