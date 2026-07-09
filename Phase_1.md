# Email RAG Chatbot — End-to-End Workflow

This document explains how the application components connect and work together, from ingesting email DOCX files to answering user chat queries using Retrieval-Augmented Generation (RAG).

## High-Level Flow

- User interacts with the Frontend (UI).
- Frontend calls Backend API endpoints (`/api/ingest`, `/api/chat`, `/api/emails`, `/api/health`).
- Ingest path: parse DOCX → store email in DB → chunk into semantic pieces → embed & persist chunks in Chroma DB and build BM25 index.
- Query path: retrieve candidate chunks (BM25 + dense/Chroma) → filter by confidence → pass context to LLM → return answer with sources and confidence.

## Mermaid Diagram (visual)

```mermaid
flowchart LR
  U[User / Browser] --> FE[Frontend UI\n(frontend/app.py)]
  FE --> API[/POST /api/ingest\nPOST /api/chat/GET /api/emails/health/]
  API --> Router[/app.api.routes\n(ingest / chat handlers)]
  
  subgraph IngestFlow [Ingest Flow]
    Router --> DOCX[DOCXEmailParser\n(parse docx)]
    DOCX --> DBAdd[DatabaseManager.add_email\n(store EmailDocument)]
    DBAdd --> DB[(SQLite)]
    DBAdd --> GetFull[email_full = db.get_email()]
    GetFull --> Chunker[`SemanticChunker.chunk()`\n(RecursiveCharacterTextSplitter)]
    Chunker --> ChunksData[chunk dicts\n(content + metadata)]
    ChunksData --> ChromaAdd[ChromaRetriever.add_chunks()]
    ChromaAdd --> Chroma[(Chroma DB\npersist_directory)]
    ChromaAdd --> BM25[BM25Okapi index]
  end
  
  subgraph QueryFlow [Query / Chat Flow]
    Router --> Retrieve[ChromaRetriever.retrieve(query)]
    Retrieve --> BM25Search[BM25 scores]
    Retrieve --> DenseSearch[Chroma dense query\n+ embeddings (SentenceTransformer)]
    BM25Search --> Ensemble[Ensemble (0.4 BM25,0.6 dense)]
    DenseSearch --> Ensemble
    Ensemble --> TopK[Top-K candidate chunks]
    TopK --> Filter[Filter by confidence threshold\n(settings.confidence_threshold)]
    Filter --> LLM[`OllamaLLMClient.generate()`\n(build prompt with context chunks)]
    LLM --> Answer[Answer returned to API]
    Answer --> Router --> FE
  end
  
  style IngestFlow fill:#f8f0e3,stroke:#f39c12
  style QueryFlow fill:#e8f6ff,stroke:#3498db
```

## Key files (where to look)

- `backend/app/main.py` — app startup, dependency wiring, include routes.
- `backend/app/api/routes.py` — API endpoints: `/ingest`, `/chat`, `/emails`, `/health`.
- `backend/app/ingestion/docx_parser.py` — DOCX parsing (used by ingest).
- `backend/app/ingestion/chunker.py` — semantic chunking using `RecursiveCharacterTextSplitter`.
- `backend/app/retrieval/chroma_retriever.py` — hybrid retriever (ChromaDB + BM25 + embeddings).
- `backend/app/core/llm.py` — `OllamaLLMClient` builds prompts and calls the local LLM.
- `backend/app/storage/database.py` — `DatabaseManager` (SQLAlchemy SQLite storage).

## Component responsibilities (concise)

- Frontend: collect user queries and DOCX upload path; display answers and sources.
- Ingest endpoint: parse, persist, chunk, embed, and persist chunks to Chroma and BM25.
- Chunker: produce deterministic chunk IDs and rich metadata for traceability.
- Retriever: keep a persistent Chroma collection, maintain an in-memory BM25 index, and return an ensemble-scored ranked list.
- Chat endpoint: filter retrieved chunks by `settings.confidence_threshold`, then call the LLM with the selected context.
- LLM client: strictly uses provided context and returns concise answers, relying on a local Ollama service.

## Route flow (step-by-step)

Ingest:
1. Frontend POST `/api/ingest` with `docx_path`.
2. `DOCXEmailParser.parse_from_path()` extracts fields (subject, sender, body, timestamp).
3. `DatabaseManager.add_email()` stores the email and returns `email_id`.
4. `SemanticChunker.chunk()` converts the email to markdown-like text and splits into chunks.
5. `ChromaRetriever.add_chunks()` generates embeddings, upserts into Chroma, and builds a BM25 index.

Chat:
1. Frontend POST `/api/chat` with `text`, `top_k`, `return_sources`.
2. `ChromaRetriever.retrieve()` runs BM25 and dense search, ensembles scores, and returns top candidates.
3. Backend filters by `settings.confidence_threshold` and builds `context_texts`.
4. `OllamaLLMClient.generate()` is called with the query and `context_texts` to produce the answer.
5. API returns `ChatResponse` with `answer`, `sources` (optional), `confidence`, and timing.

## Important runtime settings

- `settings.chroma_db_path` — where Chroma persists embeddings and metadata.
- `settings.confidence_threshold` — minimum confidence for chunks used as context.
- `settings.ollama_base_url` & `settings.ollama_model` — LLM endpoint and model name.

---

If you want the diagram exported as a PNG/SVG or want this file moved under `docs/`, tell me which format or path and I'll add it.
