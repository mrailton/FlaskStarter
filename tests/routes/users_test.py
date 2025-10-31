"""Tests for users routes."""

import pytest
from flask import url_for
from app.models import User, Role



# Test users list/index route.


def test_users_requires_authentication(client):
    """Test that users list requires login."""
    response = client.get('/users/')
    assert response.status_code in [302, 401]

def test_users_requires_permission(authenticated_client):
    """Test that users list requires view users permission."""
    response = authenticated_client.get('/users/')
    assert response.status_code == 403  # Forbidden

def test_users_list_with_permission(admin_client, db):
    """Test that users with permission can view list."""
    response = admin_client.get('/users/')
    assert response.status_code == 200

def test_users_list_shows_users(admin_client, db, regular_user):
    """Test that users list shows all users."""
    response = admin_client.get('/users/')
    assert response.status_code == 200
    assert b'Users' in response.data or b'users' in response.data

def test_users_search(admin_client, db):
    """Test users search functionality."""
    # Create test users
    user1 = User(name='John Doe', email='john@example.com')
    user1.set_password('password')
    user2 = User(name='Jane Smith', email='jane@example.com')
    user2.set_password('password')
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    response = admin_client.get('/users/?search=John')
    assert response.status_code == 200

def test_users_pagination(admin_client, db):
    """Test users pagination."""
    # Create multiple users
    for i in range(15):
        user = User(name=f'User {i}', email=f'user{i}@test.com')
        user.set_password('password')
        db.session.add(user)
    db.session.commit()

    response = admin_client.get('/users/?page=1&per_page=10')
    assert response.status_code == 200

def test_users_sort_by_name(admin_client, db):
    """Test users sorting by name."""
    response = admin_client.get('/users/?sort_by=name&sort_order=asc')
    assert response.status_code == 200

def test_users_sort_by_email(admin_client, db):
    """Test users sorting by email."""
    response = admin_client.get('/users/?sort_by=email&sort_order=desc')
    assert response.status_code == 200

def test_users_filter_by_role(admin_client, db, role_user):
    """Test users filtering by role."""
    response = admin_client.get(f'/users/?role={role_user.name}')
    assert response.status_code == 200



# Test user creation.


def test_create_requires_authentication(client):
    """Test that creating user requires login."""
    response = client.get('/users/create')
    assert response.status_code in [302, 401]

def test_create_requires_permission(authenticated_client):
    """Test that creating user requires create users permission."""
    response = authenticated_client.get('/users/create')
    assert response.status_code == 403

def test_create_form_loads(admin_client):
    """Test that create form loads for authorized users."""
    response = admin_client.get('/users/create')
    assert response.status_code == 200
    assert b'Create' in response.data or b'create' in response.data

