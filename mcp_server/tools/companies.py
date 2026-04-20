import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from interview_tracker.schemas.company import CompanyCreate
from interview_tracker.schemas.role import RoleCreate
from interview_tracker.services.company_service import CompanyService
from interview_tracker.services.role_service import RoleService


def register(mcp):
    @mcp.tool()
    def add_company(
        name: str,
        industry: str | None = None,
        website: str | None = None,
        notes: str | None = None,
    ) -> str:
        """Add a new company to track. Raises an error if the company already exists."""
        try:
            company = CompanyService().add_company(
                CompanyCreate(name=name, industry=industry, website=website, notes=notes)
            )
            return f"Added company #{company.id}: {company.name} (industry={company.industry})"
        except ValueError as e:
            return f"Error: {e}"

    @mcp.tool()
    def add_role(
        title: str,
        company: str,
        url: str | None = None,
        description: str | None = None,
        salary_min: int | None = None,
        salary_max: int | None = None,
        office_days: int | None = None,
        notes: str | None = None,
    ) -> str:
        """Add a new role at a company. The company will be created if it doesn't exist.
        salary_min and salary_max are annual figures in dollars.
        office_days is days per week in office (0=remote, 5=onsite)."""
        company_record, created = CompanyService().get_or_create(name=company)
        role = RoleService().add_role(
            RoleCreate(
                title=title,
                company_id=company_record.id,
                url=url,
                description=description,
                salary_min=salary_min,
                salary_max=salary_max,
                office_days_per_week=office_days,
                notes=notes,
            )
        )
        company_note = " (company created)" if created else ""
        salary = f"${role.salary_min:,}–${role.salary_max:,}" if role.salary_min and role.salary_max else "no salary info"  # noqa: E501
        return f"Added role #{role.id}: {role.title} at {company}{company_note} ({salary})"
