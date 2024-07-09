from flask import Flask
from flask.testing import FlaskClient
from flask_crud_generator import CRUDGenerator
from tests.models import db
from tests.models import User
from tests.models import Product


def create_app(m=None, conf=None):
    _app = Flask(__name__)
    _app.config["DEBUG"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    _app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    _app.config["ERROR_FORCE_CONTENT_TYPE"] = False
    _app.config.update(**(conf or {}))

    with _app.app_context():
        db.init_app(_app)
        db.create_all()
        crud = CRUDGenerator(_app, db)
        crud.generate_routes(User)
        crud.generate_routes(Product)

    _app.testing = True
    return _app
