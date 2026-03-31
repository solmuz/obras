"""Pydantic request/response schemas."""
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest, LogoutRequest
from app.schemas.user import UserCreate, UserUpdate, UserOut, UserListOut, RoleEnum as UserRoleEnum
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectOut,
    ProjectDetailOut,
    ProjectStatusEnum,
    AssignEmployeeRequest,
    RemoveEmployeeRequest,
)
from app.schemas.accessory import (
    AccessoryCreate,
    AccessoryUpdate,
    AccessoryOut,
    AccessoryListOut,
    BrandEnum,
    ElementTypeEnum,
    UsageStatusEnum,
)
from app.schemas.inspection import (
    ExternalInspectionCreate,
    ExternalInspectionOut,
    ExternalInspectionCompanyEnum,
    InspectionStatusEnum,
    SiteInspectionCreate,
    SiteInspectionOut,
    SiteInspectionCompanyEnum,
    SiteInspectionResultEnum,
    ColorPeriodEnum,
)
from app.schemas.decommission import DecommissionCreate, DecommissionOut
from app.schemas.audit_log import AuditLogOut, AuditActionEnum

__all__ = [
    # Auth
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "LogoutRequest",
    # User
    "UserCreate",
    "UserUpdate",
    "UserOut",
    "UserListOut",
    "UserRoleEnum",
    # Project
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectOut",
    "ProjectDetailOut",
    "ProjectStatusEnum",
    "AssignEmployeeRequest",
    "RemoveEmployeeRequest",
    # Accessory
    "AccessoryCreate",
    "AccessoryUpdate",
    "AccessoryOut",
    "AccessoryListOut",
    "BrandEnum",
    "ElementTypeEnum",
    "UsageStatusEnum",
    # Inspection
    "ExternalInspectionCreate",
    "ExternalInspectionOut",
    "ExternalInspectionCompanyEnum",
    "InspectionStatusEnum",
    "SiteInspectionCreate",
    "SiteInspectionOut",
    "SiteInspectionCompanyEnum",
    "SiteInspectionResultEnum",
    "ColorPeriodEnum",
    # Decommission
    "DecommissionCreate",
    "DecommissionOut",
    # AuditLog
    "AuditLogOut",
    "AuditActionEnum",
]
