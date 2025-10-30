#!/usr/bin/env python3
"""Management script for FlaskStarter application."""

import click
from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User, Role, Permission


def create_cli_app():
    """Create Flask app for CLI."""
    return create_app()


@click.group(cls=FlaskGroup, create_app=create_cli_app)
def cli():
    """Management script for FlaskStarter."""
    pass


@cli.command()
def init_db():
    """Initialize the database."""
    click.echo('Initializing database...')
    db.create_all()
    click.echo('Database initialized!')


@cli.command()
def seed_permissions():
    """Seed default permissions."""
    click.echo('Seeding permissions...')

    permissions_list = [
        'view users', 'create users', 'edit users', 'delete users',
        'view roles', 'create roles', 'edit roles', 'delete roles',
        'view permissions', 'create permissions', 'edit permissions', 'delete permissions',
    ]

    for perm_name in permissions_list:
        if not Permission.query.filter_by(name=perm_name).first():
            permission = Permission(name=perm_name)
            db.session.add(permission)
            click.echo(f'  Created permission: {perm_name}')

    db.session.commit()
    click.echo('Permissions seeded successfully!')


@cli.command()
def seed_roles():
    """Seed default roles with permissions."""
    click.echo('Seeding roles...')

    # Admin role with all permissions
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        admin_role = Role(name='Admin')
        db.session.add(admin_role)
        db.session.flush()

        # Assign all permissions to admin
        permissions = Permission.query.all()
        for perm in permissions:
            admin_role.give_permission_to(perm)

        click.echo('  Created role: Admin (with all permissions)')

    # User role with limited permissions
    user_role = Role.query.filter_by(name='User').first()
    if not user_role:
        user_role = Role(name='User')
        db.session.add(user_role)
        db.session.flush()

        # Assign view permissions only
        view_permissions = ['view users', 'view roles', 'view permissions']
        for perm_name in view_permissions:
            perm = Permission.query.filter_by(name=perm_name).first()
            if perm:
                user_role.give_permission_to(perm)

        click.echo('  Created role: User (with view permissions)')

    db.session.commit()
    click.echo('Roles seeded successfully!')


@cli.command()
@click.option('--email', prompt=True, help='Admin email address')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@click.option('--name', prompt=True, help='Admin name')
def create_admin(email, password, name):
    """Create an admin user."""
    click.echo('Creating admin user...')

    # Check if user already exists
    if User.query.filter_by(email=email.lower()).first():
        click.echo('Error: User with this email already exists!', err=True)
        return

    # Create user
    user = User(name=name, email=email.lower())
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    # Assign admin role
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        click.echo('Error: Admin role not found. Run seed_roles first!', err=True)
        db.session.rollback()
        return

    user.assign_role(admin_role)
    db.session.commit()

    click.echo(f'Admin user created successfully: {email}')


@cli.command()
def seed_all():
    """Seed permissions, roles, and create admin user."""
    click.echo('Seeding all data...')

    # Seed permissions
    ctx = click.get_current_context()
    ctx.invoke(seed_permissions)
    ctx.invoke(seed_roles)

    click.echo('\nAll data seeded! You can now create an admin user with: python manage.py create-admin')


@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
@click.option('--debug/--no-debug', default=True, help='Enable debug mode')
def runserver(host, port, debug):
    """Run the development server."""
    import subprocess
    import sys
    import os

    env = os.environ.copy()
    env['FLASK_APP'] = 'app'
    if debug:
        env['FLASK_DEBUG'] = '1'

    cmd = [sys.executable, '-m', 'flask', 'run', '--host', host, '--port', str(port)]
    if debug:
        cmd.append('--debug')

    click.echo(f'Starting development server on http://{host}:{port}')
    result = subprocess.run(cmd, env=env)
    sys.exit(result.returncode)



@cli.command()
@click.argument('message')
def migrate(message):
    """Create a new migration."""
    import subprocess
    import sys

    cmd = [sys.executable, '-m', 'flask', 'db', 'migrate', '-m', message]
    click.echo(f'Running: {" ".join(cmd)}')
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@cli.command()
def upgrade():
    """Upgrade database to the latest migration."""
    import subprocess
    import sys

    cmd = [sys.executable, '-m', 'flask', 'db', 'upgrade']
    click.echo(f'Running: {" ".join(cmd)}')
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@cli.command()
def downgrade():
    """Downgrade database by one migration."""
    import subprocess
    import sys

    cmd = [sys.executable, '-m', 'flask', 'db', 'downgrade']
    click.echo(f'Running: {" ".join(cmd)}')
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == '__main__':
    cli()
