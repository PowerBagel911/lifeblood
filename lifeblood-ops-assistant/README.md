# Lifeblood Ops Assistant

> An AI-powered Retrieval-Augmented Generation (RAG) system designed to provide intelligent answers about blood donation operations, donor eligibility, and standard operating procedures.

## Overview

Lifeblood Ops Assistant is a knowledge management system that combines Large Language Models (LLMs) with a vector database to deliver accurate, contextual responses about blood bank operations. The system ingests organizational documentation, indexes it using semantic embeddings, and generates AI responses grounded in your actual documents - reducing hallucinations and ensuring answers are backed by authoritative sources.

**Key Capabilities:**
- **Document-Grounded Responses**: All answers cite specific source documents
- **Two Response Modes**: Choose between comprehensive or concise answers
- **Real-Time Document Ingestion**: Add new knowledge base content on demand
- **Semantic Search**: Uses embeddings for intelligent context retrieval
- **Citation Tracking**: Every response includes source references with document IDs

## Features

- **RAG Pipeline**: Production-ready Retrieval-Augmented Generation using LangChain
- **Vector Search**: ChromaDB-powered semantic search with Google Gemini embeddings
- **Dual Response Modes**:
  - `comprehensive`: Detailed, thorough explanations with full context
  - `concise`: Brief, direct answers for quick reference
- **Document Management**: Automated ingestion pipeline with chunking and metadata preservation
- **Web Interface**: React/TypeScript frontend with real-time chat and citation display
- **REST API**: FastAPI backend with comprehensive logging and error handling
- **Observability**: Distributed tracing with request IDs for debugging and monitoring
- **Type Safety**: Pydantic schemas for request/response validation

## Architecture

The system follows a clean, layered architecture designed for maintainability and scalability:

```
┌─────────────────┐
│   Web Client    │  React + TypeScript + Tailwind CSS
│   (Port 3000)   │  Chat interface, mode selection, citation display
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│   FastAPI       │  Python 3.11 + FastAPI + Uvicorn
│   Backend       │  /ask, /ingest endpoints
│   (Port 8000)   │  Request validation, logging, CORS
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌──────┐  ┌──────────┐
│ RAG  │  │ Ingest   │
│ Flow │  │ Pipeline │
└──┬───┘  └────┬─────┘
   │           │
   │    ┌──────┴──────┐
   │    ▼             ▼
   │  ┌────────┐  ┌──────────┐
   │  │Chunking│  │  File    │
   │  │        │  │ Loaders  │
   │  └────────┘  └──────────┘
   │
   ├─────────┬─────────┐
   ▼         ▼         ▼
┌──────┐ ┌────────┐ ┌─────┐
│Vector│ │Embedder│ │ LLM │
│Store │ │        │ │     │
│      │ │ Gemini │ │Gemini│
│Chroma│ │Embed   │ │ API │
└──────┘ └────────┘ └─────┘
```

### Components

- **Web Interface** (`apps/web`): React SPA with TypeScript, provides chat UI, mode selection, and citation display
- **API Service** (`apps/api`): FastAPI application handling question answering and document ingestion
- **RAG Pipeline** (`services/rag_pipeline.py`): Orchestrates retrieval and generation using LangChain
- **Vector Store** (ChromaDB): Persistent embeddings storage with semantic similarity search
- **LLM Integration**: Google Gemini for both embeddings (`text-embedding-004`) and generation (`gemini-1.5-flash`)
- **Document Processing**: File loaders and chunking utilities with metadata preservation

For detailed architecture decisions, see [docs/architecture.md](docs/architecture.md) and [ADRs](docs/decisions/).

## Technology Stack

**Backend:**
- Python 3.11
- FastAPI + Uvicorn
- LangChain (RAG orchestration)
- ChromaDB (vector database)
- Google Gemini API (LLM + embeddings)
- Pydantic (data validation)
- pytest (testing)

