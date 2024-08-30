from . import db, Product


def test_get_web(init_database, test_client):
    prod = Product(name="test")
    db.session.add(prod)
    db.session.commit()
    res = test_client.get("/product/")
    assert res.status_code == 200


def test_get_create_page_web(init_database, test_client):
    res = test_client.get("/product/create/")
    assert res.status_code == 200
