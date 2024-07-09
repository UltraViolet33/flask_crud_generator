from tests.models import User, Product
from . import create_app, db
import pytest


@pytest.fixture(scope="module")
def test_client():
    flask_app = create_app()

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            yield testing_client


@pytest.fixture()
def init_database(test_client):
    db.create_all()

    yield

    db.drop_all()