**Frontend:**
- React 18
- TypeScript
- Vite (build tool)
- Tailwind CSS
- Lucide React (icons)

**Infrastructure:**
- Docker & Docker Compose
- Conda (Python environment management)

## Prerequisites

- **Python 3.11+** via [Conda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/distribution)
- **Node.js 18+** and npm (for frontend development)
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))
- **Git**

## Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd lifeblood-ops-assistant
```

### 2. Backend Setup

#### Create Conda Environment

```bash
conda env create -f environment.yml
conda activate lifeblood-ops-assistant
```

This installs all Python dependencies including FastAPI, LangChain, ChromaDB, and Google GenAI SDK.

#### Configure Environment Variables

```bash
cp env.template .env
```

Edit `.env` and add your API key:

```env
GEMINI_API_KEY=your_api_key_here
GOOGLE_API_KEY=              # Leave blank (deprecated)
GEMINI_MODEL=gemini-1.5-flash
GEMINI_EMBED_MODEL=models/text-embedding-004
LLM_PROVIDER=gemini
EMBED_PROVIDER=gemini
CHROMA_PERSIST_DIR=.chroma
```

⚠️ **Important**: Set ONLY `GEMINI_API_KEY`. Do not set both `GEMINI_API_KEY` and `GOOGLE_API_KEY`.

#### Initialize Vector Database

Ingest the sample documents into ChromaDB:

```bash
cd apps/api
# Start the API server first
uvicorn src.app.main:app --reload --port 8000
```

In a separate terminal, ingest documents:

```bash
curl -X POST http://localhost:8000/ingest
```

You should see a response like:
```json
{
  "indexed_docs": 5,
  "indexed_chunks": 42,
  "trace_id": "..."
}
```

### 3. Frontend Setup

```bash
cd apps/web
npm install
npm run dev
```

The web interface will be available at `http://localhost:5173` (Vite default port).

### 4. Verify Installation

**Test the API:**

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the donor eligibility requirements?", "mode": "concise"}'
```

**Or use the web interface:**

1. Open `http://localhost:5173`
2. Select a response mode (Comprehensive or Concise)
3. Type a question about blood donation operations
4. Review the answer and citations

## Docker Deployment 🐳

### Quick Start with Docker

The easiest way to run the entire application:

**Windows (PowerShell):**
```powershell
cd infra/docker
./start.ps1
```

**Linux/Mac:**
```bash
cd infra/docker
chmod +x start.sh
./start.sh
```

The script will:
1. Check for `.env` configuration
2. Let you choose production or development mode
3. Build and start all services
4. Display access URLs and next steps

### Manual Docker Setup

**Prerequisites:**
- Docker Engine 20.10+
- Docker Compose v2.0+

**1. Configure environment:**
```bash
cp env.template .env
# Edit .env and add your GEMINI_API_KEY
```

**2. Production deployment:**
```bash
cd infra/docker
docker compose up --build -d
```

**3. Access the application:**
- Web UI: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**4. Ingest documents:**
```bash
curl -X POST http://localhost:8000/ingest
```

### Development with Hot Reload

For local development with instant code updates:

```bash
cd infra/docker
docker compose -f compose.dev.yaml up
```

Features:
- ✅ Python changes reload automatically (FastAPI --reload)
- ✅ React changes reload via Vite HMR
- ✅ Source code mounted as volumes
- ✅ Debug logging enabled

### Docker Commands Cheat Sheet

```bash
# View logs
docker compose logs -f          # All services
docker compose logs -f api      # API only
docker compose logs -f web      # Web only

# Stop services
docker compose down             # Stop and remove containers
docker compose down -v          # Also remove volumes (resets database)

# Restart services
docker compose restart          # Restart all
docker compose restart api      # Restart API only

# Service status
docker compose ps               # List running services
docker compose top              # Show running processes

# Execute commands
docker compose exec api pytest                    # Run tests
docker compose exec api bash                      # Shell into API
docker compose exec api python -m pip list        # List packages

# Rebuild after code changes
docker compose up --build -d
```

