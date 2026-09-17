"""Programmatic runner for Alembic migrations."""

from __future__ import annotations

import os
from pathlib import Path

from alembic import command
from alembic.config import Config


def get_alembic_config(connection_url: str | None = None) -> Config:
    """Construct an Alembic Config object pointing to the project migrations directory.

    Args:
        connection_url: Optional database URL. If not provided, falls back to
            DB_CONNECTION_STRING environment variable.

    Returns:
        Configured Alembic Config object.
    """
    # Locate alembic.ini relative to this file or current working directory
    current_path = Path(__file__).resolve()
    # Check parent levels for alembic.ini
    repo_root = current_path.parent.parent.parent
    alembic_ini = repo_root / "alembic.ini"
    if not alembic_ini.exists():
        alembic_ini = Path.cwd() / "alembic.ini"

    config = Config(str(alembic_ini))
    migrations_dir = repo_root / "migrations"
    if migrations_dir.exists():
        config.set_main_option("script_location", str(migrations_dir))

    resolved_url = connection_url or os.environ.get("DB_CONNECTION_STRING")
    if resolved_url:
        config.set_main_option("sqlalchemy.url", resolved_url)

    return config


def run_migrations(connection_url: str | None = None, revision: str = "head") -> None:
    """Run Alembic migrations programmatically up to the target revision.

    Args:
        connection_url: Target database connection string.
        revision: Target revision string (defaults to 'head').
    """
    config = get_alembic_config(connection_url=connection_url)
    command.upgrade(config, revision)


def downgrade_migrations(connection_url: str | None = None, revision: str = "base") -> None:
    """Downgrade Alembic migrations programmatically down to the target revision.

    Args:
        connection_url: Target database connection string.
        revision: Target revision string (defaults to 'base').
    """
    config = get_alembic_config(connection_url=connection_url)
    command.downgrade(config, revision)
