from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from interview_tracker.models.role import Role


class RoleTechnology(SQLModel, table=True):
    role_id: int | None = Field(default=None, foreign_key="role.id", primary_key=True)
    technology_id: int | None = Field(default=None, foreign_key="technology.id", primary_key=True)


class Technology(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  # type: ignore[assignment]
    name: str = Field(unique=True, index=True)

    roles: list["Role"] = Relationship(back_populates="technologies", link_model=RoleTechnology)
