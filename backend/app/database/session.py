"""SQLAlchemy engine and session factory.

Supports both SQLite (dev/fallback) and PostgreSQL (Neon DB production).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from backend.app.core.config import settings

# Build engine kwargs depending on the DB dialect
_db_url = settings.DATABASE_URL
_connect_args = {}

if _db_url.startswith("sqlite"):
    # SQLite requires check_same_thread=False for multi-threaded FastAPI
    _connect_args = {"check_same_thread": False}

if _db_url.startswith("postgres"):
    # Neon DB uses SSL by default; psycopg2 handles it via sslmode in the URL.
    # No special connect_args needed unless you want to add ca cert.
    _connect_args = {}

engine = create_engine(
    _db_url,
    connect_args=_connect_args,
    echo=False,
    # For PostgreSQL / Neon: keep a small pool to avoid hitting Neon's
    # serverless connection limits.
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that provides a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