def test_create_user_success(admin_client, db):
    """Test successful user creation."""
    response = admin_client.post('/users/create', data={
        'name': 'New User',
        'email': 'newuser@example.com',
        'password': 'password123',
        'roles': []
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'created successfully' in response.data

    # Verify user was created
    user = User.query.filter_by(email='newuser@example.com').first()
    assert user is not None
    assert user.name == 'New User'

def test_create_user_with_roles(admin_client, db, role_user):
    """Test creating user with roles."""
    response = admin_client.post('/users/create', data={
        'name': 'User With Role',
        'email': 'withrole@example.com',
        'password': 'password123',
        'roles': [role_user.id]
    }, follow_redirects=True)

    assert response.status_code == 200

    user = User.query.filter_by(email='withrole@example.com').first()
    assert user is not None
    assert user.has_role('User')

def test_create_user_without_password(admin_client, db):
    """Test creating user without password generates random password."""
    response = admin_client.post('/users/create', data={
        'name': 'No Password User',
        'email': 'nopass@example.com',
        'password': '',
        'roles': []
    }, follow_redirects=True)

    assert response.status_code == 200

    user = User.query.filter_by(email='nopass@example.com').first()
    assert user is not None
    assert user.password is not None
    assert len(user.password) > 0

def test_create_duplicate_email(admin_client, user):
    """Test creating user with duplicate email."""
    response = admin_client.post('/users/create', data={
        'name': 'Duplicate',
        'email': user.email,
        'password': 'password123',
        'roles': []
    })

    assert b'already registered' in response.data

def test_create_invalid_email(admin_client):
    """Test creating user with invalid email."""
    response = admin_client.post('/users/create', data={
        'name': 'Invalid Email',
        'email': 'notanemail',
        'password': 'password123',
        'roles': []
    })

    assert response.status_code == 200  # Form validation fails

def test_create_short_password(admin_client):
    """Test creating user with too short password."""
    response = admin_client.post('/users/create', data={
        'name': 'Short Pass',
        'email': 'short@example.com',
        'password': 'short',
        'roles': []
    })

    assert b'at least 8 characters' in response.data



# Test user editing.


def test_edit_requires_authentication(client, user):
    """Test that editing user requires login."""
    response = client.get(f'/users/{user.id}/edit')
    assert response.status_code in [302, 401]

def test_edit_requires_permission(authenticated_client, regular_user):
    """Test that editing user requires edit users permission."""
    response = authenticated_client.get(f'/users/{regular_user.id}/edit')
    assert response.status_code == 403

def test_edit_form_loads(admin_client, regular_user):
    """Test that edit form loads for authorized users."""
    response = admin_client.get(f'/users/{regular_user.id}/edit')
    assert response.status_code == 200
    assert b'Edit' in response.data or b'edit' in response.data

def test_edit_user_success(admin_client, db, regular_user):
    """Test successful user editing."""
    response = admin_client.post(f'/users/{regular_user.id}/edit', data={
        'name': 'Updated Name',
        'email': regular_user.email,
        'password': '',
        'roles': []
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'updated successfully' in response.data

    # Verify user was updated
    db.session.refresh(regular_user)
    assert regular_user.name == 'Updated Name'

def test_edit_user_email(admin_client, db, regular_user):
    """Test updating user email."""
    response = admin_client.post(f'/users/{regular_user.id}/edit', data={
        'name': regular_user.name,
        'email': 'newemail@example.com',
        'password': '',
        'roles': []
    }, follow_redirects=True)

    assert response.status_code == 200

    db.session.refresh(regular_user)
    assert regular_user.email == 'newemail@example.com'

def test_edit_user_password(admin_client, db, regular_user):
    """Test updating user password."""
    old_password = regular_user.password

    response = admin_client.post(f'/users/{regular_user.id}/edit', data={
        'name': regular_user.name,
        'email': regular_user.email,
        'password': 'newpassword123',
        'roles': []
    }, follow_redirects=True)

    assert response.status_code == 200

    db.session.refresh(regular_user)
    assert regular_user.password != old_password
    assert regular_user.check_password('newpassword123')

def test_edit_user_roles(admin_client, db, regular_user, role_editor):
    """Test updating user roles."""
    response = admin_client.post(f'/users/{regular_user.id}/edit', data={
        'name': regular_user.name,
        'email': regular_user.email,
        'password': '',
        'roles': [role_editor.id]
    }, follow_redirects=True)

    assert response.status_code == 200

    db.session.refresh(regular_user)
    assert regular_user.has_role('Editor')
    assert not regular_user.has_role('User')  # Old role removed

def test_edit_nonexistent_user(admin_client):
    """Test editing non-existent user."""
    response = admin_client.get('/users/99999/edit', follow_redirects=True)
    assert b'not found' in response.data

def test_edit_duplicate_email(admin_client, user, regular_user):
    """Test editing user with existing email."""
    response = admin_client.post(f'/users/{regular_user.id}/edit', data={
        'name': regular_user.name,
        'email': user.email,  # Another user's email
        'password': '',
        'roles': []
    })

    assert b'already registered' in response.data



# Test user deletion.


def test_delete_requires_authentication(client, user):
    """Test that deleting user requires login."""
    response = client.post(f'/users/{user.id}/delete')
    assert response.status_code in [302, 401]

def test_delete_requires_permission(authenticated_client, regular_user):
    """Test that deleting user requires delete users permission."""
    response = authenticated_client.post(f'/users/{regular_user.id}/delete')
    assert response.status_code == 403

def test_delete_user_success(admin_client, db, regular_user):
    """Test successful user deletion."""
    user_id = regular_user.id

    response = admin_client.post(f'/users/{user_id}/delete', follow_redirects=True)

    assert response.status_code == 200
    assert b'deleted successfully' in response.data

    # Verify user was deleted
    user = db.session.get(User, user_id)
    assert user is None

def test_delete_nonexistent_user(admin_client):
    """Test deleting non-existent user."""
    response = admin_client.post('/users/99999/delete', follow_redirects=True)
    assert b'not found' in response.data



# Test users API endpoint.


def test_api_requires_authentication(client):
    """Test that API requires login."""
    response = client.get('/users/api')
    assert response.status_code in [302, 401]

def test_api_requires_permission(authenticated_client):
    """Test that API requires view users permission."""
    response = authenticated_client.get('/users/api')
    assert response.status_code == 403

def test_api_returns_json(admin_client):
    """Test that API returns JSON data."""
    response = admin_client.get('/users/api')
    assert response.status_code == 200
    assert response.content_type == 'application/json'

def test_api_returns_users_list(admin_client, db, regular_user):
    """Test that API returns users list."""
    response = admin_client.get('/users/api')
    assert response.status_code == 200

    data = response.get_json()
    assert 'users' in data
    assert isinstance(data['users'], list)

def test_api_search(admin_client, db, regular_user):
    """Test API search functionality."""
    response = admin_client.get(f'/users/api?search={regular_user.name}')
    assert response.status_code == 200

    data = response.get_json()
    assert 'users' in data

def test_api_pagination(admin_client, db):
    """Test API pagination."""
    # Create multiple users
    for i in range(15):
        user = User(name=f'API User {i}', email=f'apiuser{i}@test.com')
        user.set_password('password')
        db.session.add(user)
    db.session.commit()

    response = admin_client.get('/users/api?page=1&per_page=10')
    assert response.status_code == 200

    data = response.get_json()
    assert 'total' in data
    assert 'pages' in data
    assert 'current_page' in data

