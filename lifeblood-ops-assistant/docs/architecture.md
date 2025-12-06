# Architecture

## Overview

Lifeblood Ops Assistant is built on a **Retrieval-Augmented Generation (RAG)** architecture that combines the power of Large Language Models with a knowledge base of organizational documents. The system retrieves relevant context from a vector database and uses it to ground LLM responses, ensuring accuracy and reducing hallucinations.

**Core Design Principles:**
- **Separation of Concerns**: Clean layering between API, business logic, and data access
- **Type Safety**: Pydantic schemas and TypeScript for end-to-end type checking
- **Observability**: Distributed tracing with request IDs, structured logging
- **Extensibility**: Pluggable LLM and embedding providers via LangChain
- **Testability**: Modular components with comprehensive test coverage

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         Client Layer                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  React Web Application (TypeScript + Vite)             │  │
│  │  - Chat interface with message history                 │  │
│  │  - Mode selector (comprehensive/concise)               │  │
│  │  - Citation display panel                              │  │
│  │  - Real-time API communication                         │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTP/REST (JSON)
                           │ CORS-enabled
┌──────────────────────────▼───────────────────────────────────┐
│                      API Layer (FastAPI)                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  main.py - Application Bootstrap                       │  │
│  │  - CORS middleware                                     │  │
│  │  - Request tracing middleware                          │  │
│  │  - Lifespan management                                 │  │
│  │  - API key validation                                  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────┐         ┌──────────────────────────┐  │
│  │  /ask Endpoint    │         │  /ingest Endpoint        │  │
│  │  - Request valid. │         │  - File loading          │  │
│  │  - RAG pipeline   │         │  - Document chunking     │  │
│  │  - Response build │         │  - Vector indexing       │  │
│  └─────────┬─────────┘         └──────────┬───────────────┘  │
│            │                               │                  │
└────────────┼───────────────────────────────┼──────────────────┘
             │                               │
             │         ┌─────────────────────┘
             │         │
