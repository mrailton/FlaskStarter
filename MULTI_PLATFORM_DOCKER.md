# Multi-Platform Docker Support

## Overview

The FlaskStarter Docker image is built to support both **x86_64 (amd64)** and **arm64** architectures, ensuring compatibility with:

- **x86_64**: Intel/AMD processors, most cloud providers, traditional servers
- **arm64**: Apple Silicon (M1/M2/M3), AWS Graviton, Raspberry Pi 4+, modern ARM servers

## Quick Start

### Using Make (Recommended)

```bash
# Build for multiple platforms
make build-multi

# Build and push to registry
make build-multi-push IMAGE_NAME=ghcr.io/username/flaskstarter

# Show available commands
make help
```

### Using Docker Buildx

```bash
# Build for both platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag flaskstarter:latest \
  --load \
  .

# Build and push to registry
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/username/flaskstarter:latest \
  --push \
  .
```

### Using the Build Script

```bash
# Build with default settings
./docker-build-multiplatform.sh

# Build with custom version
./docker-build-multiplatform.sh v1.0.0

# Build with custom name and version
./docker-build-multiplatform.sh v1.0.0 myapp
```

## Setup Requirements

### 1. Docker Buildx

Buildx is included in Docker Desktop and recent Docker Engine versions.

**Check if buildx is available:**
```bash
docker buildx version
```

**If not available, install Docker 19.03+ or Docker Desktop.**

### 2. QEMU for Cross-Platform Builds

QEMU allows building for different architectures on your current machine.

**Setup (one-time):**
```bash
# Install QEMU binfmt
docker run --privileged --rm tonistiigi/binfmt --install all

# Verify
docker buildx ls
```

### 3. Create Buildx Builder

```bash
# Create a new builder
docker buildx create --name multiplatform --driver docker-container --use

# Bootstrap it
docker buildx inspect --bootstrap

# Verify platforms
docker buildx inspect multiplatform
```

## Build Options

### Local Build (Test Only)

Build for multiple platforms and load into local Docker:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag flaskstarter:test \
  --load \
  .
```

**Note:** `--load` only works when building for your current platform. For multi-platform, use `--push` or save to tar.

### Build and Push to Registry

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/username/flaskstarter:latest \
  --tag ghcr.io/username/flaskstarter:v1.0.0 \
  --push \
  .
```

### Build with Caching

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag flaskstarter:latest \
  --cache-from type=registry,ref=flaskstarter:buildcache \
  --cache-to type=registry,ref=flaskstarter:buildcache,mode=max \
  --push \
  .
```

### Export to Tar Files

```bash
# Export each platform separately
docker buildx build \
  --platform linux/amd64 \
  --output type=docker,dest=flaskstarter-amd64.tar \
  .

docker buildx build \
  --platform linux/arm64 \
  --output type=docker,dest=flaskstarter-arm64.tar \
  .
```

## GitHub Actions

The repository includes a GitHub Actions workflow that automatically builds for both platforms.

### Workflow Configuration

Located in `.github/workflows/ci-cd.yml`:

```yaml
# Run tests using Make
- name: Run tests with Make
  run: |
    source .venv/bin/activate
    make test

