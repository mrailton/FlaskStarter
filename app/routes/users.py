from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from app import db
from app.models.user import User
from app.models.role import Role
from app.middleware import permission_required

bp = Blueprint('users', __name__, url_prefix='/users')


class UserForm(FlaskForm):
    """User create/edit form."""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=255)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('Password', validators=[
        Optional(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    roles = SelectMultipleField('Roles', coerce=int)

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.roles.choices = [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]

    def validate_email(self, field):
        """Check if email already exists."""
        query = User.query.filter_by(email=field.data.lower())
        if self.user:
            query = query.filter(User.id != self.user.id)
        if query.first():
            raise ValidationError('Email already registered.')


@bp.route('/')
@login_required
@permission_required('view users')
def index():
    """List all users with search, sort, filter."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    role_filter = request.args.get('role', '', type=str)

    # Build query
    query = User.query

    # Apply search
    if search:
        query = query.filter(
            db.or_(
                User.name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )

    # Apply role filter
    if role_filter:
        query = query.join(User.roles).filter(Role.name == role_filter)

    # Apply sorting
    if hasattr(User, sort_by):
        column = getattr(User, sort_by)
        if sort_order == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Get all roles for filter dropdown
    roles = Role.query.order_by(Role.name).all()

    return render_template('users/index.html',
                         users=pagination.items,
                         pagination=pagination,
                         roles=roles)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@permission_required('create users')
def create():
    """Create a new user."""
    form = UserForm()

    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data.lower()
        )

        if form.password.data:
            user.set_password(form.password.data)
        else:
            # Generate a random password if none provided
            import secrets
            random_password = secrets.token_urlsafe(16)
            user.set_password(random_password)

        db.session.add(user)
        db.session.flush()  # Get user ID before committing

        # Assign roles
        for role_id in form.roles.data:
            role = db.session.get(Role, role_id)
            if role:
                user.assign_role(role)

        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('users.index'))

    return render_template('users/form.html', form=form, user=None)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('edit users')
def edit(id):
    """Edit an existing user."""
    user = db.session.get(User, id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('users.index'))

    form = UserForm(user=user, obj=user)

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data.lower()

        if form.password.data:
            user.set_password(form.password.data)

        # Update roles
        current_roles = list(user.roles)
        for role in current_roles:
            user.remove_role(role)

        for role_id in form.roles.data:
            role = db.session.get(Role, role_id)
            if role:
                user.assign_role(role)

        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('users.index'))

    # Pre-select current roles
    if request.method == 'GET':
        form.roles.data = [role.id for role in user.roles]

    return render_template('users/form.html', form=form, user=user)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@permission_required('delete users')
def delete(id):
    """Delete a user."""
    user = db.session.get(User, id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('users.index'))

    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('users.index'))


@bp.route('/api')
@login_required
@permission_required('view users')
def api():
    """API endpoint for users data (for DataTables, etc.)."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')

    query = User.query

    if search:
        query = query.filter(
            db.or_(
                User.name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'users': [{
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'roles': [role.name for role in user.roles],
            'created_at': user.created_at.isoformat()
        } for user in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })
