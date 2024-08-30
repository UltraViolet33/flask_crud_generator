from flask import Blueprint, request, jsonify, render_template


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
        model_name = model.__name__.lower()

        if blueprint_name is None:
            blueprint_name = model_name

        if blueprint is None:
            blueprint = Blueprint(model_name, __name__)

        @blueprint.route("/", methods=["GET"])
        def list_items_web():
            items = model.query.all()
            return render_template('index.html', items=items, model_name=model_name.capitalize())
        

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
