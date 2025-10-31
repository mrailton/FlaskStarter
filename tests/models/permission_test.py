"""Tests for Permission model."""

import pytest
from app.models import Permission, Role, User



# Test Permission model functionality.


def test_permission_creation(db):
    """Test creating a permission."""
    permission = Permission(name='view posts', guard_name='web')
    db.session.add(permission)
    db.session.commit()

    assert permission.id is not None
    assert permission.name == 'view posts'
    assert permission.guard_name == 'web'
    assert permission.created_at is not None
    assert permission.updated_at is not None

def test_permission_default_guard_name(db):
    """Test permission has default guard name."""
    permission = Permission(name='test permission')
    db.session.add(permission)
    db.session.commit()

    assert permission.guard_name == 'web'

def test_permission_name_unique(db, permission_view_users):
    """Test that permission name must be unique."""
    duplicate_permission = Permission(name=permission_view_users.name)
    db.session.add(duplicate_permission)

    with pytest.raises(Exception):  # Should raise IntegrityError
        db.session.commit()

def test_permission_repr(permission_view_users):
    """Test permission string representation."""
    assert repr(permission_view_users) == '<Permission view users>'



# Test Permission role relationships.


def test_assign_to_role(db, permission_view_users, role_editor):
    """Test assigning a permission to a role."""
    permission_view_users.assign_to_role(role_editor)
    db.session.commit()

    assert role_editor in permission_view_users.roles.all()
    assert role_editor.has_permission('view users') is True

def test_assign_to_role_idempotent(db, permission_view_users, role_user):
    """Test that assigning to same role twice doesn't duplicate."""
    initial_count = permission_view_users.roles.count()

    permission_view_users.assign_to_role(role_user)
    db.session.commit()

    assert permission_view_users.roles.count() == initial_count

def test_assign_to_role_new_role(db):
    """Test assigning a permission to a new role that it doesn't have yet."""
    from app.models import Permission, Role
    
    # Create a new permission and role without pre-existing relationship
    permission = Permission(name='test permission')
    role = Role(name='Test Role')
    db.session.add(permission)
    db.session.add(role)
    db.session.commit()
    
    # Verify no relationship exists
    assert permission.roles.count() == 0
    
    # Assign permission to role
    permission.assign_to_role(role)
    db.session.commit()
    
    # Verify relationship was created
    assert permission.roles.count() == 1
    assert role in permission.roles.all()

def test_assign_to_multiple_roles(db, permission_view_users, role_user, role_editor):
    """Test assigning permission to multiple roles."""
    permission_view_users.assign_to_role(role_user)
    permission_view_users.assign_to_role(role_editor)
    db.session.commit()

    assert permission_view_users.roles.count() >= 2
    assert role_user.has_permission('view users') is True
    assert role_editor.has_permission('view users') is True

def test_remove_from_role(db, permission_view_users, role_user):
    """Test removing a permission from a role."""
    assert role_user.has_permission('view users') is True

    permission_view_users.remove_from_role(role_user)
    db.session.commit()

    assert role_user.has_permission('view users') is False
    assert role_user not in permission_view_users.roles.all()

def test_remove_from_role_not_assigned(db, permission_delete_users, role_user):
    """Test removing permission from role that doesn't have it."""
    initial_count = permission_delete_users.roles.count()

    permission_delete_users.remove_from_role(role_user)
    db.session.commit()

    assert permission_delete_users.roles.count() == initial_count



# Test Permission cascade behavior.


def test_role_cascade_delete(db, permission_view_users, role_user):
    """Test that deleting a role removes permission associations."""
    assert permission_view_users.roles.count() >= 1

    initial_role_count = permission_view_users.roles.count()
    role_id = role_user.id

    db.session.delete(role_user)
    db.session.commit()

    # Permission should still exist
    assert db.session.get(Permission, permission_view_users.id) is not None
    # Role should be gone
    assert db.session.get(Role, role_id) is None
    # Permission should have one less role
    assert permission_view_users.roles.count() == initial_role_count - 1



# Test Permission integration with users through roles.


def test_permission_affects_users(db, permission_view_users, role_user):
    """Test that permission changes affect users through roles."""
    user = User(name='Test User', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.flush()

    user.assign_role(role_user)
    db.session.commit()

    # User should have permission through role
    assert user.has_permission('view users') is True

    # Remove permission from role
    permission_view_users.remove_from_role(role_user)
    db.session.commit()

    # User should no longer have permission
    assert user.has_permission('view users') is False

def test_permission_multiple_users_through_role(db, permission_view_users, role_user):
    """Test that permission affects multiple users through a role."""
    user1 = User(name='User 1', email='user1@example.com')
    user1.set_password('password')
    user2 = User(name='User 2', email='user2@example.com')
    user2.set_password('password')

    db.session.add(user1)
    db.session.add(user2)
    db.session.flush()

    user1.assign_role(role_user)
    user2.assign_role(role_user)
    db.session.commit()

    # Both users should have permission
    assert user1.has_permission('view users') is True
    assert user2.has_permission('view users') is True

    # Remove permission from role
    permission_view_users.remove_from_role(role_user)
    db.session.commit()

    # Neither user should have permission
    assert user1.has_permission('view users') is False
    assert user2.has_permission('view users') is False

def test_permission_across_multiple_roles(db, permission_view_users, role_user, role_editor):
    """Test permission assigned to multiple roles."""
    user1 = User(name='User 1', email='user1@example.com')
    user1.set_password('password')
    user2 = User(name='User 2', email='user2@example.com')
    user2.set_password('password')

    db.session.add(user1)
    db.session.add(user2)
    db.session.flush()

    user1.assign_role(role_user)
    user2.assign_role(role_editor)
    db.session.commit()

    # Both users should have the permission through different roles
    assert user1.has_permission('view users') is True
    assert user2.has_permission('view users') is True

