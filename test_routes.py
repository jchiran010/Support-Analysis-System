import pytest
import requests
from threading import Thread
import time
from Backend.app import create_app

@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False
    })
    yield app

@pytest.fixture(scope="module")
def client(app):
    return app.test_client()

def test_routes(client):
    res = client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
    assert res.status_code == 200
    
    for route in ['/dashboard', '/complaints', '/analytics', '/reports', '/users', '/notifications', '/settings']:
        r = client.get(route)
        assert r.status_code == 200
