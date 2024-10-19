from flask import Blueprint, request, jsonify, render_template, redirect, url_for
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

    def generate_web_routes(
        self,
        model,
        blueprint=None,
        blueprint_name=None,
        form_class=None,
        create_edit_form=None,
        list_config=None,
    ):
        self.copy_templates_to_app()
        model_name = model.__name__.lower()

        if list_config is None:
            list_config = {
                "keys": None,
                "details_property_on": "",
                "unique_identifier": "",
            }

        if list_config["keys"] is None:
            # add to keys every property of the model
            list_config["keys"] = [column.name for column in model.__table__.columns]

        if blueprint_name is None:
            blueprint_name = model_name

        if blueprint is None:
            blueprint = Blueprint(model_name, __name__)


        def get_nav_links(blueprint_name):
            return [
                {"name":"List", "url": f"{blueprint_name}.list_items_web"},
                {"name":"Create", "url": f"{blueprint_name}.create_item_web"},
            ]

        @blueprint.route("/", methods=["GET"])
        def list_items_web():
            items = model.query.all()
            details_url = f"{blueprint_name}.get_item_web"

            return render_template(
                "list.html",
                items=items,
                keys=list_config["keys"],
                list_config=list_config,
                model_name=model_name.capitalize(),
                details_url=details_url,
                nav_links=get_nav_links(blueprint_name),
            )

        @blueprint.route("/<int:item_id>", methods=["GET"])
        def get_item_web(item_id):
            item = model.query.get_or_404(item_id)
            edit_url = f"{blueprint_name}.edit_item_web"
            return render_template(
                "details.html",
                item=item,
                model_name=model_name.capitalize(),
                edit_url=edit_url,
nav_links=get_nav_links(blueprint_name),
            )

        @blueprint.route("/create/", methods=["GET", "POST"])
        def create_item_web():
            if form_class is not None:
                form = form_class()

                if form.validate_on_submit():
                    data = form.data
                    del data["csrf_token"]
                    item = model(**data)

                    self.db.session.add(item)
                    self.db.session.commit()
                    # flash(f'{model_name.capitalize()} created successfully!', 'success')
                    return redirect(url_for(f"{blueprint_name}.list_items_web"))
                return render_template(
                    "wtf_create.html",
                    form=form,
                    model_name=model_name.capitalize(),
                    action="Create",
                   nav_links=get_nav_links(blueprint_name),
                )

            else:
                if request.method == "POST":
                    form_data = request.form.to_dict()
                    model_columns = {column.name for column in model.__table__.columns}
                    filtered_data = {
                        key: form_data[key] for key in model_columns if key in form_data
                    }
                    try:
                        item = model(**filtered_data)
                        self.db.session.add(item)
                        self.db.session.commit()
                        return redirect(url_for(f"{blueprint_name}.list_items_web"))
                    except Exception as e:
                        self.db.session.rollback()
                        return render_template(
                            "create.html",
                            columns=model.__table__.columns,
                        nav_links=get_nav_links(blueprint_name),
                        )
                return render_template(
                    "create.html",
                    columns=model.__table__.columns,
           nav_links=get_nav_links(blueprint_name),
                )

        @blueprint.route("/edit/<int:item_id>", methods=["GET", "POST"])
        def edit_item_web(item_id):
            item = model.query.get_or_404(item_id)
            if form_class is not None:
                form = create_edit_form(item)

                if form.validate_on_submit():
                    data = form.data

                    del data["csrf_token"]
                    for key, value in data.items():
                        setattr(item, key, value)

                    self.db.session.commit()
                    # flash(f'{model_name.capitalize()} updated successfully!', 'success')
                    return redirect(url_for(f"{model_name}.list_items_web"))
                return render_template(
                    f"wtf_create.html",
                    form=form,
                    model_name=model_name.capitalize(),
                    action="Edit",
              nav_links=get_nav_links(blueprint_name),
                )
            else:

                if request.method == "POST":
                    form_data = request.form.to_dict()
                    model_columns = {column.name for column in model.__table__.columns}
                    try:
                        for key, value in form_data.items():
                            if key in model_columns:
                                setattr(item, key, value)
                        self.db.session.commit()
                        return redirect(url_for(f"{blueprint_name}.list_items_web"))
                    except Exception as e:
                        self.db.session.rollback()
                return render_template(
                    "edit.html",
                    columns=model.__table__.columns,
                    item=item,
                  nav_links=get_nav_links(blueprint_name),
                )

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
        package_templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        app_templates_dir = os.path.join(self.app.root_path, "templates")

        if not os.path.exists(app_templates_dir):
            os.makedirs(app_templates_dir)

        for filename in os.listdir(package_templates_dir):
            # copy the files and directories
            source_file = os.path.join(package_templates_dir, filename)
            destination_file = os.path.join(app_templates_dir, filename)

            if os.path.isfile(source_file):
                shutil.copy(source_file, destination_file)



    