"""Version 1 API endpoints."""

from . import auth
from . import users
from . import projects
from . import accessories
from . import inspections_external
from . import inspections_site
from . import decommissions
from . import reports
from . import audit

__all__ = [
    "auth",
    "users",
    "projects",
    "accessories",
    "inspections_external",
    "inspections_site",
    "decommissions",
    "reports",
    "audit",
]
