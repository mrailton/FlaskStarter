"""Pytest configuration and fixtures for test suite."""

import pytest
import pymysql
import os


def pytest_configure(config):
    """Configure pytest - set worker-specific database name before any imports."""
    # Determine worker ID for parallel execution
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'master')

    # Set unique database name for this worker
    if worker_id != 'master':
        test_db_name = f'flaskstarter_test_{worker_id}'
    else:
        test_db_name = 'flaskstarter_test'

    # Store in environment so config.py can pick it up
    os.environ['TEST_DATABASE_NAME'] = test_db_name


@pytest.fixture(scope='session')
def app():
    """Create application for testing session."""
    from app import create_app, db as _db

    # Get the database name set by pytest_configure
    test_db_name = os.environ.get('TEST_DATABASE_NAME', 'flaskstarter_test')

    # Create app with testing config
    app = create_app('testing')

    # Ensure we're using the correct test database
    assert test_db_name in app.config['SQLALCHEMY_DATABASE_URI'], \
        f"Tests must use test database {test_db_name}, got {app.config['SQLALCHEMY_DATABASE_URI']}"

    with app.app_context():
        # Create test database if it doesn't exist
        _create_test_database(app, test_db_name)

        # Create all tables
        _db.create_all()

        yield app

        # Cleanup: drop all tables and database
        _db.session.remove()
        _db.drop_all()
        _drop_test_database(app, test_db_name)


@pytest.fixture(scope='function')
def db(app):
    """Provide database for a test function with automatic cleanup."""
    from app import db as _db
    from app.models import User, Role, Permission

    with app.app_context():
        # Ensure we start with a clean session
        _db.session.rollback()
        _db.session.expire_all()

        yield _db

        # Clean up: remove all data from tables after each test
        # This ensures test isolation
        try:
            _db.session.rollback()  # Roll back any uncommitted changes
            _db.session.expire_all()  # Expire all cached objects

            # Delete all records from association tables first (to avoid FK constraints)
            _db.session.execute(_db.text('DELETE FROM user_has_roles'))
            _db.session.execute(_db.text('DELETE FROM role_has_permissions'))

            # Then delete from main tables
            _db.session.execute(_db.text('DELETE FROM users'))
            _db.session.execute(_db.text('DELETE FROM roles'))
            _db.session.execute(_db.text('DELETE FROM permissions'))

            _db.session.commit()
        except Exception as e:
            # If cleanup fails, at least close the session
            _db.session.rollback()
            raise
        finally:
            _db.session.remove()


@pytest.fixture(scope='function')
def client(app, db):
    """Provide test client for making requests."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Provide CLI test runner."""
    return app.test_cli_runner()


# Test data fixtures
@pytest.fixture(scope='function')
def permission_view_users(db):
    """Create or get 'view users' permission."""
    from app.models import Permission
    permission = Permission.query.filter_by(name='view users').first()
    if not permission:
        permission = Permission(name='view users', guard_name='web')
        db.session.add(permission)
        db.session.commit()
    return permission


@pytest.fixture(scope='function')
def permission_create_users(db):
    """Create or get 'create users' permission."""
    from app.models import Permission
    permission = Permission.query.filter_by(name='create users').first()
    if not permission:
        permission = Permission(name='create users', guard_name='web')
        db.session.add(permission)
        db.session.commit()
    return permission


@pytest.fixture(scope='function')
def permission_edit_users(db):
    """Create or get 'edit users' permission."""
    from app.models import Permission
    permission = Permission.query.filter_by(name='edit users').first()
    if not permission:
        permission = Permission(name='edit users', guard_name='web')
        db.session.add(permission)
        db.session.commit()
    return permission


@pytest.fixture(scope='function')
def permission_delete_users(db):
    """Create or get 'delete users' permission."""
    from app.models import Permission
    permission = Permission.query.filter_by(name='delete users').first()
    if not permission:
        permission = Permission(name='delete users', guard_name='web')
        db.session.add(permission)
        db.session.commit()
    return permission


