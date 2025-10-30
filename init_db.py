#!/usr/bin/env python3
"""Quick database initialization script."""

from app import create_app, db
from app.models import User, Role, Permission

def init_database():
    """Initialize database with sample data."""
    app = create_app()

    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("✓ Tables created")

        # Create permissions
        permissions_data = [
            'view users', 'create users', 'edit users', 'delete users',
            'view roles', 'create roles', 'edit roles', 'delete roles',
            'view permissions', 'create permissions', 'edit permissions', 'delete permissions',
        ]

        print("\nCreating permissions...")
        permissions = {}
        for perm_name in permissions_data:
            perm = Permission.query.filter_by(name=perm_name).first()
            if not perm:
                perm = Permission(name=perm_name)
                db.session.add(perm)
                print(f"  + {perm_name}")
            permissions[perm_name] = perm

        db.session.commit()
        print("✓ Permissions created")

        # Create admin role
        print("\nCreating Admin role...")
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            admin_role = Role(name='Admin')
            db.session.add(admin_role)
            db.session.flush()

            for perm in permissions.values():
                admin_role.give_permission_to(perm)

            db.session.commit()
            print("✓ Admin role created with all permissions")
        else:
            print("✓ Admin role already exists")

        # Create user role
        print("\nCreating User role...")
        user_role = Role.query.filter_by(name='User').first()
        if not user_role:
            user_role = Role(name='User')
            db.session.add(user_role)
            db.session.flush()

            view_permissions = ['view users', 'view roles', 'view permissions']
            for perm_name in view_permissions:
                user_role.give_permission_to(permissions[perm_name])

            db.session.commit()
            print("✓ User role created with view permissions")
        else:
            print("✓ User role already exists")

        # Create admin user
        print("\nCreating admin user...")
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(name='Admin User', email='admin@example.com')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.flush()

            admin.assign_role(admin_role)
            db.session.commit()
            print("✓ Admin user created")
            print("  Email: admin@example.com")
            print("  Password: admin123")
        else:
            print("✓ Admin user already exists")

        # Create regular user
        print("\nCreating regular user...")
        user = User.query.filter_by(email='user@example.com').first()
        if not user:
            user = User(name='Regular User', email='user@example.com')
            user.set_password('user123')
            db.session.add(user)
            db.session.flush()

            user.assign_role(user_role)
            db.session.commit()
            print("✓ Regular user created")
            print("  Email: user@example.com")
            print("  Password: user123")
        else:
            print("✓ Regular user already exists")

        print("\n" + "="*50)
        print("Database initialized successfully!")
        print("="*50)
        print("\nYou can now login with:")
        print("  Admin: admin@example.com / admin123")
        print("  User:  user@example.com / user123")


if __name__ == '__main__':
    init_database()
