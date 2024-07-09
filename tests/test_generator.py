import pytest
from . import db, User


def test_app_runs(test_client):
    res = test_client.get("/")
    assert res.status_code == 404


def test_create_user(init_database, test_client):
    res = test_client.post("/user/", json={"name": "John Doe", "email": "john@example.com"})
    assert res.status_code == 201


def test_get_user(init_database, test_client):
    user = User(name="John Doe", email="john@example.com")
    db.session.add(user)
    db.session.commit()
    res = test_client.get(f"/user/{user.id}")
    assert res.status_code == 200


def test_update_user(init_database, test_client):
    user = User(name="John Doe", email="john@example.com")
    db.session.add(user)
    db.session.commit()

    updated_data = {"name": "Updated Name", "email": "updated_email@example.com"}
    res = test_client.put(f"/user/{user.id}", json=updated_data)
    
    assert res.status_code == 200
    
    updated_user = User.query.get(user.id)
    assert updated_user.name == updated_data["name"]
    assert updated_user.email == updated_data["email"]


def test_delete_user(init_database, test_client):
    user = User(name="John Doe", email="john@example.com")
    db.session.add(user)
    db.session.commit()

    res = test_client.delete(f"/user/{user.id}")
    assert res.status_code == 204

    deleted_user = User.query.get(user.id)
    assert deleted_user is None