from pydantic import BaseModel


class TechnologyCreate(BaseModel):
    name: str


class TechnologyRead(BaseModel):
    id: int
    name: str
