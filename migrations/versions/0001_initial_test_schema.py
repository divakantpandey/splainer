"""Initial test schema and seed data.

Revision ID: 0001_initial_test_schema
Revises: None
Create Date: 2026-09-16 17:00:00.000000

"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "0001_initial_test_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create web_logs table
    web_logs_table = op.create_table(
        "web_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("_time", sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column("host", sa.String(length=64), nullable=False),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("sourcetype", sa.String(length=64), nullable=False),
        sa.Column("clientip", sa.String(length=45), nullable=False),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("uri_path", sa.String(length=255), nullable=False),
        sa.Column("status", sa.Integer(), nullable=False),
        sa.Column("bytes", sa.Integer(), nullable=False),
        sa.Column("useragent", sa.String(length=255), nullable=True),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # 2. Create auth_events table
    auth_events_table = op.create_table(
        "auth_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("_time", sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column("host", sa.String(length=64), nullable=False),
        sa.Column("user", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("src_ip", sa.String(length=45), nullable=False),
        sa.Column("app", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # 3. Seed initial test data generically
    op.bulk_insert(
        web_logs_table,
        [
            {
                "_time": datetime(2026, 9, 15, 10, 0, 0),
                "host": "web-01",
                "source": "/var/log/nginx/access.log",
                "sourcetype": "access_combined",
                "clientip": "192.168.1.10",
                "method": "GET",
                "uri_path": "/api/v1/users",
                "status": 200,
                "bytes": 1420,
                "useragent": "Mozilla/5.0",
                "response_time_ms": 45,
            },
            {
                "_time": datetime(2026, 9, 15, 10, 0, 5),
                "host": "web-01",
                "source": "/var/log/nginx/access.log",
                "sourcetype": "access_combined",
                "clientip": "192.168.1.11",
                "method": "POST",
                "uri_path": "/api/v1/login",
                "status": 200,
                "bytes": 520,
                "useragent": "Mozilla/5.0",
                "response_time_ms": 120,
            },
            {
                "_time": datetime(2026, 9, 15, 10, 1, 12),
                "host": "web-02",
                "source": "/var/log/nginx/access.log",
                "sourcetype": "access_combined",
                "clientip": "192.168.1.12",
                "method": "GET",
                "uri_path": "/api/v1/products",
                "status": 200,
                "bytes": 8920,
                "useragent": "curl/7.68.0",
                "response_time_ms": 30,
            },
            {
                "_time": datetime(2026, 9, 15, 10, 2, 45),
                "host": "web-02",
                "source": "/var/log/nginx/access.log",
                "sourcetype": "access_combined",
                "clientip": "192.168.1.13",
                "method": "GET",
                "uri_path": "/api/v1/orders",
                "status": 500,
                "bytes": 310,
                "useragent": "Mozilla/5.0",
                "response_time_ms": 850,
            },
            {
                "_time": datetime(2026, 9, 15, 10, 3, 0),
                "host": "web-01",
                "source": "/var/log/nginx/access.log",
                "sourcetype": "access_combined",
                "clientip": "192.168.1.14",
                "method": "GET",
                "uri_path": "/api/v1/cart",
                "status": 404,
                "bytes": 210,
                "useragent": "Mozilla/5.0",
                "response_time_ms": 15,
            },
            {
                "_time": datetime(2026, 9, 15, 10, 4, 10),
                "host": "web-03",
                "source": "/var/log/nginx/access.log",
                "sourcetype": "access_combined",
                "clientip": "192.168.1.15",
                "method": "POST",
                "uri_path": "/api/v1/checkout",
                "status": 200,
                "bytes": 1150,
                "useragent": "Mozilla/5.0",
                "response_time_ms": 310,
            },
            {
                "_time": datetime(2026, 9, 15, 10, 5, 22),
                "host": "web-01",
                "source": "/var/log/nginx/access.log",
                "sourcetype": "access_combined",
                "clientip": "192.168.1.16",
                "method": "GET",
                "uri_path": "/api/v1/users",
                "status": 200,
                "bytes": 1430,
                "useragent": "Mozilla/5.0",
                "response_time_ms": 40,
            },
            {
                "_time": datetime(2026, 9, 15, 10, 6, 30),
                "host": "web-02",
                "source": "/var/log/nginx/access.log",
                "sourcetype": "access_combined",
                "clientip": "192.168.1.17",
                "method": "GET",
                "uri_path": "/api/v1/products",
                "status": 500,
                "bytes": 310,
                "useragent": "Mozilla/5.0",
                "response_time_ms": 920,
            },
        ],
    )

    op.bulk_insert(
        auth_events_table,
        [
            {
                "_time": datetime(2026, 9, 15, 9, 30, 0),
                "host": "auth-01",
                "user": "alice",
                "action": "success",
                "src_ip": "10.0.0.5",
                "app": "ssh",
            },
            {
                "_time": datetime(2026, 9, 15, 9, 31, 0),
                "host": "auth-01",
                "user": "bob",
                "action": "failure",
                "src_ip": "10.0.0.12",
                "app": "ssh",
            },
            {
                "_time": datetime(2026, 9, 15, 9, 31, 5),
                "host": "auth-01",
                "user": "bob",
                "action": "failure",
                "src_ip": "10.0.0.12",
                "app": "ssh",
            },
            {
                "_time": datetime(2026, 9, 15, 9, 31, 10),
                "host": "auth-01",
                "user": "bob",
                "action": "success",
                "src_ip": "10.0.0.12",
                "app": "ssh",
            },
            {
                "_time": datetime(2026, 9, 15, 9, 40, 0),
                "host": "auth-02",
                "user": "admin",
                "action": "failure",
                "src_ip": "198.51.100.4",
                "app": "ssh",
            },
            {
                "_time": datetime(2026, 9, 15, 9, 40, 2),
                "host": "auth-02",
                "user": "admin",
                "action": "failure",
                "src_ip": "198.51.100.4",
                "app": "ssh",
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("auth_events")
    op.drop_table("web_logs")
