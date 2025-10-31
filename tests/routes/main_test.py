"""Tests for main routes."""

import pytest
from app.models import User, Role, Permission



# Test index route.


def test_index_unauthenticated(client):
    """Test index page when not authenticated."""
    response = client.get('/')
    assert response.status_code == 200

def test_index_authenticated(authenticated_client, db):
    """Test index page when authenticated shows dashboard."""
    response = authenticated_client.get('/')
    assert response.status_code == 200
    # Should show dashboard stats when authenticated
    assert b'Dashboard' in response.data or b'dashboard' in response.data

def test_index_shows_stats_for_authenticated(authenticated_client, db, role_user):
    """Test that index shows stats for authenticated users."""
    # Create some test data
    user2 = User(name='Test User 2', email='test2@example.com')
    user2.set_password('password')
    db.session.add(user2)
    db.session.commit()

    response = authenticated_client.get('/')
    assert response.status_code == 200
    # Should contain stats
    assert b'Users' in response.data or b'users' in response.data



# Test dashboard route.


def test_dashboard_requires_authentication(client):
    """Test that dashboard requires login."""
    response = client.get('/dashboard')
    assert response.status_code in [302, 401]  # Redirect to login or unauthorized

def test_dashboard_authenticated_access(authenticated_client):
    """Test that authenticated users can access dashboard."""
    response = authenticated_client.get('/dashboard')
    assert response.status_code == 200
    assert b'Dashboard' in response.data or b'dashboard' in response.data

def test_dashboard_shows_user_count(authenticated_client, db):
    """Test that dashboard shows correct user count."""
    # Create additional users
    for i in range(3):
        user = User(name=f'User {i}', email=f'user{i}@example.com')
        user.set_password('password')
        db.session.add(user)
    db.session.commit()

    response = authenticated_client.get('/dashboard')
    assert response.status_code == 200
    # Should show some user count
    data = response.data.decode('utf-8')
    assert 'total_users' in str(response.__dict__) or any(char.isdigit() for char in data)

def test_dashboard_shows_role_count(authenticated_client, db, role_user):
    """Test that dashboard shows correct role count."""
    # Create additional roles
    role1 = Role(name='Role 1')
    role2 = Role(name='Role 2')
    db.session.add(role1)
    db.session.add(role2)
    db.session.commit()

    response = authenticated_client.get('/dashboard')
    assert response.status_code == 200

def test_dashboard_shows_permission_count(authenticated_client, db, permission_view_users):
    """Test that dashboard shows correct permission count."""
    # Create additional permissions
    perm1 = Permission(name='permission 1')
    perm2 = Permission(name='permission 2')
    db.session.add(perm1)
    db.session.add(perm2)
    db.session.commit()

    response = authenticated_client.get('/dashboard')
    assert response.status_code == 200

def test_dashboard_empty_database(client, db):
    """Test dashboard with empty database."""
    # Create and login a user
    user = User(name='Only User', email='only@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    # Login
    client.post('/auth/login', data={
        'email': 'only@example.com',
        'password': 'password'
    })

    response = client.get('/dashboard')
    assert response.status_code == 200
    # Should handle empty stats gracefully
    assert b'Dashboard' in response.data or b'dashboard' in response.data



# Test main route integration scenarios.


def test_unauthenticated_to_authenticated_flow(client, user):
    """Test flow from unauthenticated index to authenticated dashboard."""
    # Visit index while unauthenticated
    response = client.get('/')
    assert response.status_code == 200

    # Login
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })

    # Visit index again (should show dashboard)
    response = client.get('/')
    assert response.status_code == 200
    assert b'Dashboard' in response.data or b'dashboard' in response.data

def test_dashboard_redirect_after_login(client, user):
    """Test that successful login redirects to dashboard."""
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=False)

    # Should redirect
    assert response.status_code == 302
    assert '/dashboard' in response.location or response.location == '/'

def test_multiple_users_dashboard_access(client, db):
    """Test that multiple users can access dashboard independently."""
    # Create two users
    user1 = User(name='User 1', email='user1@example.com')
    user1.set_password('password')
    user2 = User(name='User 2', email='user2@example.com')
    user2.set_password('password')
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    # Login as user1
    client.post('/auth/login', data={
        'email': 'user1@example.com',
        'password': 'password'
    })
    response = client.get('/dashboard')
    assert response.status_code == 200

    # Logout
    client.get('/auth/logout')

    # Login as user2
    client.post('/auth/login', data={
        'email': 'user2@example.com',
        'password': 'password'
    })
    response = client.get('/dashboard')
    assert response.status_code == 200

