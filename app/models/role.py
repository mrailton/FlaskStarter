from datetime import datetime, UTC
from app import db


class Role(db.Model):
    """Role model for role-based authorization (inspired by Spatie Laravel Permission)."""

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    guard_name = db.Column(db.String(255), nullable=False, default='web')
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC),
                          onupdate=lambda: datetime.now(UTC))

    # Relationships
    users = db.relationship('User', secondary='user_has_roles',
                          back_populates='roles', lazy='dynamic')
    permissions = db.relationship('Permission', secondary='role_has_permissions',
                                back_populates='roles', lazy='dynamic')

    def has_permission(self, permission_name):
        """Check if role has a specific permission."""
        return self.permissions.filter_by(name=permission_name).first() is not None

    def give_permission_to(self, permission):
        """Give a permission to this role."""
        if not self.has_permission(permission.name):
            self.permissions.append(permission)

    def revoke_permission_to(self, permission):
        """Revoke a permission from this role."""
        if self.has_permission(permission.name):
            self.permissions.remove(permission)

    def sync_permissions(self, permissions):
        """Sync role permissions (replace all with the provided list)."""
        # Clear all existing permissions
        self.permissions = []
        # Add new permissions
        for permission in permissions:
            self.permissions.append(permission)

    def __repr__(self):
        return f'<Role {self.name}>'
