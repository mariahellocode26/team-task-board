from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.tasks import get_store
from app.store import TaskStore


@pytest.fixture
def store() -> TaskStore:
    """A fresh, empty store — isolated from the app's shared singleton and
    from every other test, so tests can run in any order."""

    return TaskStore(seed=False)


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

    seeded_store = TaskStore(seed=True)
    app.dependency_overrides[get_store] = lambda: seeded_store
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
