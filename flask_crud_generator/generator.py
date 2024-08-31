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

        def to_dict(instance):
            columns = [c.key for c in class_mapper(instance.__class__).columns]
            relationships = [r.key for r in class_mapper(instance.__class__).relationships]
            result = {c: getattr(instance, c) for c in columns}
            for r in relationships:
                related_obj = getattr(instance, r)
                if related_obj:
                    if isinstance(related_obj, list):
                        result[r] = [to_dict(item) for item in related_obj]
                    else:
                        result[r] = to_dict(related_obj)
            return result
    
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
        
        @blueprint.route("/edit/<int:item_id>", methods=["GET", "POST"])
        def edit_item_web(item_id):
            model_class = globals().get(model)
            model_class = model

            item = model.query.get_or_404(item_id)

            relationships, related_data = self.get_related_data(model_class)

            if request.method == 'POST':
                 # Get the form data (use request.json for JSON data)
                form_data = request.form.to_dict()  # or request.get_json() for API routes

                # Get model columns
                model_columns = {column.name for column in model.__table__.columns}
                
                # Update the item's attributes with the new values from form_data
                for key, value in form_data.items():
                    if key in model_columns:
                        setattr(item, key, value)

                # Handle many-to-many relationships if any
                for relationship in model.__mapper__.relationships:
                    if relationship.secondary is not None:  # It's a many-to-many relationship
                        related_ids = request.form.getlist(relationship.key)
                        if related_ids:
                            related_items = relationship.mapper.class_.query.filter(
                                relationship.mapper.class_.id.in_(related_ids)
                            ).all()
                            setattr(item, relationship.key, related_items)

                # Commit the changes to the database
                self.db.session.commit()
                return redirect(url_for(f"{blueprint_name}.get_item_web",item_id=item_id))

            return render_template('edit.html', item=item.to_dict(), columns=model.__table__.columns, related_data=related_data, relationships=relationships)     

        @blueprint.route("/create/", methods=["GET", "POST"])
        def create_item_web():
            model_class = globals().get(model)
            model_class = model

            relationships, related_data = self.get_related_data(model_class)
            print(related_data)

            if request.method == 'POST':
                form_data = request.form.to_dict()
                model_columns = {column.name for column in model.__table__.columns}
                filtered_data = {key: form_data[key] for key in model_columns if key in form_data}
                try:
                    item = model(**filtered_data)                    
                    self.db.session.add(item)
                     # Traiter les relations many-to-many
                    for relationship in model.__mapper__.relationships:
                        if relationship.secondary is not None:  # C'est une relation many-to-many
                            related_ids = request.form.getlist(relationship.key)
                            if related_ids:
                                related_items = relationship.mapper.class_.query.filter(
                                    relationship.mapper.class_.id.in_(related_ids)
                                ).all()
                                print(related_items)
                                getattr(item, relationship.key).extend(related_items)

                    # Commit les changements dans la base de données
                    self.db.session.commit()
                    return redirect(url_for(f"{blueprint_name}.list_items_web"))
                except Exception as e:
                    self.db.session.rollback()
                    print(e)
                    return render_template('create.html',  columns=model.__table__.columns), 500
            print(relationships)
            return render_template('create.html',  columns=model.__table__.columns, related_data=related_data, relationships=relationships)
            
        @blueprint.route("/<int:item_id>", methods=["GET"])
        def get_item_web(item_id):
            item = model.query.get_or_404(item_id)
            return render_template('details.html', item=item, model_name=model_name.capitalize())

        if blueprint_name not in self.app.blueprints:
            self.app.register_blueprint(blueprint, url_prefix=f"/{blueprint_name}")


    def generate_api_routes(self, model, blueprint=None, blueprint_name=None):
        model_name = model.__name__.lower()

        if blueprint_name is None:
            blueprint_name = model_name

        if blueprint is None:
            blueprint = Blueprint(model_name, __name__)

        @blueprint.route("/api/", methods=["GET"])
        def list_items_api():
            items = model.query.all()
            return jsonify([item.to_dict() for item in items])

        @blueprint.route("/api/<int:item_id>", methods=["GET"])
        def get_item_api(item_id):
            item = model.query.get_or_404(item_id)
            return jsonify(item.to_dict())

        @blueprint.route("/api/", methods=["POST"])
        def create_item_api():
            data = request.get_json()
            item = model(**data)
            self.db.session.add(item)
            self.db.session.commit()
            return jsonify(item.to_dict()), 201

        @blueprint.route("/api/<int:item_id>", methods=["PUT"])
        def update_item_api(item_id):
            data = request.get_json()
            item = model.query.get_or_404(item_id)
            for key, value in data.items():
                setattr(item, key, value)
            self.db.session.commit()
            return jsonify(item.to_dict())

        @blueprint.route("/api/<int:item_id>", methods=["DELETE"])
        def delete_item_api(item_id):
            item = model.query.get_or_404(item_id)
            self.db.session.delete(item)
            self.db.session.commit()
            return "", 204

        self.app.register_blueprint(blueprint, url_prefix=f"/{blueprint_name}")


    def get_related_data(self, model_class):
        related_data = {}
        relationships = []

        for relationship in model_class.__mapper__.relationships:
            print(relationship)
            if relationship.secondary is not None:  # many to many relation
                related_model_class = relationship.mapper.class_
                related_data[relationship.key] = related_model_class.query.all()
                relationships.append(relationship)

            for column in model_class.__table__.columns:
                if column.foreign_keys:                    
                    for relationship in model_class.__mapper__.relationships:
                        if relationship.local_remote_pairs[0][0].name == column.name:
                            related_model_class = relationship.mapper.class_
                            related_data[column.name] = related_model_class.query.all()
                            break
        return [relationships, related_data]

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