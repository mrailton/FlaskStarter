# Multi-stage build for minimal production image

# Stage 1: Node.js for building frontend assets
FROM node:20-alpine AS frontend-builder

WORKDIR /build

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies (including devDependencies for build tools)
RUN npm ci

# Copy source files needed for build
COPY static/src ./static/src
COPY templates ./templates
COPY tailwind.config.js ./

# Build frontend assets (CSS and JS)
RUN npm run build

# Stage 2: Python dependencies builder
FROM python:3.13-slim AS python-builder

WORKDIR /build

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependency files
COPY pyproject.toml ./

# Install uv for faster package installation
RUN pip install --no-cache-dir uv

# Create virtual environment and install dependencies
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache -r pyproject.toml

# Stage 3: Final production image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    FLASK_APP=app \
    FLASK_ENV=production

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash flaskapp

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=python-builder /opt/venv /opt/venv

# Copy application code
COPY --chown=flaskapp:flaskapp app ./app
COPY --chown=flaskapp:flaskapp templates ./templates
COPY --chown=flaskapp:flaskapp config.py manage.py ./

# Copy built frontend assets from frontend builder
COPY --from=frontend-builder --chown=flaskapp:flaskapp /build/static/dist ./static/dist

# Create necessary directories
RUN mkdir -p instance logs && \
    chown -R flaskapp:flaskapp /app

# Switch to non-root user
USER flaskapp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Expose port
EXPOSE 8000

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "app:create_app()"]
