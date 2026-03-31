from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.config import settings
from app.core.rate_limiter import limiter
from app.db.session import engine
from app.db.base import Base

# Import all models to register them with Base.metadata
# This is required for Alembic and SQLAlchemy to detect all tables
from app.models.user import User
from app.models.project import Project
from app.models.accessory import Accessory
from app.models.inspection_external import ExternalInspection
from app.models.inspection_site import SiteInspection
from app.models.decommission import DecommissionRecord
from app.models.audit_log import AuditLog

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting OBRAS API...")
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down OBRAS API...")
    await engine.dispose()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

# Attach rate limiter state and middleware to the app
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Return 429 with a clear message when rate limit is exceeded."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please try again later.",
            "retry_after": exc.detail,
        },
    )


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """Health check endpoint for Docker and load balancers."""
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/api/v1/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def api_health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "api_version": "v1",
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "OBRAS API",
        "version": settings.API_VERSION,
        "documentation": "/docs",
    }


# Register API v1 routers
from app.api.v1 import (
    auth,
    users,
    projects,
    accessories,
    inspections_external,
    inspections_site,
    decommissions,
    reports,
    audit,
)

# Register each router with appropriate prefix and tags
app.include_router(
    auth.router,
    prefix="/api/v1",
    tags=["Authentication"],
)

app.include_router(
    users.router,
    prefix="/api/v1",
    tags=["Users"],
)

app.include_router(
    projects.router,
    prefix="/api/v1",
    tags=["Projects"],
)

app.include_router(
    accessories.router,
    prefix="/api/v1",
    tags=["Accessories"],
)

app.include_router(
    inspections_external.router,
    prefix="/api/v1",
    tags=["Inspections"],
)

app.include_router(
    inspections_site.router,
    prefix="/api/v1",
    tags=["Inspections"],
)

app.include_router(
    decommissions.router,
    prefix="/api/v1",
    tags=["Decommissions"],
)

app.include_router(
    reports.router,
    prefix="/api/v1",
    tags=["Reports"],
)

app.include_router(
    audit.router,
    prefix="/api/v1",
    tags=["Audit"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=settings.ENVIRONMENT == "development",
    )
