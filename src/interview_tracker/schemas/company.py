from pydantic import BaseModel


class CompanyCreate(BaseModel):
    name: str
    website: str | None = None
    industry: str | None = None
    status: str = "active"
    notes: str | None = None


class CompanyRead(BaseModel):
    id: int
    name: str
    website: str | None
    industry: str | None
    status: str
    notes: str | None


class CompanyUpdate(BaseModel):
    name: str | None = None
    website: str | None = None
    industry: str | None = None
    status: str | None = None
    notes: str | None = None
