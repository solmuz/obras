from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest
from app.schemas.user import UserOut
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user
from app.core.token_blacklist import token_blacklist
from app.core.rate_limiter import limiter, LOGIN_RATE_LIMIT, REFRESH_RATE_LIMIT
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
security_scheme = HTTPBearer()


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
@limiter.limit(LOGIN_RATE_LIMIT)
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
    *,
    credentials: LoginRequest,
) -> TokenResponse:
    """
    Login endpoint - authenticate user and issue tokens.
    
    Args:
        credentials: Login credentials (email and password)
        db: Database session
        
    Returns:
        TokenResponse with access_token, refresh_token, and expiration
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        user = await AuthService.authenticate_user(db, credentials.email, credentials.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"error_code": "INVALID_CREDENTIALS"},
            )
        
        tokens = AuthService.create_tokens(user)
        return TokenResponse(**tokens)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}",
            headers={"error_code": "LOGIN_ERROR"},
        ) from e


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
@limiter.limit(REFRESH_RATE_LIMIT)
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
    *,
    body: RefreshTokenRequest,
) -> TokenResponse:
    """
    Refresh access token endpoint.
    
    The old refresh token is blacklisted after successful rotation
    to prevent reuse (one-time use refresh tokens).
    
    Args:
        request: FastAPI Request (required by rate limiter)
        body: RefreshTokenRequest with refresh_token
        db: Database session
        
    Returns:
        TokenResponse with new access_token and new refresh_token
        
    Raises:
        HTTPException: If refresh token is invalid, expired, or already used
    """
    # Reject already-blacklisted refresh tokens (replay protection)
    if token_blacklist.is_blacklisted(body.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
            headers={"error_code": "TOKEN_REVOKED"},
        )

    result = await AuthService.refresh_access_token(db, body.refresh_token)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"error_code": "TOKEN_INVALID"},
        )
    
    # Blacklist the old refresh token so it cannot be reused
    token_blacklist.add(body.refresh_token)
    
    return TokenResponse(**result)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    body: RefreshTokenRequest | None = None,
):
    """
    Logout endpoint - blacklists the current access token and
    optionally the refresh token so they can no longer be used.
    
    The client should still clear tokens from local storage.
    
    Args:
        credentials: Bearer access token from Authorization header
        body: Optional refresh token to also revoke
    """
    # Blacklist the access token
    token_blacklist.add(credentials.credentials)
    logger.info("Access token blacklisted on logout")

    # Blacklist the refresh token if provided
    if body and body.refresh_token:
        token_blacklist.add(body.refresh_token)
        logger.info("Refresh token blacklisted on logout")


@router.get("/profile", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_profile(
    current_user: User = Depends(get_current_user),
) -> UserOut:
    """
    Get current user profile endpoint.
    
    Requires authentication (valid access token).
    
    Args:
        current_user: Currently authenticated user (from JWT token)
        
    Returns:
        UserOut: User profile data
    """
    return UserOut.from_orm(current_user)
