# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Database engine and session factory for the Content Service.

Provides:
- ``engine`` — SQLAlchemy engine configured from ``settings.database_url``.
- ``SessionLocal`` — session factory used in normal request handling.
- ``Base`` — declarative base class imported by all ORM models.
- ``get_db()`` — FastAPI dependency that yields a session and closes it after use.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Yield a SQLAlchemy database session and ensure it is closed afterward.

    Intended for use as a FastAPI ``Depends`` dependency.

    Yields:
        :class:`sqlalchemy.orm.Session`: An active database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
