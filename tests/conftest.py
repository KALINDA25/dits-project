import pytest
from app import create_app
from app.models import db, User

class TestConfig:
    TESTING = True
    SECRET_KEY = "test"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:" # Uses a temporary memory DB for testing
    SQLALCHEMY_TRACK_MODIFICATIONS = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        # Create a test user
        u = User(name="Test Dev", email="dev@test.com", role="developer")
        u.set_password("pass")
        db.session.add(u)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()