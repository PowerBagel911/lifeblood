# Makefile for Lifeblood Ops Assistant Docker operations
# Use: make <target>

.PHONY: help build up down restart logs logs-api logs-web ps clean ingest test shell-api shell-web dev prod

# Default target
help:
	@echo "🐳 Lifeblood Ops Assistant - Docker Commands"
	@echo ""
	@echo "Production Commands:"
	@echo "  make prod          - Start production environment"
	@echo "  make build         - Build Docker images"
	@echo "  make up            - Start services in background"
	@echo "  make down          - Stop and remove containers"
	@echo "  make restart       - Restart all services"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev           - Start development environment with hot-reload"
	@echo "  make dev-down      - Stop development environment"
	@echo ""
	@echo "Monitoring Commands:"
	@echo "  make logs          - View logs from all services"
	@echo "  make logs-api      - View API logs only"
	@echo "  make logs-web      - View web logs only"
	@echo "  make ps            - Show running containers"
	@echo ""
	@echo "Operations Commands:"
	@echo "  make ingest        - Trigger document ingestion"
	@echo "  make test          - Run tests in API container"
	@echo "  make shell-api     - Open shell in API container"
	@echo "  make shell-web     - Open shell in web container"
	@echo ""
	@echo "Cleanup Commands:"
	@echo "  make clean         - Stop and remove containers + volumes"
	@echo "  make clean-all     - Remove everything including images"
	@echo ""

# Check if .env exists
.env-check:
	@if [ ! -f .env ]; then \
		echo "⚠️  .env file not found!"; \
		echo "Creating from template..."; \
		cp env.template .env; \
		echo "Please edit .env and add your GEMINI_API_KEY"; \
		exit 1; \
	fi

# Production commands
build: .env-check
	@echo "🔨 Building Docker images..."
	cd infra/docker && docker compose build

up: .env-check
	@echo "🚀 Starting services..."
	cd infra/docker && docker compose up -d
	@echo "✅ Services started!"
	@echo "Web UI: http://localhost:3000"
	@echo "API: http://localhost:8000/docs"

prod: build up
	@echo "📊 Service status:"
	@cd infra/docker && docker compose ps

down:
	@echo "⏹️  Stopping services..."
	cd infra/docker && docker compose down

restart:
	@echo "🔄 Restarting services..."
	cd infra/docker && docker compose restart

# Development commands
dev: .env-check
	@echo "🚀 Starting development environment with hot-reload..."
	cd infra/docker && docker compose -f compose.dev.yaml up

dev-down:
	@echo "⏹️  Stopping development environment..."
	cd infra/docker && docker compose -f compose.dev.yaml down

# Monitoring commands
logs:
	cd infra/docker && docker compose logs -f

logs-api:
	cd infra/docker && docker compose logs -f api

logs-web:
	cd infra/docker && docker compose logs -f web

ps:
	cd infra/docker && docker compose ps

# Operations commands
ingest:
	@echo "📥 Triggering document ingestion..."
	@curl -X POST http://localhost:8000/ingest
	@echo ""

test:
	@echo "🧪 Running tests..."
	cd infra/docker && docker compose exec api pytest

shell-api:
	@echo "🐚 Opening shell in API container..."
	cd infra/docker && docker compose exec api bash

shell-web:
	@echo "🐚 Opening shell in web container..."
	cd infra/docker && docker compose exec web sh

# Cleanup commands
clean:
	@echo "🧹 Removing containers and volumes..."
	cd infra/docker && docker compose down -v

clean-all: clean
	@echo "🧹 Removing images..."
	docker rmi -f $$(docker images -q "lifeblood-*" 2>/dev/null) 2>/dev/null || true
	@echo "✅ Cleanup complete!"
