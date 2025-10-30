"""Tests for Role model."""

import pytest
from app.models import Role, Permission, User


class TestRoleModel:
    """Test Role model functionality."""

    def test_role_creation(self, db):
        """Test creating a role."""
        role = Role(name='Manager', guard_name='web')
        db.session.add(role)
        db.session.commit()

        assert role.id is not None
        assert role.name == 'Manager'
        assert role.guard_name == 'web'
        assert role.created_at is not None
        assert role.updated_at is not None

    def test_role_default_guard_name(self, db):
        """Test role has default guard name."""
        role = Role(name='Test Role')
        db.session.add(role)
        db.session.commit()

        assert role.guard_name == 'web'

    def test_role_name_unique(self, db, role_user):
        """Test that role name must be unique."""
        duplicate_role = Role(name=role_user.name)
        db.session.add(duplicate_role)

        with pytest.raises(Exception):  # Should raise IntegrityError
            db.session.commit()

    def test_role_repr(self, role_user):
        """Test role string representation."""
        assert repr(role_user) == '<Role User>'


class TestRolePermissions:
    """Test Role permission functionality."""

    def test_give_permission_to(self, db, role_user, permission_edit_users):
        """Test giving a permission to a role."""
        role_user.give_permission_to(permission_edit_users)
        db.session.commit()

        assert role_user.has_permission('edit users') is True
        assert permission_edit_users in role_user.permissions.all()

    def test_give_permission_idempotent(self, db, role_user, permission_view_users):
        """Test that giving same permission twice doesn't duplicate."""
        role_user.give_permission_to(permission_view_users)
        db.session.commit()

        initial_count = role_user.permissions.count()

        role_user.give_permission_to(permission_view_users)
        db.session.commit()

        assert role_user.permissions.count() == initial_count

    def test_give_multiple_permissions(self, db, role_user, permission_edit_users, permission_delete_users):
        """Test giving multiple permissions to a role."""
        role_user.give_permission_to(permission_edit_users)
        role_user.give_permission_to(permission_delete_users)
        db.session.commit()

        assert role_user.permissions.count() >= 3  # view, edit, delete
        assert role_user.has_permission('edit users') is True
        assert role_user.has_permission('delete users') is True

    def test_revoke_permission_to(self, db, role_user, permission_view_users):
        """Test revoking a permission from a role."""
        assert role_user.has_permission('view users') is True

        role_user.revoke_permission_to(permission_view_users)
        db.session.commit()

        assert role_user.has_permission('view users') is False

    def test_revoke_nonexistent_permission(self, db, role_user, permission_delete_users):
        """Test revoking a permission that role doesn't have."""
        initial_count = role_user.permissions.count()

        role_user.revoke_permission_to(permission_delete_users)
        db.session.commit()

        assert role_user.permissions.count() == initial_count

    def test_has_permission(self, role_user):
        """Test checking if role has a permission."""
        assert role_user.has_permission('view users') is True
        assert role_user.has_permission('VIEW USERS') is True
        assert role_user.has_permission('delete users') is False

    def test_sync_permissions(self, db, role_user, permission_edit_users, permission_delete_users):
        """Test syncing role permissions."""
        # Initially has view permission
        assert role_user.has_permission('view users') is True

        # Sync to only have edit and delete
        role_user.sync_permissions([permission_edit_users, permission_delete_users])
        db.session.commit()

        assert role_user.has_permission('view users') is False
        assert role_user.has_permission('edit users') is True
        assert role_user.has_permission('delete users') is True
        assert role_user.permissions.count() == 2

    def test_sync_permissions_empty_list(self, db, role_user):
        """Test syncing with empty list removes all permissions."""
        assert role_user.permissions.count() > 0

        role_user.sync_permissions([])
        db.session.commit()

        assert role_user.permissions.count() == 0


class TestRoleUsers:
    """Test Role user relationships."""

    def test_role_users_relationship(self, db, role_user, user):
        """Test that role tracks its users."""
        user.assign_role(role_user)
        db.session.commit()

        assert user in role_user.users.all()
        assert role_user.users.count() == 1

    def test_role_multiple_users(self, db, role_user):
        """Test role with multiple users."""
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

        assert role_user.users.count() == 2

    def test_role_cascade_delete(self, db, role_user, user):
        """Test that deleting a role removes user associations."""
        user.assign_role(role_user)
        db.session.commit()

        role_id = role_user.id
        db.session.delete(role_user)
        db.session.commit()

        # User should still exist
        assert User.query.get(user.id) is not None
        # But role should be gone
        assert Role.query.get(role_id) is None
        # And user should have no roles
        assert user.roles.count() == 0


class TestRolePermissionCascade:
    """Test Role permission cascade behavior."""

    def test_permission_cascade_delete(self, db, role_user, permission_view_users):
        """Test that deleting a permission removes role associations."""
        assert role_user.has_permission('view users') is True

        permission_id = permission_view_users.id
        db.session.delete(permission_view_users)
        db.session.commit()

        # Role should still exist
        assert Role.query.get(role_user.id) is not None
        # But permission should be gone
        assert Permission.query.get(permission_id) is None
        # And role should not have that permission
        assert role_user.has_permission('view users') is False
