"""Tests for Alembic migrations and database models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from spl_to_sql.db import AuthEvent, WebLog, downgrade_migrations, run_migrations

if TYPE_CHECKING:
    from pathlib import Path


def test_migrations_and_models(tmp_path: Path) -> None:
    """Verify that Alembic migrations run cleanly and models reflect seed data."""
    db_file = tmp_path / "test.db"
    db_url = f"sqlite:///{db_file}"

    # Run Alembic upgrade head programmatically
    run_migrations(connection_url=db_url, revision="head")

    engine = create_engine(db_url)
    with Session(engine) as session:
        # Verify web_logs seed data
        web_logs = session.scalars(select(WebLog)).all()
        assert len(web_logs) == 8
        assert web_logs[0].host == "web-01"
        assert web_logs[0].status == 200

        # Verify auth_events seed data
        auth_events = session.scalars(select(AuthEvent)).all()
        assert len(auth_events) == 6
        assert auth_events[0].user == "alice"
        assert auth_events[0].action == "success"


def test_migration_downgrade(tmp_path: Path) -> None:
    """Verify that Alembic migrations can be rolled back."""
    db_file = tmp_path / "test_down.db"
    db_url = f"sqlite:///{db_file}"

    # Upgrade to head then downgrade to base
    run_migrations(connection_url=db_url, revision="head")
    downgrade_migrations(connection_url=db_url, revision="base")

    engine = create_engine(db_url)
    # Tables should be dropped
    with engine.connect() as conn:
        from sqlalchemy import inspect

        inspector = inspect(conn)
        tables = inspector.get_table_names()
        assert "web_logs" not in tables
        assert "auth_events" not in tables
