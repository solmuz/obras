from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import decode_jwt_token
from app.core.config import settings
from app.core.token_blacklist import token_blacklist
from app.db.session import get_db
from app.models.user import User
from typing import Optional

security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract and validate the current user ID from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials from Authorization header
        
    Returns:
        User ID extracted from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials

    # Reject blacklisted tokens (logged-out or rotated)
    if token_blacklist.is_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"error_code": "TOKEN_REVOKED"}
        )

    payload = decode_jwt_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"error_code": "TOKEN_INVALID"}
        )
    
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID",
            headers={"error_code": "TOKEN_INVALID"}
        )
    
    return user_id


async def get_current_user_role(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract and validate the current user role from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials from Authorization header
        
    Returns:
        User role extracted from token (ADMIN, INGENIERO_HSE, CONSULTA)
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    payload = decode_jwt_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"error_code": "TOKEN_INVALID"}
        )
    
    role: Optional[str] = payload.get("role")
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user role",
            headers={"error_code": "TOKEN_INVALID"}
        )
    
    return role


def require_role(*allowed_roles: str):
    """
    Factory function to create a role-based access control dependency.
    
    Args:
        allowed_roles: Variable number of allowed role strings
        
    Example:
        @router.post("/users", dependencies=[Depends(require_role("ADMIN"))])
    """
    async def role_checker(
        user_id: str = Depends(get_current_user_id),
        role: str = Depends(get_current_user_role)
    ) -> tuple[str, str]:
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' not authorized for this action. Allowed: {allowed_roles}",
                headers={"error_code": "INSUFFICIENT_PERMISSIONS"}
            )
        return user_id, role
    
    return role_checker


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get the current authenticated user object from the database.
    
    Args:
        user_id: User ID extracted from JWT token
        db: Database session
        
    Returns:
        User model instance
        
    Raises:
        HTTPException: If user not found in database
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"error_code": "USER_NOT_FOUND"}
        )
    
    return user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to require admin role for protected endpoints.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if admin, raises HTTPException otherwise
        
    Raises:
        HTTPException: If user is not ADMIN
    """
    from app.models.user import RoleEnum
    
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
            headers={"error_code": "INSUFFICIENT_PERMISSIONS"}
        )
    
    return current_user


async def require_write_access(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to require write access (ADMIN or INGENIERO_HSE).
    CONSULTA role is read-only and will be rejected.
    """
    from app.models.user import RoleEnum

    if current_user.role == RoleEnum.CONSULTA:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Write access denied for CONSULTA role",
            headers={"error_code": "INSUFFICIENT_PERMISSIONS"}
        )

    return current_user
