from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

_engine = None
_SessionFactory = None


def init_db(db_path: str) -> None:
    """Initialize the database engine and create all tables."""
    global _engine, _SessionFactory

    _engine = create_engine(f"sqlite:///{db_path}", echo=False)
    _SessionFactory = sessionmaker(bind=_engine)

    from db.models import Base
    Base.metadata.create_all(_engine)


def get_session() -> Session:
    """Get a new database session."""
    if _SessionFactory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _SessionFactory()


def get_engine():
    """Get the current database engine."""
    return _engine
