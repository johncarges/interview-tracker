# Import all models here so SQLAlchemy's mapper always has the full registry,
# regardless of which model a script or service directly imports.
from interview_tracker.models.application import Application
from interview_tracker.models.company import Company
from interview_tracker.models.contact import Contact
from interview_tracker.models.contact_role import ContactRole
from interview_tracker.models.interview import Interview
from interview_tracker.models.role import Role
from interview_tracker.models.technology import RoleTechnology, Technology

__all__ = [
    "Application",
    "Company",
    "Contact",
    "ContactRole",
    "Interview",
    "Role",
    "RoleTechnology",
    "Technology",
]
