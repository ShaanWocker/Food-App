"""
Database connection and session management.
"""
import uuid as _uuid
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.config import settings

_DATABASE_URL = settings.DATABASE_URL


class GUID(TypeDecorator):
    """
    Platform-independent GUID type for SQLAlchemy.

    Uses PostgreSQL's native UUID type when available; falls back to
    CHAR(36) for other backends (e.g. SQLite used in tests).
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PGUUID())
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, _uuid.UUID):
            return _uuid.UUID(str(value))
        return value


# SQLite needs special engine config (used in tests); PostgreSQL uses pooling
if _DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        _DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        _DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Yields database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
