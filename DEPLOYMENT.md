# Deployment Guide

## Docker Production Deployment

### Building the Image Locally

```bash
# Build the image
docker build -t flaskstarter:latest .

# Run the container
docker run -d \
  -p 8000:8000 \
  -e DATABASE_HOST=your-db-host \
  -e DATABASE_NAME=your-db-name \
  -e DATABASE_USER=your-db-user \
  -e DATABASE_PASSWORD=your-db-password \
  -e SECRET_KEY=your-secret-key \
  --name flaskstarter \
  flaskstarter:latest
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

## Coolify Deployment

### Using GitHub Actions (Automatic)

1. **Enable GitHub Container Registry**
   - Your repository already has GitHub Actions configured
   - Push to `main` branch triggers automatic builds
   - Images are pushed to `ghcr.io/YOUR_USERNAME/YOUR_REPO:latest`

2. **Configure Coolify**
   - Add a new service in Coolify
   - Choose "Docker Image" as source
   - Set image to: `ghcr.io/YOUR_USERNAME/YOUR_REPO:latest`
   - Configure environment variables (see below)

3. **Set Environment Variables in Coolify**
   ```
   DATABASE_HOST=your-mysql-host
   DATABASE_PORT=3306
   DATABASE_NAME=flaskstarter
   DATABASE_USER=your-db-user
   DATABASE_PASSWORD=your-secure-password
   SECRET_KEY=generate-a-secure-random-key
   FLASK_ENV=production
   ```

4. **Database Setup**
   - Create a MySQL service in Coolify or use external MySQL
   - Run migrations after first deploy:
     ```bash
     # In Coolify terminal for the app
     flask db upgrade
     ```

### Manual Coolify Setup

If you prefer to build in Coolify directly:

1. **Create New Service**
   - Source: Git Repository
   - Repository: Your GitHub repo URL
   - Branch: main

2. **Build Configuration**
   - Build Pack: Dockerfile
   - Dockerfile Location: ./Dockerfile

3. **Environment Variables** (same as above)

4. **Port Configuration**
   - Internal Port: 8000

## Environment Variables

### Required
- `DATABASE_HOST` - MySQL host
- `DATABASE_NAME` - Database name
- `DATABASE_USER` - Database user
- `DATABASE_PASSWORD` - Database password
- `SECRET_KEY` - Flask secret key (generate with `python -c 'import secrets; print(secrets.token_hex(32))'`)

### Optional
- `DATABASE_PORT` - MySQL port (default: 3306)
- `FLASK_ENV` - Environment (production/development)
- `APP_NAME` - Application name
- `APP_URL` - Application URL

## GitHub Actions Workflow

The CI/CD pipeline automatically:

1. **On Push/PR**:
   - Runs all tests
   - Checks code coverage
   
2. **On Push to Main**:
   - Builds Docker image
   - Pushes to GitHub Container Registry
   - Tags with version and latest

3. **Image Tags**:
   - `latest` - Latest main branch
   - `main-{sha}` - Specific commit
   - `v1.0.0` - Semantic version tags

## Image Details

### Image Size Optimization

The production image is optimized for size:
- Multi-stage build separates build dependencies from runtime
- Uses Python slim base image
- Only production dependencies included
- Frontend assets built during build (no CDN dependencies)

### Security Features

- Runs as non-root user (`flaskapp`)
- Minimal attack surface
- Health check endpoint included
- No development dependencies in production

## Health Checks

The container exposes a health check endpoint:

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

## Monitoring

### Logs
```bash
# Docker
docker logs -f flaskstarter

# Docker Compose
docker-compose logs -f app

# Coolify
View logs in Coolify dashboard
```

### Database Migrations

```bash
# Inside container
flask db upgrade

# Or with docker exec
docker exec -it flaskstarter flask db upgrade
```

## Troubleshooting

### Container won't start
- Check environment variables are set correctly
- Verify database is accessible
- Check logs: `docker logs flaskstarter`

### Database connection issues
- Verify DATABASE_HOST is correct
- Check database credentials
- Ensure database service is running
- Test connection: `docker exec -it flaskstarter flask shell`

### Static files not loading
- Images are built with assets included
- No CDN required in production
- Verify `FLASK_ENV=production` is set

## Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set `FLASK_ENV=production`
- [ ] Enable HTTPS in reverse proxy
- [ ] Configure database backups
- [ ] Set up monitoring/alerts
- [ ] Run database migrations
- [ ] Test health check endpoint
- [ ] Verify logs are accessible
- [ ] Configure resource limits in Coolify
