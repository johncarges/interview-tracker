from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlmodel import Session

T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
    def __init__(self, session: Session) -> None:
        self.session = session

    @abstractmethod
    def get_by_id(self, id: int) -> T | None: ...

    @abstractmethod
    def list_all(self) -> list[T]: ...
