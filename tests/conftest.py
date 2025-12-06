"""
Pytest configuration and shared fixtures for EVOL tests.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from evol.db.models import Base


@pytest.fixture(scope="function")
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def mock_github_token(monkeypatch):
    """Mock GitHub token for testing."""
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token_for_testing_12345")


@pytest.fixture
def api_client():
    """FastAPI test client for API endpoint testing."""
    from evol.api.main import app
    return TestClient(app)


@pytest.fixture
def ui_client():
    """FastAPI test client for WebUI testing."""
    from evol.ui.app import app
    return TestClient(app)
