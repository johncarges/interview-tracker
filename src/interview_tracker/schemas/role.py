from pydantic import BaseModel


class RoleCreate(BaseModel):
    company_id: int
    title: str
    url: str | None = None
    description: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    status: str = "open"
    notes: str | None = None


class RoleRead(BaseModel):
    id: int
    company_id: int
    title: str
    url: str | None
    description: str | None
    salary_min: int | None
    salary_max: int | None
    status: str
    notes: str | None


class RoleUpdate(BaseModel):
    title: str | None = None
    url: str | None = None
    description: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    status: str | None = None
    notes: str | None = None
