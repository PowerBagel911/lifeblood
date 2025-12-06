# Docker Deployment Guide

This directory contains Docker configuration for the Lifeblood Ops Assistant.

## Files

- **Dockerfile.api**: Production-ready FastAPI backend image
- **Dockerfile.web**: Multi-stage React frontend build with nginx
- **compose.yaml**: Production deployment configuration
- **compose.dev.yaml**: Development setup with hot-reload

## Quick Start

### Production Deployment

1. **Set up environment variables:**

```bash
# From project root
cp env.template .env
# Edit .env and add your GEMINI_API_KEY
```

2. **Build and start services:**

```bash
cd infra/docker
docker compose up --build -d
```

3. **Verify services are running:**

```bash
docker compose ps
docker compose logs -f
```

4. **Access the application:**
- Web UI: http://localhost:3000
- API Docs: http://localhost:8000/docs

5. **Ingest documents:**

```bash
curl -X POST http://localhost:8000/ingest
```

### Development Mode with Hot Reload

```bash
cd infra/docker
docker compose -f compose.dev.yaml up
```

This provides:
- ✅ Python hot-reload (changes reflected immediately)
- ✅ React hot-reload (Vite dev server)
- ✅ Volume mounts for source code
- ✅ Debug logging enabled

## Service Details

### API Service
- **Port**: 8000
- **Base Image**: python:3.11-slim
- **Volume**: ChromaDB data persisted in named volume
- **Health Check**: GET /docs endpoint
- **Environment**:
  - `GEMINI_API_KEY` (required)
  - `CHROMA_PERSIST_DIR=/app/.chroma`
  - `LOG_LEVEL=INFO`

### Web Service
- **Port**: 3000 (nginx serves on port 80 inside container)
- **Production**: Multi-stage build with nginx
- **Development**: Vite dev server with hot reload
- **Proxy**: /api requests forwarded to backend

## Commands

### Start services
```bash
docker compose up -d
```

### View logs
```bash
docker compose logs -f
docker compose logs -f api
docker compose logs -f web
```

### Stop services
```bash
docker compose down
```

### Rebuild after code changes
```bash
docker compose up --build -d
```

### Remove volumes (reset database)
```bash
docker compose down -v
```

### Execute commands in containers
```bash
# Run pytest in API container
docker compose exec api pytest

# Access API shell
docker compose exec api bash

# View ChromaDB contents
docker compose exec api ls -la /app/.chroma
```

## Environment Variables

Required in `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
GEMINI_EMBED_MODEL=models/text-embedding-004
LLM_PROVIDER=gemini
EMBED_PROVIDER=gemini
```

Optional:
- `APP_ENV` (default: production)
- `LOG_LEVEL` (default: INFO)

## Volumes

### Named Volumes
- **chroma-data**: Persists vector database between container restarts
- **chroma-data-dev**: Development database (separate from production)

### Bind Mounts
- `../../data:/app/data`: Document files for ingestion
- Development only:
  - `../../apps/api/src:/app/api/src`: API source code hot-reload
  - `../../apps/web:/app`: Web source code hot-reload

## Networking

Services communicate via Docker network:
- **Production**: `lifeblood-network`
- **Development**: `lifeblood-network-dev`

API is accessible from web container as `http://api:8000`.

## Troubleshooting

### Port already in use
```bash
# Change ports in compose.yaml
ports:
  - "8080:8000"  # Use 8080 instead of 8000
```

### API key not found
```bash
# Ensure .env file exists in project root
ls -la ../../.env

# Check environment variables in container
docker compose exec api env | grep GEMINI
```

### ChromaDB permission errors
```bash
# Fix volume permissions
docker compose down -v
docker volume rm docker_chroma-data
docker compose up -d
```

### Build cache issues
```bash
# Force rebuild without cache
docker compose build --no-cache
docker compose up -d
```

### Web can't connect to API
- Verify API is healthy: `docker compose ps`
- Check API logs: `docker compose logs api`
- Verify CORS settings in `apps/api/src/app/main.py`
- Test API directly: `curl http://localhost:8000/docs`

## Production Considerations

### Security
- [ ] Use secrets management (not .env in production)
- [ ] Enable HTTPS with TLS certificates
- [ ] Configure rate limiting
- [ ] Add authentication/authorization
- [ ] Restrict CORS origins

### Performance
- [ ] Use production WSGI server (gunicorn with uvicorn workers)
- [ ] Enable nginx caching
- [ ] Configure resource limits (CPU, memory)
- [ ] Set up health checks and restart policies

### Monitoring
- [ ] Add Prometheus metrics exporter
- [ ] Configure log aggregation
- [ ] Set up alerts for service health
- [ ] Monitor ChromaDB disk usage

### Scaling
```yaml
# Scale API horizontally
docker compose up -d --scale api=3

# Add load balancer (nginx/traefik)
# Add Redis for session management
# Use external vector DB (Pinecone, Weaviate)
```

## Example Deployment Commands

### Build and push to registry
```bash
docker compose build
docker tag docker_api:latest your-registry/lifeblood-api:v1.0
docker push your-registry/lifeblood-api:v1.0
```

### Deploy to cloud (example)
```bash
# AWS ECS
aws ecs create-service --cli-input-json file://ecs-service.json

# Google Cloud Run
gcloud run deploy lifeblood-api --image gcr.io/project/api:latest

# Azure Container Instances
az container create --resource-group rg --file compose.yaml
```

## Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Nginx Docker Image](https://hub.docker.com/_/nginx)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
