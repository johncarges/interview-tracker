from sqlmodel import Field, SQLModel


class ContactRole(SQLModel, table=True):
    contact_id: int | None = Field(default=None, foreign_key="contact.id", primary_key=True)
    role_id: int | None = Field(default=None, foreign_key="role.id", primary_key=True)
