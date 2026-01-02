import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from exskilence_project.app import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def mock_db():
    """Mock database connection"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


# Test 1: Login Route Exists (GET)
def test_login_route_get(client):
    """Test login route is accessible via GET"""
    response = client.get('/')
    assert response.status_code == 200


# Test 2: Login Route with Invalid Credentials
def test_login_invalid_credentials(client, mock_db):
    """Test login with invalid credentials"""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = None
    
    with patch('exskilence_project.app.db', mock_conn):
        with patch('exskilence_project.app.cursor', mock_cursor):
            response = client.post('/', data={
                'username': 'invalid_user',
                'password': 'wrong_password'
            }, follow_redirects=False)
    
    assert response.status_code == 200
    assert b'Invalid credentials' in response.data or b'error' in response.data.lower()


# Test 3: Login Route with Valid Credentials
def test_login_valid_credentials(client, mock_db):
    """Test login with valid credentials"""
    mock_conn, mock_cursor = mock_db
    mock_user = {'username': 'admin', 'id': 1}
    mock_cursor.fetchone.return_value = mock_user
    
    with patch('exskilence_project.app.db', mock_conn):
        with patch('exskilence_project.app.cursor', mock_cursor):
            response = client.post('/', data={
                'username': 'admin',
                'password': 'admin123'
            }, follow_redirects=False)
    
    assert response.status_code == 302
    assert '/dashboard' in response.location or response.location.endswith('/dashboard')


# Test 4: Dashboard Route Without Session
def test_dashboard_without_session(client):
    """Test dashboard route redirects to login when not authenticated"""
    response = client.get('/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert '/' in response.location or response.location.endswith('/')


# Test 5: Dashboard Route With Session
def test_dashboard_with_session(client):
    """Test dashboard route is accessible when authenticated"""
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'admin' in response.data or b'dashboard' in response.data.lower()