┌────────────▼─────────▼───────────────────────────────────────┐
│                     Service Layer                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  RAG Pipeline (rag_pipeline.py)                        │  │
│  │  ┌──────────────────────────────────────────────────┐ │  │
│  │  │ 1. Query Analysis & Validation                   │ │  │
│  │  │ 2. Semantic Retrieval (top_k chunks)             │ │  │
│  │  │ 3. Context Ranking & Filtering                   │ │  │
│  │  │ 4. Prompt Construction (mode-specific)           │ │  │
│  │  │ 5. LLM Generation                                │ │  │
│  │  │ 6. Citation Extraction & Formatting              │ │  │
│  │  └──────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ LLM Client   │  │ Embeddings   │  │ Retrieval        │   │
│  │ (llm_client) │  │ (embeddings) │  │ (retrieval)      │   │
│  │              │  │              │  │                  │   │
│  │ - Gemini API │  │ - Embed gen  │  │ - Similarity     │   │
│  │ - Prompts    │  │ - Caching    │  │ - Ranking        │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  LangChain Factory (langchain_factory.py)             │  │
│  │  - Builds LangChain components from config            │  │
│  │  - Manages provider-specific initialization           │  │
│  │  - Abstracts LangChain complexity                     │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                      Data Layer                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  ChromaDB (Vector Store)                               │  │
│  │  - Persistent storage (.chroma directory)              │  │
│  │  - Embeddings: text-embedding-004 (768 dimensions)     │  │
│  │  - Similarity: Cosine distance                         │  │
│  │  - Metadata: doc_id, chunk_id, title, positions       │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Document Storage                                      │  │
│  │  - Source files: data/docs/*.md, *.txt                 │  │
│  │  - Chunking: ~2000 chars with 200 char overlap        │  │
│  │  - Metadata preservation                               │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│                    External Services                          │
│  ┌──────────────────────────────────────────┐                 │
│  │  Google Gemini API                       │                 │
│  │  - LLM: gemini-1.5-flash                 │                 │
│  │  - Embeddings: text-embedding-004        │                 │
│  │  - Rate limiting: Per API key            │                 │
│  └──────────────────────────────────────────┘                 │
└───────────────────────────────────────────────────────────────┘
```

## Components

### 1. Web Interface (`apps/web`)

**Technology**: React 18, TypeScript, Vite, Tailwind CSS

**Responsibilities:**
- User interaction and input validation
- Chat message display with markdown rendering
- Citation panel with expandable source details
- Mode selection (comprehensive vs. concise)
- Real-time loading states and error handling

**Key Files:**
- `ChatPage.tsx`: Main chat interface component
- `ChatBox.tsx`: Message input with mode selector
- `SourcesPanel.tsx`: Citation display
- `client.ts`: Type-safe API client with error handling

### 2. API Service (`apps/api`)

**Technology**: FastAPI, Python 3.11, Uvicorn

**Responsibilities:**
- HTTP request handling and validation
- CORS configuration for frontend access
- Request tracing with unique IDs
- Error handling and logging
- API key validation on startup

**Key Files:**
- `main.py`: Application bootstrap, middleware, lifespan events
- `core/config.py`: Environment-based configuration with Pydantic
- `core/schemas.py`: Request/response models
- `core/logging.py`: Structured logging setup

### 3. RAG Pipeline (`services/rag_pipeline.py`)

**Core RAG Flow:**

```python
# Simplified RAG pipeline logic
def ask(question: str, mode: str, top_k: int) -> dict:
    # 1. Retrieve relevant chunks from vector store
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    relevant_docs = retriever.invoke(question)
    
    # 2. Build context from retrieved documents
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    
    # 3. Construct mode-specific prompt
    prompt = build_prompt(question, context, mode)
    
    # 4. Generate answer with LLM
    answer = llm.invoke(prompt)
    
    # 5. Extract citations from retrieved docs
    citations = build_citations(relevant_docs)
    
    return {"answer": answer, "citations": citations}
```

**Responsibilities:**
- Semantic retrieval using vector similarity
- Context ranking and relevance filtering
- Prompt engineering for different modes
- LLM interaction and response parsing
- Citation extraction and formatting

### 4. Embedding Service (`services/embeddings.py`)

**Responsibilities:**
- Generate embeddings for queries and documents
- Caching for performance optimization
- Batch processing for ingestion
- Error handling for API failures

**Model**: Google `text-embedding-004` (768-dimensional vectors)

### 5. LLM Client (`services/llm_client.py`)

**Responsibilities:**
- Interface to Gemini API
- Prompt template management
- Response parsing and validation
- Token counting and rate limit handling

**Model**: `gemini-1.5-flash` (fast, cost-effective, context window up to 1M tokens)

### 6. Retrieval Service (`services/retrieval.py`)

**Responsibilities:**
- Vector similarity search
- Metadata filtering
- Result ranking and deduplication
- Relevance scoring

**Search Strategy**: Cosine similarity with top-k retrieval (default k=5)

### 7. Document Processing (`utils/`)

**File Loaders** (`file_loaders.py`):
- Load `.md` and `.txt` files from directories
- Preserve document metadata (filename, path, title)
- Handle encoding issues gracefully

**Chunking** (`chunking.py`):
- Split documents into ~2000 character chunks
- 200 character overlap for context continuity
- Preserve chunk boundaries and positions
- Attach metadata to each chunk (doc_id, chunk_id, start/end positions)

### 8. Vector Store (ChromaDB)

**Persistence**: Local directory (`.chroma/`)

**Schema:**
```python
{
    "id": "doc_123_chunk_5",           # Unique identifier
    "embedding": [0.1, 0.2, ...],      # 768-dim vector
    "metadata": {
        "doc_id": "plasma_handling",   # Source document
        "chunk_id": "chunk_5",          # Chunk identifier
        "title": "Plasma Handling",    # Document title
        "start": 1000,                 # Character start position
        "end": 3000                    # Character end position
    },
    "document": "Plasma must be..."   # Original text
}
```

## Data Flow

### Question Answering Flow

```
User Question
    │
    ├─► Web UI validates input
    │
    ├─► POST /ask {"question": "...", "mode": "concise"}
    │
    ├─► API validates with Pydantic schema
    │
    ├─► RAG Pipeline:
    │   │
    │   ├─► Generate query embedding (768-dim vector)
    │   │
    │   ├─► Vector similarity search in ChromaDB (top_k=5)
    │   │   Returns: 5 most similar document chunks
    │   │
    │   ├─► Build context from retrieved chunks
    │   │
    │   ├─► Construct prompt:
    │   │   "You are an expert assistant. Use ONLY the following
    │   │    context to answer. Context: {chunks}. Question: {q}"
    │   │
    │   ├─► Call Gemini API with prompt
    │   │
    │   ├─► Parse LLM response
    │   │
    │   └─► Extract citations from retrieved docs
    │
    └─► Return JSON response with answer + citations
```

### Document Ingestion Flow

```
Document Files (data/docs/*.md)
    │
    ├─► POST /ingest (authenticated in production)
    │
    ├─► Load all files from data/docs/
    │   - DirectoryLoader scans recursively
    │   - Reads .md and .txt files
    │
    ├─► Chunk documents
    │   - Split into ~2000 char chunks
    │   - 200 char overlap
    │   - Preserve metadata
    │
    ├─► Generate embeddings
    │   - Batch process chunks
    │   - Call Gemini embedding API
    │   - Create 768-dim vectors
    │
    ├─► Store in ChromaDB
    │   - Persist to .chroma/ directory
    │   - Index by embedding similarity
    │   - Attach metadata
    │
    └─► Return ingestion stats
        {"indexed_docs": 5, "indexed_chunks": 42}
```

## Technology Stack

### Backend Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Runtime** | Python 3.11 | Modern Python with type hints, performance improvements |
| **API Framework** | FastAPI 0.104+ | High-performance async API with automatic OpenAPI docs |
| **Server** | Uvicorn | ASGI server with hot reload for development |
| **RAG Framework** | LangChain 0.1+ | RAG orchestration, document loaders, prompt management |
| **Vector DB** | ChromaDB 0.4+ | Embedded vector database with persistence |
| **LLM Provider** | Google Gemini | Fast, cost-effective LLM and embeddings |
| **Validation** | Pydantic 2.0+ | Type-safe data validation and serialization |
| **Testing** | pytest | Unit and integration testing |
| **HTTP Client** | httpx | Async HTTP client for external APIs |

### Frontend Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | React 18 | Component-based UI with hooks |
| **Language** | TypeScript 5.2+ | Type safety and better developer experience |
| **Build Tool** | Vite 5.0+ | Fast dev server and optimized builds |
| **Styling** | Tailwind CSS 3.3+ | Utility-first CSS framework |
| **Icons** | Lucide React | Modern, customizable icon library |
| **Linting** | ESLint + TS Plugin | Code quality and consistency |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Containers** | Docker + Docker Compose | Containerized deployment |
| **Env Management** | Conda | Python environment isolation |
| **Version Control** | Git | Source code management |

## Design Decisions

### Why RAG over Fine-Tuning?

**Chosen**: Retrieval-Augmented Generation (RAG)

**Rationale**:
- **Dynamic Updates**: Add/remove knowledge without retraining
- **Source Attribution**: Citations for every answer
- **Cost-Effective**: No GPU training costs, pay-per-API-call
- **Lower Latency**: No model hosting infrastructure needed
- **Hallucination Reduction**: Grounded in actual documents

See [ADR-0001](decisions/adr-0001-rag.md) for detailed analysis.

### Why ChromaDB?

**Chosen**: ChromaDB (embedded mode)

**Rationale**:
- **Simplicity**: Single-file persistence, no separate server
- **Fast Prototyping**: Zero-config setup for local development
- **LangChain Integration**: First-class support in LangChain ecosystem
- **Good Enough**: Handles thousands of documents efficiently

**Production Alternatives**: Pinecone, Weaviate, Qdrant for scale

See [ADR-0002](decisions/adr-0002-vector-store.md) for comparison.

### Why Two Response Modes?

**Comprehensive Mode**:
- Detailed explanations with full context
- Multiple perspectives and nuances
- Educational and training use cases

**Concise Mode**:
- Quick reference for experienced users
- Time-sensitive situations
- Mobile or low-bandwidth contexts

**Implementation**: Different prompt templates, same retrieval pipeline

### Why FastAPI?

- **Async Support**: Native async/await for I/O-bound operations
- **Type Safety**: Pydantic integration for request/response validation
- **Auto Documentation**: OpenAPI/Swagger UI out of the box
- **Performance**: One of the fastest Python frameworks
- **Developer Experience**: Intuitive API, great error messages

## Security Considerations

### API Key Management
- ✅ Environment variables for sensitive data
- ✅ `.env` in `.gitignore`
- ❌ **TODO**: Use secrets management in production (AWS Secrets Manager, Azure Key Vault)

### Authentication & Authorization
- ⚠️ **Current**: No authentication (local prototype only)
- ❌ **TODO**: Add JWT-based auth for `/ingest` endpoint
- ❌ **TODO**: Role-based access control (RBAC)

### Input Validation
- ✅ Pydantic schemas validate all API inputs
- ✅ Question length limits
- ✅ Mode enumeration (only `comprehensive` | `concise`)

### CORS Configuration
- ⚠️ **Current**: Permissive CORS for local development
- ❌ **TODO**: Whitelist specific origins in production

### Data Privacy
- ✅ No PII in sample documents
- ✅ Request trace IDs for debugging (no question text in traces)
- ❌ **TODO**: Implement data retention policies
- ❌ **TODO**: Add audit logging for sensitive operations

### Rate Limiting
- ❌ **TODO**: Implement rate limiting per user/IP
- ❌ **TODO**: Configure Gemini API quotas

See [docs/threat-model-lite.md](threat-model-lite.md) for full security analysis.

## Performance Characteristics

### Latency Breakdown (Typical Query)

```
Total: ~2-4 seconds
├─ API overhead: ~50ms
├─ Embedding generation: ~300ms (query embedding)
├─ Vector search: ~100ms (ChromaDB lookup)
├─ LLM generation: ~1.5-3s (Gemini API, varies by answer length)
└─ Response serialization: ~50ms
```

### Scalability Limits

| Resource | Current Limit | Bottleneck |
|----------|---------------|------------|
| **Documents** | ~1,000 docs | ChromaDB memory usage |
| **Concurrent Users** | ~10 users | Single Uvicorn worker |
| **Embeddings** | ~10,000 chunks | ChromaDB query time |
| **API Rate** | Gemini API limits | External service quota |

### Optimization Strategies

**Short Term**:
- Cache embeddings for common queries
- Batch document ingestion
- Use connection pooling for Gemini API

**Long Term**:
- Migrate to client-server vector DB (Pinecone, Weaviate)
- Add Redis for query result caching
- Implement embedding model caching
- Use async workers for ingestion
- Deploy on Kubernetes with horizontal scaling

## Monitoring & Observability

### Current Logging

- **Structured Logging**: JSON format with trace IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Request Tracing**: Unique trace_id per request
- **Log Locations**: stdout (container-friendly)

### Recommended Production Monitoring

**Metrics** (Prometheus + Grafana):
- API latency (p50, p95, p99)
- Request rate and error rate
- LLM API latency and cost
- Vector search latency
- ChromaDB size and query time

**Logging** (ELK Stack or CloudWatch):
- Request/response logs with trace IDs
- Error logs with stack traces
- Audit logs for ingestion operations

**Alerting**:
- API error rate > 5%
- P95 latency > 5s
- Gemini API quota exhaustion
- ChromaDB disk space

## Future Enhancements

### Short Term (1-2 Months)
- [ ] Add PDF and DOCX document loaders
- [ ] Implement query rewriting for better retrieval
- [ ] Add user feedback mechanism (thumbs up/down)
- [ ] Build automated evaluation pipeline with golden questions
- [ ] Add authentication for `/ingest` endpoint

### Medium Term (3-6 Months)
- [ ] Multi-hop reasoning for complex questions
- [ ] Conversational memory (chat history context)
- [ ] Support for multiple vector stores (user selection)
- [ ] Advanced RAG techniques (HyDE, query decomposition)
- [ ] Kubernetes deployment manifests

### Long Term (6+ Months)
- [ ] Fine-tuned embeddings for domain-specific retrieval
- [ ] Multi-modal support (images, tables in documents)
- [ ] Federated search across multiple knowledge bases
- [ ] Agent-based workflows with tool use
- [ ] Real-time document sync from CMS/wiki

## References

- [LangChain RAG Documentation](https://python.langchain.com/docs/use_cases/question_answering/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Google Gemini API](https://ai.google.dev/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [RAG Survey Paper](https://arxiv.org/abs/2312.10997) (Lewis et al., 2020)
