from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, ValidationError
from app import db
from app.models.permission import Permission
from app.middleware import permission_required as require_permission

bp = Blueprint('permissions', __name__, url_prefix='/permissions')


class PermissionForm(FlaskForm):
    """Permission create/edit form."""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=255)])

    def __init__(self, permission=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.permission = permission

    def validate_name(self, field):
        """Check if permission name already exists."""
        query = Permission.query.filter_by(name=field.data)
        if self.permission:
            query = query.filter(Permission.id != self.permission.id)
        if query.first():
            raise ValidationError('Permission name already exists.')


@bp.route('/')
@login_required
@require_permission('view permissions')
def index():
    """List all permissions with search and sort."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')

    # Build query
    query = Permission.query

    # Apply search
    if search:
        query = query.filter(Permission.name.ilike(f'%{search}%'))

    # Apply sorting
    if hasattr(Permission, sort_by):
        column = getattr(Permission, sort_by)
        if sort_order == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('permissions/index.html',
                         permissions=pagination.items,
                         pagination=pagination)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@require_permission('create permissions')
def create():
    """Create a new permission."""
    form = PermissionForm()

    if form.validate_on_submit():
        permission = Permission(name=form.name.data)
        db.session.add(permission)
        db.session.commit()
        flash('Permission created successfully!', 'success')
        return redirect(url_for('permissions.index'))

    return render_template('permissions/form.html', form=form, permission=None)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@require_permission('edit permissions')
def edit(id):
    """Edit an existing permission."""
    permission = db.session.get(Permission, id)
    if not permission:
        flash('Permission not found.', 'error')
        return redirect(url_for('permissions.index'))

    form = PermissionForm(permission=permission, obj=permission)

    if form.validate_on_submit():
        permission.name = form.name.data
        db.session.commit()
        flash('Permission updated successfully!', 'success')
        return redirect(url_for('permissions.index'))

    return render_template('permissions/form.html', form=form, permission=permission)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@require_permission('delete permissions')
def delete(id):
    """Delete a permission."""
    permission = db.session.get(Permission, id)
    if not permission:
        flash('Permission not found.', 'error')
        return redirect(url_for('permissions.index'))

    db.session.delete(permission)
    db.session.commit()
    flash('Permission deleted successfully!', 'success')
    return redirect(url_for('permissions.index'))


@bp.route('/api')
@login_required
@require_permission('view permissions')
def api():
    """API endpoint for permissions data."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')

    query = Permission.query

    if search:
        query = query.filter(Permission.name.ilike(f'%{search}%'))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'permissions': [{
            'id': perm.id,
            'name': perm.name,
            'roles_count': perm.roles.count(),
            'created_at': perm.created_at.isoformat()
        } for perm in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })
