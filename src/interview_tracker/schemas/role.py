from pydantic import BaseModel


def work_arrangement_label(office_days_per_week: int | None) -> str | None:
    if office_days_per_week is None:
        return None
    if office_days_per_week == 0:
        return "remote"
    if office_days_per_week == 5:
        return "onsite"
    return f"hybrid ({office_days_per_week}d/wk)"


class RoleCreate(BaseModel):
    company_id: int
    title: str
    url: str | None = None
    description: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    status: str = "open"
    office_days_per_week: int | None = None
    min_experience_years: int | None = None
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
    office_days_per_week: int | None
    min_experience_years: int | None
    notes: str | None
    application_status: str | None = None  # None means not yet applied

    @property
    def work_arrangement(self) -> str | None:
        return work_arrangement_label(self.office_days_per_week)


class RoleUpdate(BaseModel):
    title: str | None = None
    url: str | None = None
    description: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    status: str | None = None
    office_days_per_week: int | None = None
    min_experience_years: int | None = None
    notes: str | None = None
