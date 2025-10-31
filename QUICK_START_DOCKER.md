# Quick Start - Multi-Platform Docker

## TL;DR

Your Docker setup is **already configured** for both x86_64 and arm64! 🎉

### GitHub Actions (Automatic)
Push to `main` → Automatically builds for both platforms → Pushes to GHCR

### Local Build (Manual)
```bash
# Option 1: Use Makefile (easiest)
make build-multi

# Option 2: Use the script
./docker-build-multiplatform.sh

# Option 3: Use docker buildx directly
docker buildx build --platform linux/amd64,linux/arm64 -t flaskstarter:latest --load .
```

## What's Already Configured

✅ **Dockerfile** - Uses multi-arch base images  
✅ **GitHub Actions** - Builds for amd64 + arm64 automatically  
✅ **Makefile** - Convenient build commands  
✅ **Build Script** - Custom multi-platform builds  

## Common Commands

```bash
# Show available Make commands
make help

# Build for both platforms
make build-multi

# Build and push to registry
make build-multi-push IMAGE_NAME=ghcr.io/user/repo

# Run container
make run

# View logs
make logs

# Stop container
make stop

# Clean up
make clean
```

## Deploy to Coolify

1. **Push code to GitHub** (triggers automatic build)

2. **In Coolify:**
   - Add new service → Docker Image
   - Image: `ghcr.io/YOUR_USERNAME/YOUR_REPO:latest`
   - Port: 8000
   - Health check: `/health`

3. **Coolify automatically:**
   - Pulls the correct platform image (amd64 or arm64)
   - Deploys to your server
   - No configuration needed!

## Verify Multi-Platform

```bash
# After pushing to registry, check platforms:
docker buildx imagetools inspect ghcr.io/user/repo:latest

# You should see both:
# - linux/amd64
# - linux/arm64
```

## Need Help?

- Full guide: [MULTI_PLATFORM_DOCKER.md](MULTI_PLATFORM_DOCKER.md)
- Deployment: [DEPLOYMENT.md](DEPLOYMENT.md)
- Build details: [DOCKER_BUILD.md](DOCKER_BUILD.md)

## That's It!

Your Docker image will work on:
- Intel/AMD servers (x86_64)
- Apple Silicon Macs (M1/M2/M3)
- AWS Graviton instances
- ARM servers and Raspberry Pi

No additional configuration needed! 🚀