@pytest.fixture(scope='function')
def all_permissions(db):
    """Create or get all standard permissions."""
    from app.models import Permission
    permissions = [
        'view users', 'create users', 'edit users', 'delete users',
        'view roles', 'create roles', 'edit roles', 'delete roles',
        'view permissions', 'create permissions', 'edit permissions', 'delete permissions',
    ]

    created_permissions = []
    for perm_name in permissions:
        # Check if permission already exists
        permission = Permission.query.filter_by(name=perm_name).first()
        if not permission:
            permission = Permission(name=perm_name, guard_name='web')
            db.session.add(permission)
        created_permissions.append(permission)

    db.session.commit()
    return created_permissions


@pytest.fixture(scope='function')
def role_admin(db, all_permissions):
    """Create or get admin role with all permissions."""
    from app.models import Role
    role = Role.query.filter_by(name='Admin').first()
    if not role:
        role = Role(name='Admin', guard_name='web')
        db.session.add(role)
        db.session.flush()

        for permission in all_permissions:
            role.give_permission_to(permission)

        db.session.commit()
    return role


@pytest.fixture(scope='function')
def role_user(db, permission_view_users):
    """Create or get user role with limited permissions."""
    from app.models import Role
    role = Role.query.filter_by(name='User').first()
    if not role:
        role = Role(name='User', guard_name='web')
        db.session.add(role)
        db.session.flush()

        role.give_permission_to(permission_view_users)

        db.session.commit()
    return role


@pytest.fixture(scope='function')
def role_editor(db, permission_view_users, permission_edit_users):
    """Create or get editor role with view and edit permissions."""
    from app.models import Role
    role = Role.query.filter_by(name='Editor').first()
    if not role:
        role = Role(name='Editor', guard_name='web')
        db.session.add(role)
        db.session.flush()

        role.give_permission_to(permission_view_users)
        role.give_permission_to(permission_edit_users)

        db.session.commit()
    return role


@pytest.fixture(scope='function')
def user(db):
    """Create a basic test user without roles."""
    from app.models import User
    user = User(name='Test User', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def admin_user(db, role_admin):
    """Create an admin user with admin role."""
    from app.models import User
    user = User(name='Admin User', email='admin@example.com')
    user.set_password('admin123')
    db.session.add(user)
    db.session.flush()

    user.assign_role(role_admin)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def regular_user(db, role_user):
    """Create a regular user with user role."""
    from app.models import User
    user = User(name='Regular User', email='regular@example.com')
    user.set_password('regular123')
    db.session.add(user)
    db.session.flush()

    user.assign_role(role_user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def authenticated_client(client, user):
    """Provide an authenticated test client."""
    with client:
        client.post('/auth/login', data={
            'email': user.email,
            'password': 'password123'
        }, follow_redirects=True)
        yield client


@pytest.fixture(scope='function')
def admin_client(client, admin_user):
    """Provide an authenticated admin client."""
    with client:
        client.post('/auth/login', data={
            'email': admin_user.email,
            'password': 'admin123'
        }, follow_redirects=True)
        yield client


# Helper functions
def _create_test_database(app, db_name):
    """Create test database if it doesn't exist."""
    config = app.config

    # Connect without specifying database
    connection = pymysql.connect(
        host=config['DATABASE_HOST'],
        port=int(config['DATABASE_PORT']),
        user=config['DATABASE_USER'],
        password=config['DATABASE_PASSWORD']
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        connection.commit()
    finally:
        connection.close()


def _drop_test_database(app, db_name):
    """Drop test database."""
    config = app.config

    # Connect without specifying database
    connection = pymysql.connect(
        host=config['DATABASE_HOST'],
        port=int(config['DATABASE_PORT']),
        user=config['DATABASE_USER'],
        password=config['DATABASE_PASSWORD']
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
        connection.commit()
    finally:
        connection.close()
