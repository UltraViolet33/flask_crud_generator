from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from sqlalchemy.orm import class_mapper
import shutil
import os


class CRUDGenerator:
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        if app is not None:
            self.init_app(app, db)

    def init_app(self, app, db):
        self.app = app
        self.db = db
        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["crud_generator"] = self

    def generate_web_routes(self, model, blueprint=None, blueprint_name=None):
        self.copy_templates_to_app()
        model_name = model.__name__.lower()

        if blueprint_name is None:
            blueprint_name = model_name

        if blueprint is None:
            blueprint = Blueprint(model_name, __name__)

        @blueprint.route("/", methods=["GET"])
        def list_items_web():
            items = model.query.all()
            details_url = f"{blueprint_name}.get_item_web"
            return render_template('list.html', items=items, model_name=model_name.capitalize(), details_url=details_url)

        @blueprint.route("/<int:item_id>", methods=["GET"])
        def get_item_web(item_id):
            item = model.query.get_or_404(item_id)
            return render_template('details.html', item=item, model_name=model_name.capitalize())
        

        @blueprint.route("/create/", methods=["GET", "POST"])
        def create_item_web():
            if request.method == 'POST':
                form_data = request.form.to_dict()
                model_columns = {column.name for column in model.__table__.columns}
                filtered_data = {key: form_data[key] for key in model_columns if key in form_data}
                try:
                    item = model(**filtered_data)                    
                    self.db.session.add(item)
                    self.db.session.commit()
                    return redirect(url_for(f"{blueprint_name}.list_items_web"))
                except Exception as e:
                    self.db.session.rollback()
                    return render_template('create.html',  columns=model.__table__.columns)
            return render_template('create.html',  columns=model.__table__.columns)
            
        
        self.app.register_blueprint(blueprint, url_prefix=f"/{blueprint_name}")

    def generate_routes(self, model, blueprint=None, blueprint_name=None):
        model_name = model.__name__.lower()

        if blueprint_name is None:
            blueprint_name = f"api_{model_name}"

        if blueprint is None:
            blueprint = Blueprint(blueprint_name, __name__)

        @blueprint.route("/", methods=["GET"])
        def list_items():
            items = model.query.all()
            return jsonify([item.to_dict() for item in items])

        @blueprint.route("/<int:item_id>", methods=["GET"])
        def get_item(item_id):
            item = model.query.get_or_404(item_id)
            return jsonify(item.to_dict())

        @blueprint.route("/", methods=["POST"])
        def create_item():
            data = request.get_json()
            item = model(**data)
            self.db.session.add(item)
            self.db.session.commit()
            return jsonify(item.to_dict()), 201

        @blueprint.route("/<int:item_id>", methods=["PUT"])
        def update_item(item_id):
            data = request.get_json()
            item = model.query.get_or_404(item_id)
            for key, value in data.items():
                setattr(item, key, value)
            self.db.session.commit()
            return jsonify(item.to_dict())

        @blueprint.route("/<int:item_id>", methods=["DELETE"])
        def delete_item(item_id):
            item = model.query.get_or_404(item_id)
            self.db.session.delete(item)
            self.db.session.commit()
            return "", 204

        self.app.register_blueprint(blueprint, url_prefix=f"/api/{model_name}")

    def copy_templates_to_app(self):
        package_templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        app_templates_dir = os.path.join(self.app.root_path, 'templates')

        if not os.path.exists(app_templates_dir):
            os.makedirs(app_templates_dir)

        for filename in os.listdir(package_templates_dir):
            source_file = os.path.join(package_templates_dir, filename)
            destination_file = os.path.join(app_templates_dir, filename)
            
            if os.path.isfile(source_file):
                shutil.copy(source_file, destination_file)
