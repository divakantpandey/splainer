"""SQLAlchemy models for test datasets and event schemas."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from spl_to_sql.db.base import Base


class WebLog(Base):
    """Web access log events, corresponding to sourcetype=access_combined."""

    __tablename__ = "web_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    _time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    host: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    sourcetype: Mapped[str] = mapped_column(String(64), nullable=False)
    clientip: Mapped[str] = mapped_column(String(45), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    uri_path: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    useragent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)


class AuthEvent(Base):
    """Authentication events, corresponding to sourcetype=linux_secure."""

    __tablename__ = "auth_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    _time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    host: Mapped[str] = mapped_column(String(64), nullable=False)
    user: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    src_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    app: Mapped[str] = mapped_column(String(64), nullable=False)
