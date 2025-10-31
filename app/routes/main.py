from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import User, Role, Permission

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Homepage route."""
    if current_user.is_authenticated:
        # Get stats for dashboard
        stats = {
            'total_users': User.query.count(),
            'total_roles': Role.query.count(),
            'total_permissions': Permission.query.count(),
        }
        return render_template('dashboard.html', stats=stats)
    return render_template('index.html')


@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route."""
    # Get stats for dashboard
    stats = {
        'total_users': User.query.count(),
        'total_roles': Role.query.count(),
        'total_permissions': Permission.query.count(),
    }
    return render_template('dashboard.html', stats=stats)


@bp.route('/health')
def health():
    """Health check endpoint for container orchestration."""
    return jsonify({
        'status': 'healthy',
        'service': 'flaskstarter'
    }), 200
