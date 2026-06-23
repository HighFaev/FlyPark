import os
import tempfile

os.environ.setdefault("DATABASE_URL", f"sqlite:///{os.path.join(tempfile.gettempdir(), 'flypark_test.db')}")
os.environ.setdefault("SECRET_KEY", "test-secret")

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.seed import seed


@pytest.fixture
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed(db)
    yield db
    db.close()


@pytest.fixture
def client(db_session):
    return TestClient(app)


@pytest.fixture
def employee_client(client):
    client.post(
        "/logowanie/pracownik",
        data={"email": "pracownik@flypark.pl", "haslo": "pracownik123"},
        follow_redirects=False,
    )
    return client
