from datetime import datetime, UTC
from flask_login import UserMixin
from app import db
import bcrypt


class User(UserMixin, db.Model):
    """User model with authentication and authorization."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC),
                          onupdate=lambda: datetime.now(UTC))

    # Relationships
    roles = db.relationship('Role', secondary='user_has_roles',
                          back_populates='users', lazy='dynamic')

    def set_password(self, password):
        """Hash and set the user's password."""
        from flask import current_app
        # Use configured bcrypt rounds (fast in testing, secure in production)
        rounds = current_app.config.get('BCRYPT_LOG_ROUNDS', 12)
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds)).decode('utf-8')

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def has_role(self, role_name):
        """Check if user has a specific role."""
        return self.roles.filter_by(name=role_name).first() is not None

    def has_any_role(self, *role_names):
        """Check if user has any of the specified roles."""
        return self.roles.filter(db.func.lower(db.text('name')).in_([r.lower() for r in role_names])).first() is not None

    def has_all_roles(self, *role_names):
        """Check if user has all of the specified roles."""
        user_roles = {role.name.lower() for role in self.roles}
        return all(role.lower() in user_roles for role in role_names)

    def assign_role(self, role):
        """Assign a role to the user."""
        if not self.has_role(role.name):
            self.roles.append(role)

    def remove_role(self, role):
        """Remove a role from the user."""
        if self.has_role(role.name):
            self.roles.remove(role)

    def has_permission(self, permission_name):
        """Check if user has a specific permission through their roles."""
        for role in self.roles:
            if role.has_permission(permission_name):
                return True
        return False

    def has_any_permission(self, *permission_names):
        """Check if user has any of the specified permissions."""
        permission_names_lower = [p.lower() for p in permission_names]
        for role in self.roles:
            for permission in role.permissions:
                if permission.name.lower() in permission_names_lower:
                    return True
        return False

    def has_all_permissions(self, *permission_names):
        """Check if user has all of the specified permissions."""
        user_permissions = self.get_permissions()
        user_permission_names = {p.name.lower() for p in user_permissions}
        return all(perm.lower() in user_permission_names for perm in permission_names)

    def get_permissions(self):
        """Get all permissions the user has through their roles."""
        permissions = []
        seen_ids = set()
        for role in self.roles:
            for permission in role.permissions:
                if permission.id not in seen_ids:
                    permissions.append(permission)
                    seen_ids.add(permission.id)
        return permissions

    def __repr__(self):
        return f'<User {self.email}>'
