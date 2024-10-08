## Flask Crud Generator

Allow you to generate CRUD routes based on your models in a Flask application

```py 
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
products = Blueprint("products", __name__)
# you can also pass a blueprint to a crud generator
crud.generate_routes(Product, products, 'products')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
```

Then go to <a href="http://localhost:5000/user">locahost:5000/user</a>
or <a href="http://localhost:5000/products">locahost:5000/product</a>


Todos : 

- [ ] Support models relationships
- [ ] Support ORM other than SQLAlchemy 
- [ ] Generate HTML views with basics forms 
- [ ] Custom data validations
- [ ] Choose which CRUD operations for which model