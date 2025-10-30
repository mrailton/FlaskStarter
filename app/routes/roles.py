from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField
from wtforms.validators import DataRequired, Length, ValidationError
from app import db
from app.models.role import Role
from app.models.permission import Permission
from app.middleware import permission_required

bp = Blueprint('roles', __name__, url_prefix='/roles')


class RoleForm(FlaskForm):
    """Role create/edit form."""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=255)])
    permissions = SelectMultipleField('Permissions', coerce=int)

    def __init__(self, role=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        self.permissions.choices = [(p.id, p.name) for p in Permission.query.order_by(Permission.name).all()]

    def validate_name(self, field):
        """Check if role name already exists."""
        query = Role.query.filter_by(name=field.data)
        if self.role:
            query = query.filter(Role.id != self.role.id)
        if query.first():
            raise ValidationError('Role name already exists.')


@bp.route('/')
@login_required
@permission_required('view roles')
def index():
    """List all roles with search and sort."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')

    # Build query
    query = Role.query

    # Apply search
    if search:
        query = query.filter(Role.name.ilike(f'%{search}%'))

    # Apply sorting
    if hasattr(Role, sort_by):
        column = getattr(Role, sort_by)
        if sort_order == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('roles/index.html',
                         roles=pagination.items,
                         pagination=pagination)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@permission_required('create roles')
def create():
    """Create a new role."""
    form = RoleForm()

    if form.validate_on_submit():
        role = Role(name=form.name.data)
        db.session.add(role)
        db.session.flush()

        # Assign permissions
        for permission_id in form.permissions.data:
            permission = db.session.get(Permission, permission_id)
            if permission:
                role.give_permission_to(permission)

        db.session.commit()
        flash('Role created successfully!', 'success')
        return redirect(url_for('roles.index'))

    return render_template('roles/form.html', form=form, role=None)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('edit roles')
def edit(id):
    """Edit an existing role."""
    role = db.session.get(Role, id)
    if not role:
        flash('Role not found.', 'error')
        return redirect(url_for('roles.index'))

    form = RoleForm(role=role, obj=role)

    if form.validate_on_submit():
        role.name = form.name.data

        # Sync permissions
        selected_permissions = [
            db.session.get(Permission, pid) for pid in form.permissions.data
        ]
        role.sync_permissions([p for p in selected_permissions if p])

        db.session.commit()
        flash('Role updated successfully!', 'success')
        return redirect(url_for('roles.index'))

    # Pre-select current permissions
    if request.method == 'GET':
        form.permissions.data = [perm.id for perm in role.permissions]

    return render_template('roles/form.html', form=form, role=role)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@permission_required('delete roles')
def delete(id):
    """Delete a role."""
    role = db.session.get(Role, id)
    if not role:
        flash('Role not found.', 'error')
        return redirect(url_for('roles.index'))

    db.session.delete(role)
    db.session.commit()
    flash('Role deleted successfully!', 'success')
    return redirect(url_for('roles.index'))


@bp.route('/api')
@login_required
@permission_required('view roles')
def api():
    """API endpoint for roles data."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')

    query = Role.query

    if search:
        query = query.filter(Role.name.ilike(f'%{search}%'))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'roles': [{
            'id': role.id,
            'name': role.name,
            'permissions_count': role.permissions.count(),
            'users_count': role.users.count(),
            'created_at': role.created_at.isoformat()
        } for role in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })
