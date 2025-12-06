# Lifeblood Ops Assistant

> An AI-powered Retrieval-Augmented Generation (RAG) system designed to provide intelligent answers about blood donation operations, donor eligibility, and standard operating procedures.

## Overview

Lifeblood Ops Assistant is a knowledge management system that combines Large Language Models (LLMs) with a vector database to deliver accurate, contextual responses about blood bank operations. The system ingests organizational documentation, indexes it using semantic embeddings, and generates AI responses grounded in your actual documents—reducing hallucinations and ensuring answers are backed by authoritative sources.

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

## Running the Application

### Development Mode

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

### Using Docker Compose

```bash
docker compose -f infra/docker/compose.yaml up --build
```

This starts both API (port 3001) and Web (port 3000) services.

### Production Deployment

See `infra/docker/` for Dockerfiles and `docs/architecture.md` for production considerations including:
- API key security (use secrets management)
- CORS configuration
- Rate limiting
- Authentication/authorization
- Vector store persistence
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

## Contributing

Contributions are welcome! This is a prototype system demonstrating RAG best practices.

**Development Guidelines:**
1. Follow existing code structure and naming conventions
2. Add tests for new features (`apps/api/tests/`)
3. Update documentation for API changes
4. Use type hints in Python and TypeScript
5. Follow PEP 8 for Python code
6. Run linters before committing: `pytest` and `npm run lint`

## License

This project is for educational and demonstration purposes. Please review licensing requirements for dependencies (LangChain, ChromaDB, Google Gemini) before commercial use.

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Google Gemini API](https://ai.google.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [RAG Best Practices](https://python.langchain.com/docs/use_cases/question_answering/)

---

**Built with ❤️ for blood donation operations teams**
