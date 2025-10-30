# Bug Fixes

## Issues Fixed

### 1. ✅ CSRF Token Missing in Templates
**Problem:** `csrf_token()` was undefined in templates, causing Jinja2 errors when trying to render forms.

**Solution:** Initialize Flask-WTF's CSRFProtect extension in the app factory.

**Fixed in:** `app/__init__.py:5,12,28`

### 2. ✅ `manage.py runserver` Command
**Problem:** The `runserver` command was calling `app.run()` which conflicts with Flask's CLI.

**Solution:** Updated to use `subprocess` to call Flask's built-in run command.

**Fixed in:** `manage.py:138-155`

### 3. ✅ Permission Query Methods
**Problem:** User permission methods (`has_permission`, `has_any_permission`, etc.) were using incorrect SQLAlchemy query syntax with `db.text()` for joins, causing `ArgumentError`.

**Solution:** Rewrote methods to use the existing relationship attributes instead of manual joins:
- Iterate through `user.roles`
- Check each `role.permissions`
- Use simpler, more maintainable code

**Fixed in:** `app/models/user.py:55-86`

**Methods Fixed:**
- `has_permission()` - Now iterates through roles
- `has_any_permission()` - Checks permissions across all roles
- `has_all_permissions()` - Uses `get_permissions()` helper
- `get_permissions()` - Returns unique list of all permissions

### 4. ✅ Dashboard Template Stats
**Problem:** Dashboard template was trying to call `.query.count()` on model instances, which doesn't work.

**Solution:**
- Updated route to calculate stats and pass to template
- Changed template to use passed `stats` dictionary

**Fixed in:**
- `app/routes/main.py:1-32`
- `templates/dashboard.html:26,48,70`

## Testing

All fixes have been tested and verified. The application now:
- ✅ Starts correctly with `uv run python manage.py runserver`
- ✅ Checks permissions correctly through role relationships
- ✅ Displays dashboard stats without errors

## New Helper Script

Created `init_db.py` - A simple script to initialize the database with sample data:
- Creates all permissions
- Creates Admin and User roles
- Creates test admin and regular user accounts

Run with: `uv run python init_db.py`

## Running the Application

```bash
# 1. Make sure MySQL is running and database exists
mysql -u root -p -e "CREATE DATABASE flaskstarter;"

# 2. Run migrations
uv run flask --app app db migrate -m "Initial migration"
uv run flask --app app db upgrade

# 3. Initialize database with sample data
uv run python init_db.py

# 4. Start server
uv run python manage.py runserver

# 5. Visit http://127.0.0.1:5000 and login:
#    Admin: admin@example.com / admin123
#    User:  user@example.com / user123
```

## Code Quality

- All changes maintain backwards compatibility
- Code is more readable and maintainable
- Follows SQLAlchemy best practices
- Uses proper relationship traversal instead of raw SQL
