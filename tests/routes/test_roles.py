"""Tests for roles routes."""

import pytest
from app.models import Role, Permission


class TestRolesIndex:
    """Test roles list/index route."""

    def test_roles_requires_authentication(self, client):
        """Test that roles list requires login."""
        response = client.get('/roles/')
        assert response.status_code in [302, 401]

    def test_roles_requires_permission(self, authenticated_client):
        """Test that roles list requires view roles permission."""
        response = authenticated_client.get('/roles/')
        assert response.status_code == 403

    def test_roles_list_with_permission(self, admin_client):
        """Test that users with permission can view list."""
        response = admin_client.get('/roles/')
        assert response.status_code == 200

    def test_roles_list_shows_roles(self, admin_client, db, role_user, role_editor):
        """Test that roles list shows all roles."""
        response = admin_client.get('/roles/')
        assert response.status_code == 200
        assert b'Roles' in response.data or b'roles' in response.data

    def test_roles_search(self, admin_client, db, role_user, role_editor):
        """Test roles search functionality."""
        response = admin_client.get('/roles/?search=User')
        assert response.status_code == 200

    def test_roles_pagination(self, admin_client, db):
        """Test roles pagination."""
        # Create multiple roles
        for i in range(15):
            role = Role(name=f'Role {i}')
            db.session.add(role)
        db.session.commit()

        response = admin_client.get('/roles/?page=1&per_page=10')
        assert response.status_code == 200

    def test_roles_sort_by_name_asc(self, admin_client):
        """Test roles sorting by name ascending."""
        response = admin_client.get('/roles/?sort_by=name&sort_order=asc')
        assert response.status_code == 200

    def test_roles_sort_by_name_desc(self, admin_client):
        """Test roles sorting by name descending."""
        response = admin_client.get('/roles/?sort_by=name&sort_order=desc')
        assert response.status_code == 200


