#!/bin/bash
set -e

# Multi-platform Docker build script for FlaskStarter
# Builds for both x86_64 (amd64) and arm64 architectures

echo "🚀 Building multi-platform Docker image for FlaskStarter"
echo "=================================================="

# Check if buildx is available
if ! docker buildx version > /dev/null 2>&1; then
    echo "❌ Error: Docker buildx is not available"
    echo "Please update Docker to a version that supports buildx"
    exit 1
fi

# Create a new builder instance if it doesn't exist
BUILDER_NAME="flaskstarter-builder"
if ! docker buildx inspect $BUILDER_NAME > /dev/null 2>&1; then
    echo "📦 Creating new buildx builder: $BUILDER_NAME"
    docker buildx create --name $BUILDER_NAME --driver docker-container --use
else
    echo "✅ Using existing buildx builder: $BUILDER_NAME"
    docker buildx use $BUILDER_NAME
fi

# Bootstrap the builder (downloads QEMU if needed for cross-platform)
echo "🔧 Bootstrapping builder..."
docker buildx inspect --bootstrap

# Get version/tag (default to 'latest')
VERSION=${1:-latest}
IMAGE_NAME=${2:-flaskstarter}

echo ""
echo "📋 Build Configuration:"
echo "   Image Name: $IMAGE_NAME"
echo "   Version: $VERSION"
echo "   Platforms: linux/amd64, linux/arm64"
echo ""

# Build for multiple platforms
echo "🔨 Building for linux/amd64 and linux/arm64..."
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag $IMAGE_NAME:$VERSION \
    --tag $IMAGE_NAME:latest \
    --cache-from type=local,src=/tmp/.buildx-cache \
    --cache-to type=local,dest=/tmp/.buildx-cache-new,mode=max \
    --progress=plain \
    --load \
    . 

# Rotate cache to avoid growing indefinitely
if [ -d "/tmp/.buildx-cache-new" ]; then
    rm -rf /tmp/.buildx-cache
    mv /tmp/.buildx-cache-new /tmp/.buildx-cache
fi

echo ""
echo "✅ Multi-platform build complete!"
echo ""
echo "📦 Built images:"
docker images | grep $IMAGE_NAME | head -3

echo ""
echo "🧪 To test the image:"
echo "   docker run -p 8000:8000 $IMAGE_NAME:$VERSION"
echo ""
echo "📤 To push to a registry:"
echo "   docker buildx build --platform linux/amd64,linux/arm64 \\"
echo "     --tag your-registry/$IMAGE_NAME:$VERSION --push ."
