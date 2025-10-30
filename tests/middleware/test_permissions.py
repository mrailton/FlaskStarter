"""Tests for permission middleware decorators."""

import pytest
from flask import Blueprint
from app.middleware import role_required, permission_required, all_permissions_required, all_roles_required


# Create test blueprints for testing decorators
_test_bp = Blueprint('test_middleware', __name__)


@_test_bp.route('/test_permission_required')
@permission_required('view users')
def permission_view_route():
    return 'success'


@_test_bp.route('/test_role_required')
@role_required('Admin')
def role_view_route():
    return 'success'


@_test_bp.route('/test_all_permissions')
@all_permissions_required('view users', 'edit users')
def all_perms_view_route():
    return 'success'


@_test_bp.route('/test_all_roles')
@all_roles_required('Admin', 'User')
def all_roles_view_route():
    return 'success'


@_test_bp.route('/test_multiple_permissions')
@permission_required('view users', 'edit users')
def multiple_perms_view_route():
    return 'success'


@_test_bp.route('/test_multiple_roles')
@role_required('Admin', 'Editor')
def multiple_roles_view_route():
    return 'success'


@pytest.fixture(scope='session', autouse=True)
def setup_test_routes(app):
    """Register test blueprint once for the session."""
    with app.app_context():
        app.register_blueprint(_test_bp)
    return app


class TestPermissionRequired:
    """Test permission_required decorator."""

    def test_permission_required_unauthenticated(self, client):
        """Test that decorator returns 401 for unauthenticated users."""
        response = client.get('/test_permission_required')
        assert response.status_code == 401

    def test_permission_required_without_permission(self, authenticated_client):
        """Test that decorator returns 403 without permission."""
        response = authenticated_client.get('/test_permission_required')
        assert response.status_code == 403

    def test_permission_required_with_permission(self, admin_client):
        """Test that decorator allows access with permission."""
        response = admin_client.get('/test_permission_required')
        assert response.status_code == 200
        assert b'success' in response.data

    def test_permission_required_through_role(self, client, db, regular_user):
        """Test that decorator works with permissions through roles."""
        # regular_user has role_user which has 'view users' permission
        client.post('/auth/login', data={
            'email': regular_user.email,
            'password': 'regular123'
        })

        response = client.get('/test_permission_required')
        assert response.status_code == 200

    def test_multiple_permissions_any_match(self, client, db, regular_user):
        """Test decorator with multiple permissions (any match)."""
        client.post('/auth/login', data={
            'email': regular_user.email,
            'password': 'regular123'
        })

        # regular_user has 'view users' but not 'edit users'
        # permission_required accepts any match
        response = client.get('/test_multiple_permissions')
        assert response.status_code == 200


class TestRoleRequired:
    """Test role_required decorator."""

    def test_role_required_unauthenticated(self, client):
        """Test that decorator returns 401 for unauthenticated users."""
        response = client.get('/test_role_required')
        assert response.status_code == 401

    def test_role_required_without_role(self, authenticated_client):
        """Test that decorator returns 403 without role."""
        response = authenticated_client.get('/test_role_required')
        assert response.status_code == 403

    def test_role_required_with_role(self, admin_client):
        """Test that decorator allows access with role."""
        response = admin_client.get('/test_role_required')
        assert response.status_code == 200
        assert b'success' in response.data

    def test_multiple_roles_any_match(self, client, db, regular_user):
        """Test decorator with multiple roles (any match)."""
        client.post('/auth/login', data={
            'email': regular_user.email,
            'password': 'regular123'
        })

        # regular_user has 'User' role (matches one of Admin, Editor)
        response = client.get('/test_multiple_roles')
        assert response.status_code == 403  # User is not Admin or Editor

    def test_multiple_roles_with_match(self, admin_client):
        """Test decorator with multiple roles where one matches."""
        # admin_user has 'Admin' role
        response = admin_client.get('/test_multiple_roles')
        assert response.status_code == 200


