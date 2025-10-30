# Quick Start Guide

Get FlaskStarter running in 5 minutes!

## Prerequisites

- Python 3.13+
- MySQL 5.7+ or MariaDB 10.3+
- uv package manager

## Quick Setup

### 1. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Run Setup Script

```bash
# Make setup script executable (Unix/Mac)
chmod +x setup.sh

# Run setup
./setup.sh
```

The setup script will:
- Install all dependencies
- Create `.env` configuration file
- Set up database migrations
- Seed default permissions and roles
- Create admin user

### 3. Configure Database

Edit `.env` and update these values:

```bash
DATABASE_HOST=localhost
DATABASE_USER=your_mysql_user
DATABASE_PASSWORD=your_mysql_password
DATABASE_NAME=flaskstarter
```

### 4. Create MySQL Database

```bash
mysql -u root -p -e "CREATE DATABASE flaskstarter CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p -e "CREATE DATABASE flaskstarter_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 5. Run Migrations

```bash
uv run flask --app app db upgrade
```

### 6. Seed Data

**Option A: Use the quick init script (fastest)**

```bash
uv run python init_db.py
```

This creates sample data including:
- Admin user: admin@example.com / admin123
- Regular user: user@example.com / user123

**Option B: Use manage.py commands (more control)**

```bash
# Seed permissions and roles
uv run python manage.py seed-all

# Create admin user (follow prompts)
uv run python manage.py create-admin
```

### 7. Start Development Server

```bash
uv run python manage.py runserver
```

Visit **http://localhost:5000** and log in with your admin credentials!

## Default Permissions

The starter includes these default permissions:

**Users:**
- view users
- create users
- edit users
- delete users

**Roles:**
- view roles
- create roles
- edit roles
- delete roles

**Permissions:**
- view permissions
- create permissions
- edit permissions
- delete permissions

## Default Roles

**Admin** - Has all permissions

**User** - Has view-only permissions

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html
```

## Common Commands

```bash
# Development server
uv run python manage.py runserver

# Create migration
uv run python manage.py migrate "migration message"

# Apply migrations
uv run python manage.py upgrade

# Run tests
uv run python manage.py test

# Create admin user
uv run python manage.py create-admin
```

## What's Next?

1. **Customize** - Update branding, colors, and styles
2. **Extend** - Add your own models, routes, and features
3. **Deploy** - Configure for production deployment

See **README.md** for detailed documentation.

## Troubleshooting

### Database Connection Error

- Check MySQL is running: `mysql -u root -p`
- Verify `.env` credentials are correct
- Ensure database exists

### Import Errors

- Reinstall dependencies: `uv sync --extra dev`
- Check Python version: `python --version`

### Migration Errors

- Reset migrations:
  ```bash
  rm -rf migrations/versions/*
  uv run flask --app app db migrate -m "Initial migration"
  uv run flask --app app db upgrade
  ```

## Need Help?

- Check **README.md** for detailed documentation
- Review code examples in `tests/` directory
- Open an issue on GitHub

Happy coding! 🚀
