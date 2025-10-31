# Docker Build & CI/CD Setup

## Overview

This project is configured with a production-ready Docker setup and automated CI/CD pipeline that builds, tests, and deploys to GitHub Container Registry (GHCR).

## What's Included

### 1. **Multi-Stage Dockerfile**
   - **Stage 1**: Node.js builder for frontend assets
   - **Stage 2**: Python dependencies builder  
   - **Stage 3**: Minimal production runtime

### 2. **Frontend Build Process**
   - Tailwind CSS compiled and minified
   - Alpine.js bundled (no CDN dependency)
   - Assets served from static files in production
   - CDN fallback in development mode

### 3. **GitHub Actions CI/CD**
   - Automated testing on push/PR
   - Docker image build and push to GHCR
   - Multi-platform support (amd64, arm64)
   - Automatic versioning and tagging

### 4. **Production Optimizations**
   - Non-root user execution
   - Minimal base image (Python slim)
   - Health check endpoint
   - Gunicorn WSGI server
   - Optimized layer caching

## File Structure

```
.
├── Dockerfile              # Multi-stage production build
├── docker-compose.yml      # Local testing setup
├── .dockerignore          # Exclude unnecessary files
├── .github/
│   └── workflows/
│       └── ci-cd.yml      # GitHub Actions pipeline
├── package.json           # Frontend dependencies
├── tailwind.config.js     # Tailwind configuration
├── static/
│   ├── src/
│   │   ├── css/
│   │   │   └── app.css    # Source CSS with Tailwind directives
│   │   └── js/
│   │       └── app.js     # Source JavaScript (Alpine.js imports)
│   └── dist/              # Built assets (generated, gitignored)
│       ├── css/
│       │   └── app.css    # Compiled & minified CSS
│       └── js/
│           └── app.js     # Alpine.js bundle
└── DEPLOYMENT.md          # Deployment instructions
```

## Quick Start

### Build Locally

```bash
# Build the image
docker build -t flaskstarter:latest .

# Or use docker-compose
docker-compose up -d
```

### Build Frontend Assets Only

```bash
# Install dependencies
npm install

# Build CSS and JS
npm run build

# Watch mode for development
npm run watch:css
```

## Image Details

### Size Optimization
- **Base Image**: python:3.13-slim
- **Build Dependencies**: Separated from runtime
- **Final Size**: ~200-250 MB (compared to ~800MB+ without optimization)

### What's Included in Production
- Python runtime and app code
- Compiled Python dependencies  
- Built frontend assets (CSS + JS)
- Gunicorn WSGI server
- Health check endpoint

### What's NOT Included
- Build tools and compilers
- Development dependencies
- Node.js runtime
- Git history
- Test files

## GitHub Actions Workflow

### Triggers
- Push to `main` or `develop` branches
- Tagged releases (`v*`)
- Pull requests

### Steps
1. **Test Job**
   - Sets up Python 3.13
   - Installs dependencies with uv
   - Runs MySQL service for testing
   - Executes full test suite
   - Uploads coverage reports

2. **Build and Push Job** (only on push, not PRs)
   - Builds multi-platform Docker image
   - Pushes to GitHub Container Registry
   - Creates multiple tags:
     - `latest` (main branch only)
     - `main-{sha}` (specific commit)
     - `v1.0.0` (semver tags)

3. **Deployment Notification**
   - Comments on commits with deployment info
   - Provides image URL and version

## Environment Configuration

### Development (uses CDN)
```bash
FLASK_ENV=development
```
- Tailwind and Alpine loaded from CDN
- Hot reload friendly
- No build step required

### Production (uses built assets)
```bash
FLASK_ENV=production
```
- Compiled Tailwind CSS  
- Bundled Alpine.js
- No external dependencies
- Optimized and minified

## Container Registry

Images are pushed to GitHub Container Registry:

```
ghcr.io/YOUR_USERNAME/YOUR_REPO:latest
ghcr.io/YOUR_USERNAME/YOUR_REPO:main-abc1234
ghcr.io/YOUR_USERNAME/YOUR_REPO:v1.0.0
```

### Pulling Images

```bash
# Public repo (no auth needed)
docker pull ghcr.io/YOUR_USERNAME/YOUR_REPO:latest

# Private repo (requires authentication)
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
docker pull ghcr.io/YOUR_USERNAME/YOUR_REPO:latest
```

## Coolify Integration

### Automatic Deployment

1. **Connect to GitHub**
   - Coolify can watch for new images
   - Auto-deploy on new tags

2. **Configure Service**
   ```
   Image: ghcr.io/YOUR_USERNAME/YOUR_REPO:latest
   Port: 8000
   Health Check: /health
   ```

3. **Environment Variables**
   ```
   DATABASE_HOST=...
   DATABASE_NAME=...
   DATABASE_USER=...
   DATABASE_PASSWORD=...
   SECRET_KEY=...
   FLASK_ENV=production
   ```

## Development Workflow

### Making Changes

1. **Frontend Changes**
   ```bash
   # Watch mode for CSS
   npm run watch:css
   
   # Manual build
   npm run build
   ```

2. **Backend Changes**
   - Tests run automatically on push
   - Docker image builds on merge to main

3. **Testing Locally**
   ```bash
   # Run tests
   uv run manage.py test -n auto
   
   # Test Docker build
   docker build -t flaskstarter:test .
   docker run -p 8000:8000 flaskstarter:test
   ```

## Health Checks

The application exposes a health check endpoint:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "flaskstarter"
}
```

This is used by:
- Docker's built-in health check
- Coolify service monitoring
- Load balancers
- Orchestration platforms

## Security Considerations

### Container Security
- ✅ Runs as non-root user (uid 1000)
- ✅ Minimal attack surface
- ✅ No build tools in production
- ✅ Read-only file system compatible
- ✅ Health checks for availability

### Secrets Management
- ❌ Never commit secrets to Git
- ✅ Use environment variables
- ✅ Generate strong SECRET_KEY
- ✅ Use Coolify secret management

## Troubleshooting

### Build Fails

```bash
# Check Dockerfile syntax
docker build --no-cache -t test .

# Verify frontend builds
npm run build
```

### Image Too Large

```bash
# Check image size
docker images | grep flaskstarter

# Inspect layers
docker history flaskstarter:latest
```

### Health Check Failing

```bash
# Check if port is accessible
docker exec -it <container> curl http://localhost:8000/health

# Check logs
docker logs <container>
```

## Maintenance

### Updating Dependencies

```bash
# Python dependencies
uv pip compile pyproject.toml

# Frontend dependencies
npm update
npm audit fix
```

### Rebuilding Images

```bash
# Force rebuild (no cache)
docker build --no-cache -t flaskstarter:latest .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t flaskstarter:latest .
```

## Performance Tips

1. **Build Cache**: GitHub Actions caches layers for faster builds
2. **Multi-platform**: Builds for both x64 and ARM  
3. **Layer Optimization**: Dependencies installed before code copy
4. **Asset Minification**: CSS and JS are minified
5. **Production Server**: Uses Gunicorn with multiple workers

## Next Steps

1. Push to GitHub to trigger first build
2. Check Actions tab for build progress
3. View image in GitHub Packages
4. Configure Coolify with image URL
5. Deploy and enjoy! 🚀
