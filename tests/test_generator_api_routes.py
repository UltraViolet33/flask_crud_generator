from . import db, User


def test_app_runs(test_client):
    res = test_client.get("/")
    assert res.status_code == 404


def test_get_api(init_database, test_client):
    user = User(name="John Doe", email="john@example.com")
    db.session.add(user)
    db.session.commit()
    res = test_client.get(f"/user/api/{user.id}")
    assert res.status_code == 200


def test_create_api(init_database, test_client):
    res = test_client.post(
        "/user/api/", json={"name": "John Doe", "email": "john@example.com"}
    )
    assert res.status_code == 201


def test_update_api(init_database, test_client):
    user = User(name="John Doe", email="john@example.com")
    db.session.add(user)
    db.session.commit()
    updated_data = {"name": "Updated Name", "email": "updated_email@example.com"}
    res = test_client.put(f"/user/api/{user.id}", json=updated_data)
    assert res.status_code == 200
    updated_user = User.query.filter_by(id=user.id).first()
    assert updated_user.name == updated_data["name"]
    assert updated_user.email == updated_data["email"]


def test_delete_api(init_database, test_client):
    user = User(name="John Doe", email="john@example.com")
    db.session.add(user)
    db.session.commit()

    res = test_client.delete(f"/user/api/{user.id}")
    assert res.status_code == 204

    deleted_user = User.query.filter_by(id=user.id).first()
    assert deleted_user is None


def test_get_api_with_custom_blueprint(init_database, test_client):
    res = test_client.get("/categories/api/")
    assert res.status_code == 200


def test_post_api_with_custom_blueprint(init_database, test_client):
    res = test_client.post("/categories/api/", json={"id": 12, "name": "cat 1"})
    assert res.status_code == 201
