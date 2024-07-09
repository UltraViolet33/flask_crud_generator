.. Flask-CRUDGenerator documentation master file, created by
   sphinx-quickstart on Tue Jul  9 16:15:45 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Flask Crud Generator
====================

Allow you to generate CRUD routes based on your models in a Flask application.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Example
-------

.. code-block:: python

    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from flask_crud_generator import CRUDGenerator

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)
    crud = CRUDGenerator(app, db)

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(80))
        email = db.Column(db.String(120), unique=True)

        def to_dict(self):
            return {'id': self.id, 'name': self.name, 'email': self.email}

    class Product(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(80))

        def to_dict(self):
            return {'id': self.id, 'name': self.name}

    crud.generate_routes(User)
    crud.generate_routes(Product)

    with app.app_context():
        db.create_all()

    if __name__ == '__main__':
        app.run(debug=True)

Then go to `localhost:5000/user <http://localhost:5000/user>`_ or `localhost:5000/product <http://localhost:5000/product>`_.
