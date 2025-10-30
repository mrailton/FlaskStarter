# FlaskStarter

A modern, full-stack Flask application starter with authentication, role-based authorization (inspired by Spatie's Laravel Permission), and a beautiful, responsive UI.

## Features

### Backend
- **Python 3.13** - Latest Python version
- **Flask 3.1+** - Modern Flask web framework
- **MySQL Database** - Reliable data storage with SQLAlchemy ORM
- **Database Migrations** - Auto-generated migrations with Alembic/Flask-Migrate
- **Authentication** - Secure email/password authentication with Flask-Login
- **Role-Based Authorization** - Spatie-style permissions system with roles and permissions
- **RESTful API** - Clean, organized route structure

### Frontend
- **Tailwind CSS 4** - Modern, utility-first CSS framework
- **Alpine.js 3** - Lightweight JavaScript framework for interactivity
- **Dark Mode** - Built-in light/dark theme switcher
- **Responsive Design** - Mobile, tablet, and desktop optimized
- **Advanced Tables** - Searchable, sortable, and filterable data tables

### Testing & Development
- **PyTest** - Comprehensive test suite with parallel execution
- **Code Coverage** - Built-in coverage reporting
- **Management CLI** - Convenient commands for common tasks
- **Development Tools** - Hot reload, debugging, and more

## Requirements

- Python 3.13+
- MySQL 5.7+ or MariaDB 10.3+
- uv (for package management)

## Installation

### 1. Clone or Use as Template

```bash
# If cloning
git clone <repository-url>
cd FlaskStarter

# If creating from template
# Use this repository as a template on GitHub
```

### 2. Install Dependencies

```bash
# Install all dependencies including dev dependencies
uv sync --extra dev
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# At minimum, update:
# - SECRET_KEY
# - DATABASE_USER
# - DATABASE_PASSWORD
# - DATABASE_NAME
```

### 4. Create Database

```bash
# Create the MySQL database
mysql -u root -p
> CREATE DATABASE flaskstarter CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
> CREATE DATABASE flaskstarter_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
> exit
```

### 5. Initialize Database

```bash
# Create initial migration
uv run flask --app app db migrate -m "Initial migration"

# Apply migrations
uv run flask --app app db upgrade

# Seed permissions and roles
uv run python manage.py seed-all

# Create admin user
uv run python manage.py create-admin
```

## Usage

### Running the Development Server

```bash
# Option 1: Using manage.py (recommended)
uv run python manage.py runserver

# Option 2: Using Flask directly
uv run flask --app app run --debug

# Option 3: With custom host/port
uv run python manage.py runserver --host 0.0.0.0 --port 8000

# The application will be available at http://127.0.0.1:5000
```

### Management Commands

The `manage.py` script provides convenient commands:

```bash
# Run development server
uv run python manage.py runserver

# Database operations
uv run python manage.py init-db              # Initialize database
uv run python manage.py migrate "message"    # Create migration
uv run python manage.py upgrade              # Apply migrations
uv run python manage.py downgrade            # Rollback migration

# Seeding data
uv run python manage.py seed-permissions     # Seed permissions
uv run python manage.py seed-roles           # Seed roles
uv run python manage.py seed-all             # Seed all data
uv run python manage.py create-admin         # Create admin user

# Testing
uv run python manage.py test                 # Run tests with coverage
uv run python manage.py test --no-parallel   # Run tests serially
uv run python manage.py test --no-coverage   # Run tests without coverage
```

### Running Tests

```bash
# Run all tests with coverage (parallel by default)
uv run pytest

# Run tests in parallel
uv run pytest -n auto

# Run specific test file
uv run pytest tests/test_models.py

# Run with coverage report
uv run pytest --cov=app --cov-report=html --cov-report=term-missing

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Project Structure

```
FlaskStarter/
├── app/
│   ├── __init__.py          # App factory
│   ├── models/              # Database models
│   │   ├── user.py
│   │   ├── role.py
│   │   └── permission.py
│   ├── routes/              # Route blueprints
│   │   ├── auth.py          # Authentication routes
│   │   ├── main.py          # Main routes
│   │   ├── users.py         # User management
│   │   ├── roles.py         # Role management
│   │   └── permissions.py   # Permission management
│   └── middleware/          # Custom middleware
│       └── permissions.py   # Permission decorators
├── templates/               # Jinja2 templates
│   ├── base.html           # Base template
│   ├── auth/               # Auth templates
│   ├── users/              # User management
│   ├── roles/              # Role management
│   └── permissions/        # Permission management
├── static/                  # Static files
│   ├── css/
│   └── js/
├── migrations/              # Database migrations
├── tests/                   # Test suite
│   ├── conftest.py         # Test fixtures
│   ├── test_models.py      # Model tests
│   ├── test_auth.py        # Auth tests
│   └── test_permissions.py # Permission tests
├── config.py               # Configuration
├── manage.py               # Management script
├── pyproject.toml          # Project dependencies
└── .env                    # Environment variables
```

## Permissions System

This starter uses a Spatie-style permissions system:

### How It Works

1. **Permissions** are granular capabilities (e.g., "view users", "edit posts")
2. **Roles** are collections of permissions (e.g., "Admin", "Editor")
3. **Users** are assigned roles, gaining all their permissions

### Using Permissions in Routes

```python
from flask import Blueprint
from app.middleware import permission_required, role_required

bp = Blueprint('example', __name__)

@bp.route('/admin')
@permission_required('access admin')
def admin_page():
    return 'Admin page'

@bp.route('/users')
@permission_required('view users', 'edit users')  # User needs ANY of these
def users_page():
    return 'Users page'

@bp.route('/settings')
@role_required('Admin')
def settings():
    return 'Settings'
```

### Checking Permissions in Code

```python
from flask_login import current_user

# Check single permission
if current_user.has_permission('edit users'):
    # Do something

# Check any permission
if current_user.has_any_permission('edit users', 'delete users'):
    # Do something

# Check all permissions
if current_user.has_all_permissions('view users', 'edit users'):
    # Do something

# Check role
if current_user.has_role('Admin'):
    # Do something

# Get all permissions
permissions = current_user.get_permissions()
```

### Checking Permissions in Templates

```html
{% if current_user.has_permission('create users') %}
    <a href="{{ url_for('users.create') }}">Add User</a>
{% endif %}

{% if current_user.has_role('Admin') %}
    <a href="{{ url_for('admin.dashboard') }}">Admin Panel</a>
{% endif %}
```

## Customization

### Adding New Models

1. Create model in `app/models/`
2. Import in `app/models/__init__.py`
3. Create migration: `uv run python manage.py migrate "Add model"`
4. Apply migration: `uv run python manage.py upgrade`

### Adding New Routes

1. Create blueprint in `app/routes/`
2. Register in `app/__init__.py`
3. Add templates in `templates/`

### Adding New Permissions

1. Add permission name to seed script in `manage.py`
2. Run: `uv run python manage.py seed-permissions`

## Production Deployment

### Environment Variables

Update your `.env` for production:

```bash
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
DATABASE_HOST=<production-db-host>
DATABASE_PASSWORD=<strong-password>
```

### Using as a Template for New Projects

1. Update `pyproject.toml` with your project name
2. Update `APP_NAME` in `.env`
3. Customize branding in templates
4. Add your application logic
5. Deploy!

## Contributing

This is a starter template. Feel free to customize it for your needs!

## License

MIT License - feel free to use this starter for your projects.

## Support

For issues or questions, please open an issue on GitHub.
