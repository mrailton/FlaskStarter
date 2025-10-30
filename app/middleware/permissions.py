from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*role_names):
    """Decorator to require one or more roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_any_role(*role_names):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def permission_required(*permission_names):
    """Decorator to require one or more permissions."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_any_permission(*permission_names):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def all_permissions_required(*permission_names):
    """Decorator to require all specified permissions."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_all_permissions(*permission_names):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def all_roles_required(*role_names):
    """Decorator to require all specified roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_all_roles(*role_names):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
