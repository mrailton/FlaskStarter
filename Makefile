.PHONY: help build build-multi test clean run stop logs

# Variables
IMAGE_NAME ?= flaskstarter
VERSION ?= latest
PLATFORMS ?= linux/amd64,linux/arm64

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker image for current platform
	@echo "🔨 Building Docker image for current platform..."
	docker build -t $(IMAGE_NAME):$(VERSION) .

build-multi: ## Build Docker image for multiple platforms (amd64, arm64)
	@echo "🔨 Building multi-platform Docker image..."
	@docker buildx build \
		--platform $(PLATFORMS) \
		--tag $(IMAGE_NAME):$(VERSION) \
		--tag $(IMAGE_NAME):latest \
		--load \
		.

build-multi-push: ## Build and push multi-platform image to registry
	@echo "🚀 Building and pushing multi-platform image..."
	@docker buildx build \
		--platform $(PLATFORMS) \
		--tag $(IMAGE_NAME):$(VERSION) \
		--push \
		.

test: ## Run tests
	@echo "🧪 Running tests..."
	uv run manage.py test -n auto

test-docker: ## Test the built Docker image
	@echo "🧪 Testing Docker image..."
	@docker run --rm \
		-e DATABASE_HOST=localhost \
		-e DATABASE_NAME=test \
		-e DATABASE_USER=test \
		-e DATABASE_PASSWORD=test \
		-e SECRET_KEY=test-secret-key \
		$(IMAGE_NAME):$(VERSION) \
		python -c "from app import create_app; app = create_app(); print('✅ App created successfully')"

run: ## Run Docker container
	@echo "🚀 Starting Docker container..."
	@docker run -d \
		--name $(IMAGE_NAME) \
		-p 8000:8000 \
		-e DATABASE_HOST=db \
		-e DATABASE_NAME=flaskstarter \
		-e DATABASE_USER=user \
		-e DATABASE_PASSWORD=password \
		-e SECRET_KEY=change-this-secret \
		$(IMAGE_NAME):$(VERSION)
	@echo "✅ Container started. Visit http://localhost:8000"

stop: ## Stop and remove Docker container
	@echo "🛑 Stopping Docker container..."
	@docker stop $(IMAGE_NAME) 2>/dev/null || true
	@docker rm $(IMAGE_NAME) 2>/dev/null || true
	@echo "✅ Container stopped"

logs: ## Show Docker container logs
	docker logs -f $(IMAGE_NAME)

clean: ## Clean up Docker images and cache
	@echo "🧹 Cleaning up..."
	@docker rmi $(IMAGE_NAME):$(VERSION) 2>/dev/null || true
	@docker rmi $(IMAGE_NAME):latest 2>/dev/null || true
	@docker builder prune -f
	@echo "✅ Cleanup complete"

shell: ## Open shell in running container
	docker exec -it $(IMAGE_NAME) /bin/bash

npm-build: ## Build frontend assets
	@echo "📦 Building frontend assets..."
	@mkdir -p static/dist/css static/dist/js
	npm run build

inspect: ## Inspect Docker image
	@echo "🔍 Inspecting Docker image..."
	@docker image inspect $(IMAGE_NAME):$(VERSION)

platforms: ## Show supported platforms for the image
	@echo "🏗️  Checking supported platforms..."
	@docker buildx imagetools inspect $(IMAGE_NAME):$(VERSION) 2>/dev/null || \
		echo "Image not yet pushed to registry. Run 'make build-multi-push' first."

size: ## Show Docker image size
	@echo "📏 Image size:"
	@docker images $(IMAGE_NAME):$(VERSION) --format "{{.Repository}}:{{.Tag}}\t{{.Size}}"
