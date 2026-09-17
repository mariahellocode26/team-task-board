from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app
from app.routers.tasks import get_store
from app.store import TaskStore, seed_rows


def _isolated_session() -> Session:
    """A Session against its own private in-memory SQLite database, fully
    isolated from the app's real database and from every other test.

    StaticPool keeps the same in-memory connection alive for the session's
    lifetime — plain in-memory SQLite databases are otherwise dropped as
    soon as a connection closes, which happens between statements without
    it. check_same_thread=False matches app/database.py's own handling
    for the same reason: TestClient calls into the app from a thread pool.
    """

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()


@pytest.fixture
def db_session() -> Session:
    session = _isolated_session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def store(db_session: Session) -> TaskStore:
    """A fresh, empty store — isolated from the app's real database and
    from every other test, so tests can run in any order."""

    return TaskStore(db_session)


@pytest.fixture
def client(store: TaskStore) -> TestClient:
    app.dependency_overrides[get_store] = lambda: store
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def seeded_client() -> TestClient:
    """A client backed by a store carrying the same seed data the app
    starts with, for tests that care about that starting state."""

    session = _isolated_session()
    session.add_all(seed_rows())
    session.commit()
    seeded_store = TaskStore(session)
    app.dependency_overrides[get_store] = lambda: seeded_store
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        session.close()
