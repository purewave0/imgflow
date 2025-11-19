import pytest

from app import create_app
from config import TestingConfig
from app.extensions import db
from app.models.user import User


@pytest.fixture()
def app():
    app = create_app(TestingConfig)

    yield app

@pytest.fixture()
def user(app):
    with app.app_context():
        created_user = User('testuser1', 'password1')
        db.session.add(created_user)
        db.session.commit()
        yield created_user
