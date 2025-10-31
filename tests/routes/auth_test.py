"""Tests for authentication routes."""

import pytest
from flask import url_for
from app.models import User



# Test login functionality.


def test_login_page_loads(client):
    """Test that login page loads successfully."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data or b'login' in response.data

def test_login_success(client, user):
    """Test successful login."""
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Login successful!' in response.data or b'Dashboard' in response.data

def test_login_invalid_email(client):
    """Test login with non-existent email."""
    response = client.post('/auth/login', data={
        'email': 'nonexistent@example.com',
        'password': 'password123'
    }, follow_redirects=True)

    assert b'Invalid email or password' in response.data

def test_login_wrong_password(client, user):
    """Test login with wrong password."""
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    assert b'Invalid email or password' in response.data

def test_login_case_insensitive_email(client, user):
    """Test that login email is case insensitive."""
    response = client.post('/auth/login', data={
        'email': 'TEST@EXAMPLE.COM',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Login successful!' in response.data or b'Dashboard' in response.data

def test_login_redirects_authenticated_user(authenticated_client):
    """Test that authenticated users are redirected from login page."""
    response = authenticated_client.get('/auth/login')
    assert response.status_code == 302  # Redirect

def test_login_remember_me(client, user):
    """Test remember me functionality."""
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123',
        'remember': True
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Login successful!' in response.data or b'Dashboard' in response.data

def test_login_next_parameter(client, user):
    """Test that next parameter works after login."""
    response = client.post('/auth/login?next=/users/', data={
        'email': 'test@example.com',
        'password': 'password123'
    })

    # Should redirect to next page
    assert response.status_code == 302

def test_login_empty_fields(client):
    """Test login with empty fields."""
    response = client.post('/auth/login', data={
        'email': '',
        'password': ''
    })

    assert response.status_code == 200  # Form validation error, stays on page



# Test registration functionality.


def test_register_page_loads(client):
    """Test that register page loads successfully."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register' in response.data or b'register' in response.data

def test_register_success(client, db):
    """Test successful registration."""
    response = client.post('/auth/register', data={
        'name': 'New User',
        'email': 'newuser@example.com',
        'password': 'password123',
        'password_confirm': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Registration successful!' in response.data

    # Verify user was created in database
    user = User.query.filter_by(email='newuser@example.com').first()
    assert user is not None
    assert user.name == 'New User'

def test_register_duplicate_email(client, user):
    """Test registration with existing email."""
    response = client.post('/auth/register', data={
        'name': 'Another User',
        'email': 'test@example.com',
        'password': 'password123',
        'password_confirm': 'password123'
    })

    assert b'Email already registered' in response.data

def test_register_email_case_insensitive(client, user):
    """Test that email uniqueness is case insensitive."""
    response = client.post('/auth/register', data={
        'name': 'Another User',
        'email': 'TEST@EXAMPLE.COM',
        'password': 'password123',
        'password_confirm': 'password123'
    })

    assert b'Email already registered' in response.data

def test_register_password_mismatch(client):
    """Test registration with mismatched passwords."""
    response = client.post('/auth/register', data={
        'name': 'New User',
        'email': 'newuser@example.com',
        'password': 'password123',
        'password_confirm': 'differentpassword'
    })

    assert b'Passwords must match' in response.data

def test_register_short_password(client):
    """Test registration with too short password."""
    response = client.post('/auth/register', data={
        'name': 'New User',
        'email': 'newuser@example.com',
        'password': 'short',
        'password_confirm': 'short'
    })

    assert b'at least 8 characters' in response.data

def test_register_invalid_email(client):
    """Test registration with invalid email format."""
    response = client.post('/auth/register', data={
        'name': 'New User',
        'email': 'notanemail',
        'password': 'password123',
        'password_confirm': 'password123'
    })

    assert response.status_code == 200  # Form validation fails, stays on page

def test_register_short_name(client):
    """Test registration with too short name."""
    response = client.post('/auth/register', data={
        'name': 'A',
        'email': 'newuser@example.com',
        'password': 'password123',
        'password_confirm': 'password123'
    })

    assert response.status_code == 200  # Form validation fails

def test_register_redirects_authenticated_user(authenticated_client):
    """Test that authenticated users are redirected from register page."""
    response = authenticated_client.get('/auth/register')
    assert response.status_code == 302  # Redirect

def test_register_email_stored_lowercase(client, db):
    """Test that email is stored in lowercase."""
    client.post('/auth/register', data={
        'name': 'New User',
        'email': 'MixedCase@Example.COM',
        'password': 'password123',
        'password_confirm': 'password123'
    }, follow_redirects=True)

    user = User.query.filter_by(email='mixedcase@example.com').first()
    assert user is not None
    assert user.email == 'mixedcase@example.com'



# Test logout functionality.


def test_logout_success(authenticated_client):
    """Test successful logout."""
    response = authenticated_client.get('/auth/logout', follow_redirects=True)

    assert response.status_code == 200
    assert b'logged out' in response.data

def test_logout_unauthenticated(client):
    """Test logout when not authenticated."""
    response = client.get('/auth/logout')
    # Should redirect to login (401 or 302)
    assert response.status_code in [302, 401]

def test_logout_clears_session(authenticated_client):
    """Test that logout clears the session."""
    # Logout
    authenticated_client.get('/auth/logout', follow_redirects=True)

    # Try to access protected page
    response = authenticated_client.get('/dashboard')
    assert response.status_code in [302, 401]  # Should redirect to login



# Test authentication integration scenarios.


def test_full_registration_and_login_flow(client, db):
    """Test complete registration and login flow."""
    # Register
    response = client.post('/auth/register', data={
        'name': 'Flow Test User',
        'email': 'flowtest@example.com',
        'password': 'password123',
        'password_confirm': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200

    # Login with the new account
    response = client.post('/auth/login', data={
        'email': 'flowtest@example.com',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Login successful!' in response.data or b'Dashboard' in response.data

def test_login_logout_login_flow(client, user):
    """Test login, logout, and login again flow."""
    # Login
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)

    # Logout
    client.get('/auth/logout', follow_redirects=True)

    # Login again
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Login successful!' in response.data or b'Dashboard' in response.data

