from datetime import datetime, UTC
from app import db


class Permission(db.Model):
    """Permission model for role-based authorization (inspired by Spatie Laravel Permission)."""

    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    guard_name = db.Column(db.String(255), nullable=False, default='web')
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC),
                          onupdate=lambda: datetime.now(UTC))

    # Relationships
    roles = db.relationship('Role', secondary='role_has_permissions',
                          back_populates='permissions', lazy='dynamic')

    def assign_to_role(self, role):
        """Assign this permission to a role."""
        if not self.roles.filter_by(id=role.id).first():
            self.roles.append(role)

    def remove_from_role(self, role):
        """Remove this permission from a role."""
        if self.roles.filter_by(id=role.id).first():
            self.roles.remove(role)

    def __repr__(self):
        return f'<Permission {self.name}>'


# Association table for model (User) has roles (many-to-many)
model_has_roles = db.Table('model_has_roles',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    db.Column('model_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('model_type', db.String(255), nullable=False, default='User')
)

# Association table for role has permissions (many-to-many)
role_has_permissions = db.Table('role_has_permissions',
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)
