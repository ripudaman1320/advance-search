# Email RAG Chatbot Architecture

## Purpose

This repository implements a local-first email question-answering system. It ingests email documents, splits them into semantic chunks, stores them in a vector database, retrieves the most relevant chunks for a user query, reranks them, scores their confidence, and passes the best evidence to an LLM for answer generation.

The application is organized as a small pipeline with four main concerns:

1. Interface layer
2. API orchestration layer
3. Retrieval and ranking layer
4. Storage and persistence layer

Phase 2 enhances the query pipeline by adding query expansion, cross-encoder reranking, and confidence-based evidence filtering before the LLM is called.

---

## Mental Model

Think of the system as a pipeline:

- Ingestion path: email file -> parsed email -> stored in SQLite -> chunked -> indexed in Chroma
- Query path: question -> expanded/retrieved chunks -> reranked -> confidence-scored -> LLM answer
- Supporting services: configuration, embeddings, and LLM access

A helpful way to remember it is:

- SQLite = “source of truth” for email documents
- Chroma = “search index” for chunk retrieval
- Ollama = “reasoning engine” for answer generation
- FastAPI = “API glue” between user and backend logic
- Gradio = “simple UI shell” for interacting with the system

---

## Top-Level Components

### 1. Interface Layer
- [frontend/app.py](frontend/app.py)
- Provides a Gradio-based chat UI
- Lets users:
  - ask questions
  - upload DOCX emails
  - view ingested emails

### 2. API Layer
- [backend/app/main.py](backend/app/main.py)
- [backend/app/api/routes.py](backend/app/api/routes.py)
- Exposes HTTP endpoints for:
  - health checks
  - chat requests
  - ingestion
  - listing emails

### 3. Application Services
- [backend/app/config.py](backend/app/config.py)
- [backend/app/storage/database.py](backend/app/storage/database.py)
- [backend/app/core/llm.py](backend/app/core/llm.py)

These hold runtime configuration, database access, and LLM integration.

### 4. Ingestion Layer
- [backend/app/ingestion/docx_parser.py](backend/app/ingestion/docx_parser.py)
- [backend/app/ingestion/chunker.py](backend/app/ingestion/chunker.py)

These parse email DOCX files and split them into chunks.

### 5. Retrieval Layer
- [backend/app/retrieval/chroma_retriever.py](backend/app/retrieval/chroma_retriever.py)
- [backend/app/retrieval/advanced_retriever.py](backend/app/retrieval/advanced_retriever.py)
- [backend/app/retrieval/reranker.py](backend/app/retrieval/reranker.py)
- [backend/app/retrieval/confidence_scorer.py](backend/app/retrieval/confidence_scorer.py)
- [backend/app/retrieval/query_expander.py](backend/app/retrieval/query_expander.py)
- [backend/app/retrieval/pipeline_v2.py](backend/app/retrieval/pipeline_v2.py)

These perform hybrid retrieval, query expansion, duplicate merging, reranking, and confidence scoring.

### 6. Data Models
- [backend/app/models/schemas.py](backend/app/models/schemas.py)

Defines the core Pydantic models for:
- emails
- chunks
- retrieval results
- chat requests/responses

---

## End-to-End Workflow

### A. Ingestion Flow

1. User uploads a DOCX email through the Gradio UI.
2. The frontend calls the FastAPI ingestion endpoint.
3. The API route uses the DOCX parser to extract:
   - sender
   - subject
   - body
   - timestamp
4. The parsed email is saved into SQLite via the database manager.
5. The email is converted into a semantic chunk list.
6. Chunks are indexed into Chroma for later retrieval.

In short:

User Upload -> DOCX Parser -> SQLite Storage -> Semantic Chunking -> Chroma Indexing

### B. Query Flow

1. User asks a question using the chat UI.
2. The frontend sends the request to the API `/chat` endpoint.
3. The API calls the `AdvancedRetriever`.
4. The retriever pipeline:
   - expands the query into variants with `QueryExpander`
   - performs hybrid search over BM25 and Chroma dense retrieval
   - deduplicates duplicate chunks from multiple query variants
   - reranks candidates with `CrossEncoderReranker`
   - computes a confidence score for each result using `ConfidenceScorer`
   - filters out low-confidence chunks before passing context to the LLM
5. The best chunks are passed to the LLM.
6. The LLM generates a grounded answer based only on the provided context.
7. The API returns:
   - generated answer
   - source chunks
   - confidence
   - timing info

In short:

Question -> Expand -> Hybrid Retrieval -> Dedup -> Rerank -> Score -> Filter -> LLM -> Response

---

## Main Runtime Lifecycle

### Startup
When the backend starts:

- [backend/app/main.py](backend/app/main.py) creates the FastAPI app
- It initializes:
  - the SQLite database
  - the `AdvancedRetriever` pipeline (including query expansion, hybrid retrieval, reranking, and confidence scoring)
  - the Ollama client
- It links those services into the router layer

### Request Handling
The API layer routes requests to the correct service:

- `/health` -> check service health
- `/chat` -> retrieve context, call LLM, return answer
- `/ingest` -> parse and index email
- `/emails` -> list stored emails

---

## Core Data Flow Diagram

```mermaid
flowchart TD
    U[User] --> UI[Gradio UI]
    UI --> API[FastAPI API]

    API --> DB[(SQLite Database)]
    API --> CH[Chroma Vector Store]
    API --> LLM[Ollama LLM]

    subgraph Ingestion
        DOCX[DOCX Email File]
        PARSE[DOCX Parser]
        CHUNK[Semantic Chunker]
        STORE[SQLite]
        INDEX[Chroma Index]
        DOCX --> PARSE --> CHUNK --> STORE
        CHUNK --> INDEX
    end

    subgraph Retrieval
        QUERY[User Query]
        EXPAND[Query Expansion]
        SEARCH[Hybrid Retrieval]
        RERANK[Reranker]
        SCORE[Confidence Scorer]
        QUERY --> EXPAND --> SEARCH --> RERANK --> SCORE
    end

    API --> QUERY
    SCORE --> LLM
    LLM --> API
    API --> UI
    STORE --> CHUNK
    INDEX --> SEARCH