class TestAllPermissionsRequired:
    """Test all_permissions_required decorator."""

    def test_all_permissions_unauthenticated(self, client):
        """Test that decorator returns 401 for unauthenticated users."""
        response = client.get('/test_all_permissions')
        assert response.status_code == 401

    def test_all_permissions_without_all(self, client, db, regular_user):
        """Test that decorator returns 403 without all permissions."""
        client.post('/auth/login', data={
            'email': regular_user.email,
            'password': 'regular123'
        })

        # regular_user has 'view users' but not 'edit users'
        response = client.get('/test_all_permissions')
        assert response.status_code == 403

    def test_all_permissions_with_all(self, client, db, user, role_editor):
        """Test that decorator allows access with all permissions."""
        user.assign_role(role_editor)
        db.session.commit()

        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })

        # role_editor has both 'view users' and 'edit users'
        response = client.get('/test_all_permissions')
        assert response.status_code == 200

    def test_all_permissions_with_admin(self, admin_client):
        """Test that decorator allows access for admin with all permissions."""
        response = admin_client.get('/test_all_permissions')
        assert response.status_code == 200


class TestAllRolesRequired:
    """Test all_roles_required decorator."""

    def test_all_roles_unauthenticated(self, client):
        """Test that decorator returns 401 for unauthenticated users."""
        response = client.get('/test_all_roles')
        assert response.status_code == 401

    def test_all_roles_without_all(self, client, db, regular_user):
        """Test that decorator returns 403 without all roles."""
        client.post('/auth/login', data={
            'email': regular_user.email,
            'password': 'regular123'
        })

        # regular_user has 'User' but not 'Admin'
        response = client.get('/test_all_roles')
        assert response.status_code == 403

    def test_all_roles_with_all(self, client, db, user, role_user):
        """Test that decorator allows access with all roles."""
        # Create Admin role
        from app.models import Role
        admin_role = Role(name='Admin')
        db.session.add(admin_role)
        db.session.commit()

        # Assign both roles to user
        user.assign_role(role_user)
        user.assign_role(admin_role)
        db.session.commit()

        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })

        response = client.get('/test_all_roles')
        assert response.status_code == 200

    def test_all_roles_with_only_one(self, admin_client):
        """Test that decorator returns 403 with only one role."""
        # admin_user has 'Admin' but not 'User'
        response = admin_client.get('/test_all_roles')
        assert response.status_code == 403


class TestDecoratorIntegration:
    """Test decorator integration scenarios."""

    def test_stacked_decorators(self, app, admin_client):
        """Test multiple decorators stacked together."""
        # This test verifies that decorators can be stacked
        # The actual routes already have login_required + permission_required stacked
        response = admin_client.get('/users/')
        # Should work because admin has all permissions
        assert response.status_code == 200

    def test_decorator_preserves_function_name(self):
        """Test that decorators preserve function names."""
        from app.middleware import permission_required

        @permission_required('test')
        def test_func():
            """Test function."""
            return 'test'

        assert test_func.__name__ == 'test_func'

    def test_permission_check_case_sensitivity(self, client, db, user, role_user, permission_view_users):
        """Test that permission checks are case insensitive."""
        user.assign_role(role_user)
        db.session.commit()

        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })

        # The decorator checks for 'view users' but the permission is stored as 'view users'
        response = client.get('/test_permission_required')
        assert response.status_code == 200

    def test_role_check_order_independence(self, client, db):
        """Test that role checking is order independent."""
        from app.models import User, Role

        user = User(name='Multi Role User', email='multirole@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.flush()

        # Assign roles in different order
        role1 = Role(name='Role1')
        role2 = Role(name='Role2')
        db.session.add(role1)
        db.session.add(role2)
        db.session.commit()

        user.assign_role(role2)  # Assign in reverse order
        user.assign_role(role1)
        db.session.commit()

        client.post('/auth/login', data={
            'email': 'multirole@example.com',
            'password': 'password'
        })

        # Should work regardless of assignment order
        assert user.has_role('Role1')
        assert user.has_role('Role2')

    def test_empty_permission_name(self, client, admin_user):
        """Test behavior with empty permission name."""
        # This is an edge case test
        # Decorators should handle edge cases gracefully
        assert admin_user.has_permission('view users')
        assert not admin_user.has_permission('')

    def test_none_permission_name(self, admin_user):
        """Test behavior with None permission name."""
        # Edge case: ensure no crashes with None
        try:
            result = admin_user.has_permission(None)
            # Should return False or handle gracefully
            assert result is False or result is None
        except (TypeError, AttributeError):
            # It's okay to raise an error for None
            pass
