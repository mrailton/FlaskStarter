#!/bin/bash

# FlaskStarter Setup Script
# This script helps you quickly set up the FlaskStarter application

set -e

echo "🚀 FlaskStarter Setup"
echo "===================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed"
    echo "Please install uv first: https://github.com/astral-sh/uv"
    exit 1
fi

# Check if Python 3.13 is available
if ! command -v python3.13 &> /dev/null; then
    echo "⚠️  Warning: Python 3.13 not found, using system Python"
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync --extra dev
echo "✅ Dependencies installed"
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env and configure your database settings"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Ask if user wants to initialize database
read -p "🗄️  Do you want to create database migrations? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating initial migration..."
    uv run flask --app app db migrate -m "Initial migration"
    echo "✅ Migration created"
    echo ""

    read -p "🗄️  Apply migrations now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Applying migrations..."
        uv run flask --app app db upgrade
        echo "✅ Migrations applied"
        echo ""
    fi
fi

# Ask if user wants to seed data
read -p "🌱 Do you want to seed permissions and roles? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Seeding data..."
    uv run python manage.py seed-all
    echo "✅ Data seeded"
    echo ""

    read -p "👤 Do you want to create an admin user? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        uv run python manage.py create-admin
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your database credentials"
echo "2. Run: uv run python manage.py runserver"
echo "3. Visit: http://localhost:5000"
echo ""
echo "For more information, see README.md"
