"""Tests for app initialization and Flask-Login integration."""

import pytest


def test_user_loader_loads_existing_user(app, db, user):
    """Test that user loader loads an existing user."""
    from app.models import User
    
    with app.test_request_context():
        # Get the actual user_loader callback function
        user_loader_callback = app.login_manager._user_callback
        
        # Load user through Flask-Login's user_loader
        loaded_user = user_loader_callback(str(user.id))
        
        assert loaded_user is not None
        assert loaded_user.id == user.id
        assert loaded_user.email == user.email

def test_user_loader_returns_none_for_invalid_id(app, db):
    """Test that user loader returns None for invalid user ID."""
    from app.models import User
    
    with app.test_request_context():
        # Get the actual user_loader callback function
        user_loader_callback = app.login_manager._user_callback
        
        # Try to load non-existent user
        loaded_user = user_loader_callback('99999')
        
        assert loaded_user is None

def test_user_loader_with_authenticated_session(client, user):
    """Test that user loader works with authenticated session."""
    # Login the user
    response = client.post('/auth/login', data={
        'email': user.email,
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Make another request - this will use the user_loader
    response = client.get('/dashboard')
    assert response.status_code == 200
