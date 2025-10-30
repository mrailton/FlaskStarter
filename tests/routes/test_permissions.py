"""Tests for permissions routes."""

import pytest
from app.models import Permission, Role


class TestPermissionsIndex:
    """Test permissions list/index route."""

    def test_permissions_requires_authentication(self, client):
        """Test that permissions list requires login."""
        response = client.get('/permissions/')
        assert response.status_code in [302, 401]

    def test_permissions_requires_permission(self, authenticated_client):
        """Test that permissions list requires view permissions permission."""
        response = authenticated_client.get('/permissions/')
        assert response.status_code == 403

    def test_permissions_list_with_permission(self, admin_client):
        """Test that users with permission can view list."""
        response = admin_client.get('/permissions/')
        assert response.status_code == 200

    def test_permissions_list_shows_permissions(self, admin_client, db, all_permissions):
        """Test that permissions list shows all permissions."""
        response = admin_client.get('/permissions/')
        assert response.status_code == 200
        assert b'Permissions' in response.data or b'permissions' in response.data

    def test_permissions_search(self, admin_client, db, permission_view_users):
        """Test permissions search functionality."""
        response = admin_client.get('/permissions/?search=view')
        assert response.status_code == 200

    def test_permissions_pagination(self, admin_client, db):
        """Test permissions pagination."""
        # Create multiple permissions
        for i in range(15):
            perm = Permission(name=f'permission {i}')
            db.session.add(perm)
        db.session.commit()

        response = admin_client.get('/permissions/?page=1&per_page=10')
        assert response.status_code == 200

    def test_permissions_sort_by_name_asc(self, admin_client):
        """Test permissions sorting by name ascending."""
        response = admin_client.get('/permissions/?sort_by=name&sort_order=asc')
        assert response.status_code == 200

    def test_permissions_sort_by_name_desc(self, admin_client):
        """Test permissions sorting by name descending."""
        response = admin_client.get('/permissions/?sort_by=name&sort_order=desc')
        assert response.status_code == 200


