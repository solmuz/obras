"""
Alembic environment configuration for database migrations.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from app.core.config import settings
from app.db.base import Base
# Import all models to register them with Base.metadata for Alembic autogenerate
from app.models.user import User
from app.models.project import Project
from app.models.accessory import Accessory
from app.models.inspection_external import ExternalInspection
from app.models.inspection_site import SiteInspection
from app.models.decommission import DecommissionRecord
from app.models.audit_log import AuditLog
# this is the Alembic Config object, which provides the values of the [alembic] section
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Convert async URL to sync for offline mode
    # postgresql+asyncpg://user:pass@host/db -> postgresql://user:pass@host/db
    url = settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Convert async URL to sync for SQLAlchemy engine
    # postgresql+asyncpg://user:pass@host/db -> postgresql://user:pass@host/db
    url = settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
    
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