class TestRolesCreate:
    """Test role creation."""

    def test_create_requires_authentication(self, client):
        """Test that creating role requires login."""
        response = client.get('/roles/create')
        assert response.status_code in [302, 401]

    def test_create_requires_permission(self, authenticated_client):
        """Test that creating role requires create roles permission."""
        response = authenticated_client.get('/roles/create')
        assert response.status_code == 403

    def test_create_form_loads(self, admin_client):
        """Test that create form loads for authorized users."""
        response = admin_client.get('/roles/create')
        assert response.status_code == 200
        assert b'Create' in response.data or b'create' in response.data

    def test_create_role_success(self, admin_client, db):
        """Test successful role creation."""
        response = admin_client.post('/roles/create', data={
            'name': 'New Role',
            'permissions': []
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'created successfully' in response.data

        # Verify role was created
        role = Role.query.filter_by(name='New Role').first()
        assert role is not None

    def test_create_role_with_permissions(self, admin_client, db, permission_view_users, permission_edit_users):
        """Test creating role with permissions."""
        response = admin_client.post('/roles/create', data={
            'name': 'Role With Permissions',
            'permissions': [permission_view_users.id, permission_edit_users.id]
        }, follow_redirects=True)

        assert response.status_code == 200

        role = Role.query.filter_by(name='Role With Permissions').first()
        assert role is not None
        assert role.has_permission('view users')
        assert role.has_permission('edit users')

    def test_create_duplicate_role_name(self, admin_client, role_user):
        """Test creating role with duplicate name."""
        response = admin_client.post('/roles/create', data={
            'name': role_user.name,
            'permissions': []
        })

        assert b'already exists' in response.data

    def test_create_role_short_name(self, admin_client):
        """Test creating role with too short name."""
        response = admin_client.post('/roles/create', data={
            'name': 'A',
            'permissions': []
        })

        assert response.status_code == 200  # Form validation fails


class TestRolesEdit:
    """Test role editing."""

    def test_edit_requires_authentication(self, client, role_user):
        """Test that editing role requires login."""
        response = client.get(f'/roles/{role_user.id}/edit')
        assert response.status_code in [302, 401]

    def test_edit_requires_permission(self, authenticated_client, role_user):
        """Test that editing role requires edit roles permission."""
        response = authenticated_client.get(f'/roles/{role_user.id}/edit')
        assert response.status_code == 403

    def test_edit_form_loads(self, admin_client, role_user):
        """Test that edit form loads for authorized users."""
        response = admin_client.get(f'/roles/{role_user.id}/edit')
        assert response.status_code == 200
        assert b'Edit' in response.data or b'edit' in response.data

    def test_edit_role_name(self, admin_client, db, role_editor):
        """Test updating role name."""
        response = admin_client.post(f'/roles/{role_editor.id}/edit', data={
            'name': 'Updated Editor',
            'permissions': []
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'updated successfully' in response.data

        db.session.refresh(role_editor)
        assert role_editor.name == 'Updated Editor'

    def test_edit_role_permissions(self, admin_client, db, role_editor, permission_delete_users):
        """Test updating role permissions."""
        response = admin_client.post(f'/roles/{role_editor.id}/edit', data={
            'name': role_editor.name,
            'permissions': [permission_delete_users.id]
        }, follow_redirects=True)

        assert response.status_code == 200

        db.session.refresh(role_editor)
        assert role_editor.has_permission('delete users')
        # Old permissions should be removed
        assert not role_editor.has_permission('view users')

    def test_edit_role_add_permissions(self, admin_client, db):
        """Test adding permissions to role."""
        role = Role(name='Test Role')
        db.session.add(role)
        db.session.commit()

        perm1 = Permission(name='test permission 1')
        perm2 = Permission(name='test permission 2')
        db.session.add(perm1)
        db.session.add(perm2)
        db.session.commit()

        response = admin_client.post(f'/roles/{role.id}/edit', data={
            'name': role.name,
            'permissions': [perm1.id, perm2.id]
        }, follow_redirects=True)

        assert response.status_code == 200

        db.session.refresh(role)
        assert role.has_permission('test permission 1')
        assert role.has_permission('test permission 2')

    def test_edit_nonexistent_role(self, admin_client):
        """Test editing non-existent role."""
        response = admin_client.get('/roles/99999/edit', follow_redirects=True)
        assert b'not found' in response.data

    def test_edit_duplicate_name(self, admin_client, role_user, role_editor):
        """Test editing role with existing name."""
        response = admin_client.post(f'/roles/{role_editor.id}/edit', data={
            'name': role_user.name,  # Another role's name
            'permissions': []
        })

        assert b'already exists' in response.data


class TestRolesDelete:
    """Test role deletion."""

    def test_delete_requires_authentication(self, client, role_editor):
        """Test that deleting role requires login."""
        response = client.post(f'/roles/{role_editor.id}/delete')
        assert response.status_code in [302, 401]

    def test_delete_requires_permission(self, authenticated_client, role_editor):
        """Test that deleting role requires delete roles permission."""
        response = authenticated_client.post(f'/roles/{role_editor.id}/delete')
        assert response.status_code == 403

    def test_delete_role_success(self, admin_client, db, role_editor):
        """Test successful role deletion."""
        role_id = role_editor.id

        response = admin_client.post(f'/roles/{role_id}/delete', follow_redirects=True)

        assert response.status_code == 200
        assert b'deleted successfully' in response.data

        # Verify role was deleted
        role = db.session.get(Role, role_id)
        assert role is None

    def test_delete_role_removes_user_associations(self, admin_client, db, regular_user, role_user):
        """Test that deleting role removes user associations."""
        role_id = role_user.id

        # Verify user has the role
        assert regular_user.has_role('User')

        response = admin_client.post(f'/roles/{role_id}/delete', follow_redirects=True)
        assert response.status_code == 200

        # Verify role was deleted
        role = db.session.get(Role, role_id)
        assert role is None

        # Verify user no longer has the role
        db.session.refresh(regular_user)
        assert not regular_user.has_role('User')

    def test_delete_nonexistent_role(self, admin_client):
        """Test deleting non-existent role."""
        response = admin_client.post('/roles/99999/delete', follow_redirects=True)
        assert b'not found' in response.data


class TestRolesAPI:
    """Test roles API endpoint."""

    def test_api_requires_authentication(self, client):
        """Test that API requires login."""
        response = client.get('/roles/api')
        assert response.status_code in [302, 401]

    def test_api_requires_permission(self, authenticated_client):
        """Test that API requires view roles permission."""
        response = authenticated_client.get('/roles/api')
        assert response.status_code == 403

    def test_api_returns_json(self, admin_client):
        """Test that API returns JSON data."""
        response = admin_client.get('/roles/api')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

    def test_api_returns_roles_list(self, admin_client, db, role_user, role_editor):
        """Test that API returns roles list."""
        response = admin_client.get('/roles/api')
        assert response.status_code == 200

        data = response.get_json()
        assert 'roles' in data
        assert isinstance(data['roles'], list)

    def test_api_includes_counts(self, admin_client, db, role_user, regular_user):
        """Test that API includes permission and user counts."""
        response = admin_client.get('/roles/api')
        assert response.status_code == 200

        data = response.get_json()
        assert 'roles' in data
        if len(data['roles']) > 0:
            role_data = data['roles'][0]
            assert 'permissions_count' in role_data
            assert 'users_count' in role_data

    def test_api_search(self, admin_client, db, role_user):
        """Test API search functionality."""
        response = admin_client.get('/roles/api?search=User')
        assert response.status_code == 200

        data = response.get_json()
        assert 'roles' in data

    def test_api_pagination(self, admin_client, db):
        """Test API pagination."""
        # Create multiple roles
        for i in range(15):
            role = Role(name=f'API Role {i}')
            db.session.add(role)
        db.session.commit()

        response = admin_client.get('/roles/api?page=1&per_page=10')
        assert response.status_code == 200

        data = response.get_json()
        assert 'total' in data
        assert 'pages' in data
        assert 'current_page' in data
