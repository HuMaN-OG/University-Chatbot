import pytest
from app import app
from database import init_db
import json
import os

@pytest.fixture
def client():
    # Use SQLite for testing
    os.environ.pop("DATABASE_URL", None)
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

def test_home_page(client):
    rv = client.get('/')
    assert rv.status_code == 200

def test_chat_greeting(client):
    rv = client.post('/chat', json={'message': 'hello'})
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert 'responses' in data
    assert 'greeting' in data['intents']

def test_chat_farewell(client):
    rv = client.post('/chat', json={'message': 'bye'})
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert 'farewell' in data['intents']

def test_admin_login_invalid(client):
    rv = client.post('/api/admin/login', json={'password': 'wrongpassword'})
    assert rv.status_code == 401

def test_admin_login_valid(client):
    # Depending on .env, standard password is used
    admin_pass = os.environ.get("ADMIN_PASSWORD", "admin123")
    rv = client.post('/api/admin/login', json={'password': admin_pass})
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert 'token' in data

def test_protected_routes_without_token(client):
    rv = client.get('/api/responses')
    assert rv.status_code == 401