### Docker Architecture

The Docker setup includes:

**Services:**
- **api**: FastAPI backend (Python 3.11) on port 8000
- **web**: React frontend (nginx) on port 3000

**Volumes:**
- **chroma-data**: Persistent vector database storage
- **data/**: Document files for ingestion (bind mount)

**Networking:**
- Internal bridge network for service communication
- Web container proxies `/api` requests to backend

**Images:**
- API: Custom Python image with all dependencies (~500MB)
- Web: Multi-stage build (Node builder + nginx runtime) (~50MB)

See [infra/docker/README.md](infra/docker/README.md) for detailed Docker documentation.

## Running the Application

### Option 1: Docker (Recommended for Quick Start)

**Production:**
```bash
cd infra/docker
docker compose up -d
```

**Development (with hot-reload):**
```bash
cd infra/docker
docker compose -f compose.dev.yaml up
```

**Access:**
- Web: http://localhost:3000
- API: http://localhost:8000/docs

### Option 2: Local Development (Native)

**Backend (Terminal 1):**
```bash
conda activate lifeblood-ops-assistant
cd apps/api
uvicorn src.app.main:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd apps/web
npm run dev
```

**Access:**
- Web: http://localhost:5173 (Vite dev server)
- API: http://localhost:8000/docs

### Option 3: Production Deployment

For production deployments, Docker is recommended. See the **Docker Deployment** section above and [infra/docker/README.md](infra/docker/README.md) for:
- Environment configuration
- Secrets management
- Scaling strategies
- Monitoring setup
- Cloud deployment examples (AWS, GCP, Azure)

## Usage

### Asking Questions
- Monitoring and logging

## Usage

### Asking Questions

**Via Web UI:**
1. Select response mode: `comprehensive` or `concise`
2. Type your question
3. View answer with inline citations
4. Expand the Sources panel to see full citation details

**Via API:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How should plasma be handled after collection?",
    "mode": "comprehensive",
    "top_k": 5
  }'
```

**Response:**
```json
{
  "question": "How should plasma be handled after collection?",
  "answer": "According to the plasma handling guidelines, plasma must be frozen within 8 hours...",
  "citations": [
    {
      "doc_id": "plasma_handling",
      "chunk_id": "plasma_handling_chunk_3",
      "text": "Plasma units must be frozen solid within 8 hours...",
      "title": "Plasma Handling Procedures"
    }
  ],
  "mode": "comprehensive",
  "trace_id": "abc-123-def-456"
}
```

### Adding Documents

Place markdown or text files in `data/docs/`, then trigger ingestion:

```bash
curl -X POST http://localhost:8000/ingest
```

The system will:
1. Load all documents from `data/docs/`
2. Chunk them into ~2000 character segments with 200 character overlap
3. Generate embeddings using Gemini
4. Store in ChromaDB with metadata (doc_id, title, chunk boundaries)

## Project Structure

```
lifeblood-ops-assistant/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── src/
│   │   │   └── app/
│   │   │       ├── main.py           # Application entry point
│   │   │       ├── core/             # Config, schemas, logging
│   │   │       ├── routes/           # API endpoints (ask, ingest)
│   │   │       ├── services/         # RAG pipeline, LLM, embeddings
│   │   │       └── utils/            # Chunking, file loaders
│   │   └── tests/                    # pytest test suite
│   └── web/                    # React frontend
│       └── src/
│           ├── components/           # React components
│           ├── app/api/              # API client
│           └── types.ts              # TypeScript types
├── data/
│   └── docs/                   # Source documents for ingestion
├── docs/                       # Documentation
│   ├── architecture.md
│   ├── demo-script.md
│   ├── threat-model-lite.md
│   └── decisions/              # Architectural Decision Records
├── infra/
│   └── docker/                 # Docker configuration
├── environment.yml             # Conda dependencies
└── env.template                # Environment variables template
```

## Testing

```bash
cd apps/api
pytest
```

Run specific test files:
```bash
pytest tests/test_rag_pipeline.py -v
pytest tests/test_chunking.py -v
```

## API Reference

### POST `/ask`

Ask a question to the knowledge base.

**Request Body:**
```typescript
{
  question: string;      // Question text (required)
  mode: "comprehensive" | "concise";  // Response mode (required)
  top_k?: number;        // Number of context chunks (default: 5)
}
```

**Response:**
```typescript
{
  question: string;
  answer: string;
  citations: Citation[];
  mode: string;
  trace_id: string;
}
```

### POST `/ingest`

Ingest documents from `data/docs/` into the vector database.

**Response:**
```typescript
{
  indexed_docs: number;    // Number of documents processed
  indexed_chunks: number;  // Number of chunks indexed
  trace_id: string;
}
```

## Configuration

All configuration is environment-based. See `env.template` for available options:

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | (required) |
| `GEMINI_MODEL` | LLM model for generation | `gemini-1.5-flash` |
| `GEMINI_EMBED_MODEL` | Embedding model | `models/text-embedding-004` |
| `LLM_PROVIDER` | LLM provider name | `gemini` |
| `EMBED_PROVIDER` | Embedding provider | `gemini` |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path | `.chroma` |

## Safety & Ethics

### Security Considerations

- **API Key Protection**: Never commit `.env` files. Use secrets management in production.
- **Input Validation**: All requests validated via Pydantic schemas.
- **CORS**: Configure allowed origins in production (`main.py`).
- **Rate Limiting**: Implement rate limiting for production deployments.
- **Authentication**: Add authentication before exposing publicly (local prototype only).

### Ethical Guidelines

- **Source Attribution**: All AI responses include citations to source documents.
- **Transparency**: System clearly indicates AI-generated content.
- **Human Oversight**: Critical decisions should be verified by qualified personnel.
- **Privacy**: No personal or patient data should be included in training documents.

### Privacy Protection

- **No PII**: Ensure documents contain no personally identifiable information.
- **Request Logging**: Trace IDs for debugging, but avoid logging sensitive data.
- **Data Retention**: Configure ChromaDB persistence and cleanup policies.

For detailed security analysis, see [docs/threat-model-lite.md](docs/threat-model-lite.md).

## Troubleshooting

**API key errors:**
- Verify `GEMINI_API_KEY` is set in `.env`
- Ensure only one API key variable is set (not both `GEMINI_API_KEY` and `GOOGLE_API_KEY`)

**No documents ingested:**
- Check that files exist in `data/docs/`
- Ensure files are `.md` or `.txt` format
- Review API logs for file loading errors

**Empty responses:**
- Run `/ingest` endpoint to populate vector database
- Check ChromaDB persistence directory exists
- Verify embedding model is accessible

**Frontend connection issues:**
- Ensure API is running on port 8000
- Check CORS configuration in `main.py`
- Verify API client URL in `apps/web/src/app/api/client.ts`

## Roadmap

- [ ] **Multi-modal Support**: Add PDF and Word document loaders
- [ ] **Advanced RAG**: Implement query rewriting and multi-hop reasoning
- [ ] **Authentication**: Add user authentication and role-based access control
- [ ] **Evaluation**: Build automated RAG evaluation pipeline with golden questions
- [ ] **Production Monitoring**: Integrate observability tools (Prometheus, Grafana)
- [ ] **Scalability**: Migrate to production vector database (Pinecone, Weaviate)
- [ ] **Fine-tuning**: Experiment with domain-specific model fine-tuning

## License

This project is for educational and demonstration purposes. Please review licensing requirements for dependencies (LangChain, ChromaDB, Google Gemini) before commercial use.

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Google Gemini API](https://ai.google.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [RAG Best Practices](https://python.langchain.com/docs/use_cases/question_answering/)

---

**Built with ❤️**
