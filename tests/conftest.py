"""Shared fixtures: every test gets a temporary SQLite file and a fake
in-memory MongoDB (mongomock), so tests never touch real data."""
import os
import sys

import mongomock
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db_connections  # noqa: E402


@pytest.fixture(autouse=True)
def temp_sqlite(tmp_path, monkeypatch):
    monkeypatch.setenv("EPT_SQLITE_PATH", str(tmp_path / "test_company.db"))


@pytest.fixture(autouse=True)
def fake_mongo(monkeypatch):
    collection = mongomock.MongoClient()["test_db"]["reviews"]
    monkeypatch.setattr(db_connections, "get_reviews_collection", lambda: collection)
    return collection


@pytest.fixture
def employee():
    import employee_manager as em
    return em.add_employee("Asha", "Rao", "asha@example.com", "2023-01-10", "Engineering")


@pytest.fixture
def project():
    import project_manager as pm
    return pm.add_project("Website", "2024-01-01")