class TestPermissionsCreate:
    """Test permission creation."""

    def test_create_requires_authentication(self, client):
        """Test that creating permission requires login."""
        response = client.get('/permissions/create')
        assert response.status_code in [302, 401]

    def test_create_requires_permission(self, authenticated_client):
        """Test that creating permission requires create permissions permission."""
        response = authenticated_client.get('/permissions/create')
        assert response.status_code == 403

    def test_create_form_loads(self, admin_client):
        """Test that create form loads for authorized users."""
        response = admin_client.get('/permissions/create')
        assert response.status_code == 200
        assert b'Create' in response.data or b'create' in response.data

    def test_create_permission_success(self, admin_client, db):
        """Test successful permission creation."""
        response = admin_client.post('/permissions/create', data={
            'name': 'new permission'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'created successfully' in response.data

        # Verify permission was created
        permission = Permission.query.filter_by(name='new permission').first()
        assert permission is not None

    def test_create_duplicate_permission_name(self, admin_client, permission_view_users):
        """Test creating permission with duplicate name."""
        response = admin_client.post('/permissions/create', data={
            'name': permission_view_users.name
        })

        assert b'already exists' in response.data

    def test_create_permission_short_name(self, admin_client):
        """Test creating permission with too short name."""
        response = admin_client.post('/permissions/create', data={
            'name': 'A'
        })

        assert response.status_code == 200  # Form validation fails

    def test_create_permission_empty_name(self, admin_client):
        """Test creating permission with empty name."""
        response = admin_client.post('/permissions/create', data={
            'name': ''
        })

        assert response.status_code == 200  # Form validation fails


class TestPermissionsEdit:
    """Test permission editing."""

    def test_edit_requires_authentication(self, client, permission_view_users):
        """Test that editing permission requires login."""
        response = client.get(f'/permissions/{permission_view_users.id}/edit')
        assert response.status_code in [302, 401]

    def test_edit_requires_permission(self, authenticated_client, permission_view_users):
        """Test that editing permission requires edit permissions permission."""
        response = authenticated_client.get(f'/permissions/{permission_view_users.id}/edit')
        assert response.status_code == 403

    def test_edit_form_loads(self, admin_client, permission_view_users):
        """Test that edit form loads for authorized users."""
        response = admin_client.get(f'/permissions/{permission_view_users.id}/edit')
        assert response.status_code == 200
        assert b'Edit' in response.data or b'edit' in response.data

    def test_edit_permission_name(self, admin_client, db):
        """Test updating permission name."""
        permission = Permission(name='original permission')
        db.session.add(permission)
        db.session.commit()

        response = admin_client.post(f'/permissions/{permission.id}/edit', data={
            'name': 'updated permission'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'updated successfully' in response.data

        db.session.refresh(permission)
        assert permission.name == 'updated permission'

    def test_edit_nonexistent_permission(self, admin_client):
        """Test editing non-existent permission."""
        response = admin_client.get('/permissions/99999/edit', follow_redirects=True)
        assert b'not found' in response.data

    def test_edit_duplicate_name(self, admin_client, permission_view_users, permission_edit_users):
        """Test editing permission with existing name."""
        response = admin_client.post(f'/permissions/{permission_edit_users.id}/edit', data={
            'name': permission_view_users.name  # Another permission's name
        })

        assert b'already exists' in response.data

    def test_edit_permission_affects_roles(self, admin_client, db, role_user, permission_view_users):
        """Test that editing permission name affects roles."""
        old_name = permission_view_users.name

        # Verify role has the permission
        assert role_user.has_permission(old_name)

        # Update permission name
        admin_client.post(f'/permissions/{permission_view_users.id}/edit', data={
            'name': 'renamed permission'
        }, follow_redirects=True)

        db.session.refresh(role_user)
        db.session.refresh(permission_view_users)

        # Role should still have the permission (by relationship, not name)
        assert not role_user.has_permission(old_name)
        assert role_user.has_permission('renamed permission')


class TestPermissionsDelete:
    """Test permission deletion."""

    def test_delete_requires_authentication(self, client):
        """Test that deleting permission requires login."""
        permission = Permission(name='test delete perm')
        response = client.post(f'/permissions/1/delete')
        assert response.status_code in [302, 401]

    def test_delete_requires_permission(self, authenticated_client, permission_edit_users):
        """Test that deleting permission requires delete permissions permission."""
        response = authenticated_client.post(f'/permissions/{permission_edit_users.id}/delete')
        assert response.status_code == 403

    def test_delete_permission_success(self, admin_client, db):
        """Test successful permission deletion."""
        permission = Permission(name='to be deleted')
        db.session.add(permission)
        db.session.commit()

        permission_id = permission.id

        response = admin_client.post(f'/permissions/{permission_id}/delete', follow_redirects=True)

        assert response.status_code == 200
        assert b'deleted successfully' in response.data

        # Verify permission was deleted
        permission = db.session.get(Permission, permission_id)
        assert permission is None

    def test_delete_permission_removes_role_associations(self, admin_client, db, role_user, permission_view_users):
        """Test that deleting permission removes role associations."""
        permission_id = permission_view_users.id

        # Verify role has the permission
        assert role_user.has_permission('view users')

        response = admin_client.post(f'/permissions/{permission_id}/delete', follow_redirects=True)
        assert response.status_code == 200

        # Verify permission was deleted
        permission = db.session.get(Permission, permission_id)
        assert permission is None

        # Verify role no longer has the permission
        db.session.refresh(role_user)
        assert not role_user.has_permission('view users')

    def test_delete_nonexistent_permission(self, admin_client):
        """Test deleting non-existent permission."""
        response = admin_client.post('/permissions/99999/delete', follow_redirects=True)
        assert b'not found' in response.data

    def test_delete_permission_affects_users(self, admin_client, db, regular_user, role_user, permission_view_users):
        """Test that deleting permission affects users through roles."""
        # Verify user has permission through role
        assert regular_user.has_permission('view users')

        permission_id = permission_view_users.id
        admin_client.post(f'/permissions/{permission_id}/delete', follow_redirects=True)

        # Verify user no longer has permission
        db.session.refresh(regular_user)
        assert not regular_user.has_permission('view users')


class TestPermissionsAPI:
    """Test permissions API endpoint."""

    def test_api_requires_authentication(self, client):
        """Test that API requires login."""
        response = client.get('/permissions/api')
        assert response.status_code in [302, 401]

    def test_api_requires_permission(self, authenticated_client):
        """Test that API requires view permissions permission."""
        response = authenticated_client.get('/permissions/api')
        assert response.status_code == 403

    def test_api_returns_json(self, admin_client):
        """Test that API returns JSON data."""
        response = admin_client.get('/permissions/api')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

    def test_api_returns_permissions_list(self, admin_client, db, all_permissions):
        """Test that API returns permissions list."""
        response = admin_client.get('/permissions/api')
        assert response.status_code == 200

        data = response.get_json()
        assert 'permissions' in data
        assert isinstance(data['permissions'], list)

    def test_api_includes_roles_count(self, admin_client, db, permission_view_users, role_user):
        """Test that API includes roles count."""
        response = admin_client.get('/permissions/api')
        assert response.status_code == 200

        data = response.get_json()
        assert 'permissions' in data
        if len(data['permissions']) > 0:
            perm_data = data['permissions'][0]
            assert 'roles_count' in perm_data

    def test_api_search(self, admin_client, db, permission_view_users):
        """Test API search functionality."""
        response = admin_client.get('/permissions/api?search=view')
        assert response.status_code == 200

        data = response.get_json()
        assert 'permissions' in data

    def test_api_pagination(self, admin_client, db):
        """Test API pagination."""
        # Create multiple permissions
        for i in range(15):
            perm = Permission(name=f'api permission {i}')
            db.session.add(perm)
        db.session.commit()

        response = admin_client.get('/permissions/api?page=1&per_page=10')
        assert response.status_code == 200

        data = response.get_json()
        assert 'total' in data
        assert 'pages' in data
        assert 'current_page' in data