# Build and push multi-platform image
- name: Build and push multi-platform Docker image
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    platforms: linux/amd64,linux/arm64
    tags: ${{ steps.meta.outputs.tags }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Note:** The workflow uses `docker/build-push-action` for building because it's highly optimized for multi-platform builds with GitHub's cache. For local builds, use `make build-multi` or `make build-multi-push`.

### Triggering Builds

**Automatic builds on:**
- Push to `main` or `develop` branches
- Tagged releases (`v*`)
- Pull requests (build only, no push)

**Manual trigger:**
```bash
# Create and push a tag
git tag v1.0.0
git push origin v1.0.0
```

### Viewing Built Images

After the workflow completes:

```bash
# List available tags
gh api /user/packages/container/flaskstarter/versions

# Pull the image
docker pull ghcr.io/username/flaskstarter:latest

# Inspect platforms
docker buildx imagetools inspect ghcr.io/username/flaskstarter:latest
```

## Platform-Specific Considerations

### Image Compatibility

The Dockerfile uses multi-arch base images:
- `node:20-alpine` - Supports amd64, arm64
- `python:3.13-slim` - Supports amd64, arm64

All dependencies are compatible with both architectures.

### Build Times

| Platform | Build Time (estimated) | Notes |
|----------|----------------------|-------|
| amd64 (native) | 3-5 minutes | Fast, native compilation |
| arm64 (native) | 3-5 minutes | Fast on Apple Silicon |
| amd64 (cross) | 5-8 minutes | Emulated via QEMU |
| arm64 (cross) | 5-8 minutes | Emulated via QEMU |

### Performance

- **Native builds**: Full CPU speed
- **Cross-platform builds**: 50-70% slower due to QEMU emulation
- **GitHub Actions**: Builds both platforms in parallel (~6-8 minutes total)

## Testing Multi-Platform Images

### Test on Current Platform

```bash
docker run --rm flaskstarter:latest python --version
```

### Test Specific Platform

```bash
# Test amd64 on any platform
docker run --rm --platform linux/amd64 flaskstarter:latest python --version

# Test arm64 on any platform
docker run --rm --platform linux/arm64 flaskstarter:latest python --version
```

### Inspect Image

```bash
# Show all platforms
docker buildx imagetools inspect flaskstarter:latest

# Check manifest
docker manifest inspect flaskstarter:latest
```

## Coolify Deployment

Coolify automatically selects the correct platform based on your server's architecture.

### From GHCR

```
Image: ghcr.io/username/flaskstarter:latest
```

Coolify will pull:
- `linux/amd64` on x86_64 servers
- `linux/arm64` on ARM servers (Graviton, Raspberry Pi, etc.)

### Verification

In Coolify, check the container details:
```bash
docker inspect flaskstarter | grep Architecture
```

## Troubleshooting

### "no match for platform" Error

**Problem:** Image doesn't exist for your platform

**Solution:**
```bash
# Check available platforms
docker buildx imagetools inspect your-image:tag

# Rebuild for missing platform
docker buildx build --platform linux/amd64,linux/arm64 --tag your-image:tag --push .
```

### Slow Cross-Platform Builds

**Problem:** Building for arm64 on amd64 (or vice versa) is slow

**Solutions:**
1. Use GitHub Actions (builds in parallel)
2. Build on native hardware when possible
3. Use build caching to speed up subsequent builds

### QEMU Not Working

**Problem:** Cross-platform builds fail

**Solution:**
```bash
# Reinstall QEMU support
docker run --privileged --rm tonistiigi/binfmt --uninstall qemu-*
docker run --privileged --rm tonistiigi/binfmt --install all

# Restart Docker Desktop (if using)
```

### Can't Load Multi-Platform Image

**Problem:** `--load` fails with multi-platform build

**Explanation:** Docker can only load images for the current platform.

**Solutions:**
- Use `--push` to push to a registry instead
- Build only for current platform: `--platform linux/amd64`
- Export to tar and load manually

## Best Practices

### 1. Use Registry for Multi-Platform

Always push multi-platform images to a registry:
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --push \
  --tag ghcr.io/user/app:latest \
  .
```

### 2. Tag Strategy

```bash
# Semantic versioning
--tag app:v1.0.0 \
--tag app:v1.0 \
--tag app:v1 \
--tag app:latest
```

### 3. Use Caching

```bash
# GitHub Actions cache
--cache-from type=gha \
--cache-to type=gha,mode=max
```

### 4. Test Both Platforms

```bash
# Run tests on both
docker run --platform linux/amd64 app:latest pytest
docker run --platform linux/arm64 app:latest pytest
```

### 5. Monitor Image Size

```bash
# Check size for each platform
docker buildx imagetools inspect app:latest --raw | \
  jq '.manifests[] | {platform: .platform.os + "/" + .platform.architecture, size: .size}'
```

## Makefile Commands

The included Makefile provides convenient commands:

```bash
make help              # Show all available commands
make build            # Build for current platform
make build-multi      # Build for amd64 + arm64
make build-multi-push # Build and push multi-platform
make test             # Run tests
make test-docker      # Test Docker image
make run              # Run container
make stop             # Stop container
make logs             # View logs
make clean            # Clean up images
make platforms        # Show supported platforms
make size             # Show image size
```

## Resources

- [Docker Buildx Documentation](https://docs.docker.com/buildx/working-with-buildx/)
- [Multi-platform Images Guide](https://docs.docker.com/build/building/multi-platform/)
- [GitHub Actions Docker Build](https://github.com/docker/build-push-action)
- [QEMU User Emulation](https://www.qemu.org/docs/master/user/main.html)

## Summary

✅ **Dockerfile is multi-platform ready**
✅ **GitHub Actions builds for both amd64 and arm64**
✅ **Works on x86_64 and ARM servers**
✅ **Compatible with Coolify auto-deployment**
✅ **Makefile for easy local builds**
✅ **Build script for custom workflows**

Your Docker image will work seamlessly on any modern server architecture! 🚀
