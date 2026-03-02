from collections.abc import Generator
from contextlib import contextmanager

from sqlmodel import Session

from interview_tracker.database.engine import engine


@contextmanager
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
