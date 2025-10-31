"""Tests for User model."""

import pytest
from app.models import User, Role, Permission
from datetime import datetime



# Test User model functionality.


def test_user_creation(db):
    """Test creating a user."""
    user = User(name='John Doe', email='john@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    assert user.id is not None
    assert user.name == 'John Doe'
    assert user.email == 'john@example.com'
    assert user.password != 'password123'  # Password should be hashed
    assert user.created_at is not None
    assert user.updated_at is not None

def test_user_email_unique(db, user):
    """Test that email must be unique."""
    duplicate_user = User(name='Another User', email=user.email)
    duplicate_user.set_password('password456')
    db.session.add(duplicate_user)

    with pytest.raises(Exception):  # Should raise IntegrityError
        db.session.commit()

def test_set_password(db):
    """Test password hashing."""
    user = User(name='Test', email='test@example.com')
    user.set_password('mypassword')

    assert user.password != 'mypassword'
    assert len(user.password) > 0
    assert '$2b$' in user.password  # bcrypt hash identifier

def test_check_password_correct(user):
    """Test checking correct password."""
    assert user.check_password('password123') is True

def test_check_password_incorrect(user):
    """Test checking incorrect password."""
    assert user.check_password('wrongpassword') is False

def test_check_password_case_sensitive(user):
    """Test that password check is case sensitive."""
    assert user.check_password('PASSWORD123') is False

def test_user_repr(user):
    """Test user string representation."""
    assert repr(user) == '<User test@example.com>'



# Test User role functionality.


def test_assign_role(db, user, role_user):
    """Test assigning a role to a user."""
    user.assign_role(role_user)
    db.session.commit()

    assert user.has_role('User') is True
    assert role_user in user.roles.all()

def test_assign_role_idempotent(db, user, role_user):
    """Test that assigning same role twice doesn't duplicate."""
    user.assign_role(role_user)
    user.assign_role(role_user)
    db.session.commit()

    assert user.roles.count() == 1

def test_assign_multiple_roles(db, user, role_user, role_editor):
    """Test assigning multiple roles to a user."""
    user.assign_role(role_user)
    user.assign_role(role_editor)
    db.session.commit()

    assert user.roles.count() == 2
    assert user.has_role('User') is True
    assert user.has_role('Editor') is True

def test_remove_role(db, user, role_user):
    """Test removing a role from a user."""
    user.assign_role(role_user)
    db.session.commit()

    user.remove_role(role_user)
    db.session.commit()

    assert user.has_role('User') is False
    assert user.roles.count() == 0

def test_has_role(db, user, role_user):
    """Test checking if user has a role."""
    assert user.has_role('User') is False

    user.assign_role(role_user)
    db.session.commit()

    assert user.has_role('User') is True
    assert user.has_role('user') is True
    assert user.has_role('Admin') is False

def test_has_any_role(db, user, role_user):
    """Test checking if user has any of specified roles."""
    user.assign_role(role_user)
    db.session.commit()

    assert user.has_any_role('Admin', 'User') is True
    assert user.has_any_role('Admin', 'Editor') is False

def test_has_any_role_case_insensitive(db, user, role_user):
    """Test has_any_role is case insensitive."""
    user.assign_role(role_user)
    db.session.commit()

    assert user.has_any_role('admin', 'user') is True

def test_has_all_roles(db, user, role_user, role_editor):
    """Test checking if user has all specified roles."""
    user.assign_role(role_user)
    user.assign_role(role_editor)
    db.session.commit()

    assert user.has_all_roles('User', 'Editor') is True
    assert user.has_all_roles('User', 'Admin') is False

def test_has_all_roles_case_insensitive(db, user, role_user, role_editor):
    """Test has_all_roles is case insensitive."""
    user.assign_role(role_user)
    user.assign_role(role_editor)
    db.session.commit()

    assert user.has_all_roles('user', 'editor') is True



# Test User permission functionality.


def test_has_permission(db, user, role_user, permission_view_users):
    """Test checking if user has a permission through role."""
    user.assign_role(role_user)
    db.session.commit()

    assert user.has_permission('view users') is True
    assert user.has_permission('edit users') is False

def test_has_permission_no_roles(user):
    """Test that user without roles has no permissions."""
    assert user.has_permission('view users') is False

def test_has_permission_multiple_roles(db, user, role_user, role_editor):
    """Test permissions from multiple roles."""
    user.assign_role(role_user)
    user.assign_role(role_editor)
    db.session.commit()

    assert user.has_permission('view users') is True
    assert user.has_permission('edit users') is True

def test_has_any_permission(db, user, role_user):
    """Test checking if user has any of specified permissions."""
    user.assign_role(role_user)
    db.session.commit()

    assert user.has_any_permission('view users', 'edit users') is True
    assert user.has_any_permission('edit users', 'delete users') is False

def test_has_any_permission_case_insensitive(db, user, role_user):
    """Test has_any_permission is case insensitive."""
    user.assign_role(role_user)
    db.session.commit()

    assert user.has_any_permission('VIEW USERS', 'EDIT USERS') is True

def test_has_all_permissions(db, user, role_editor):
    """Test checking if user has all specified permissions."""
    user.assign_role(role_editor)
    db.session.commit()

    assert user.has_all_permissions('view users', 'edit users') is True
    assert user.has_all_permissions('view users', 'delete users') is False

def test_has_all_permissions_case_insensitive(db, user, role_editor):
    """Test has_all_permissions is case insensitive."""
    user.assign_role(role_editor)
    db.session.commit()

    assert user.has_all_permissions('VIEW USERS', 'EDIT USERS') is True

def test_get_permissions(db, user, role_editor, permission_view_users, permission_edit_users):
    """Test getting all user permissions."""
    user.assign_role(role_editor)
    db.session.commit()

    permissions = user.get_permissions()

    assert len(permissions) == 2
    permission_names = [p.name for p in permissions]
    assert 'view users' in permission_names
    assert 'edit users' in permission_names

def test_get_permissions_no_duplicates(db, user, role_user, role_editor):
    """Test that get_permissions doesn't return duplicates."""
    user.assign_role(role_user)
    user.assign_role(role_editor)
    db.session.commit()

    permissions = user.get_permissions()
    permission_ids = [p.id for p in permissions]

    # Should have unique permission IDs (no duplicates)
    assert len(permission_ids) == len(set(permission_ids))

def test_admin_has_all_permissions(admin_user, all_permissions):
    """Test that admin user has all permissions."""
    for permission in all_permissions:
        assert admin_user.has_permission(permission.name) is True



# Test User Flask-Login integration.


def test_user_is_authenticated(user):
    """Test that user is authenticated."""
    assert user.is_authenticated is True

def test_user_is_active(user):
    """Test that user is active."""
    assert user.is_active is True

def test_user_is_not_anonymous(user):
    """Test that user is not anonymous."""
    assert user.is_anonymous is False

def test_get_id(user):
    """Test getting user ID for Flask-Login."""
    assert user.get_id() == str(user.id)

