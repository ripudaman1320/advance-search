# Email RAG Chatbot — Phase 2 Summary

This document captures the key changes introduced in Phase 2, compared to the Phase 1 baseline.
It keeps the same email ingest architecture, but upgrades query retrieval and quality control.

## Phase 2 Purpose

Phase 2 improves answer relevance and trust by adding a more advanced retrieval pipeline before the LLM is called.
The goal is to reduce noisy context, broaden recall, and return only high-confidence evidence.

## What changed from Phase 1

- **Advanced retrieval layer**: Phase 1 used `ChromaRetriever` directly. Phase 2 now uses `AdvancedRetriever` as the main search engine.
- **Query expansion**: user queries are automatically expanded into variations using `QueryExpander` to improve recall.
- **Hybrid retrieval remains**: Chroma dense search + BM25 still run together, but now across expanded query variants.
- **Result deduplication**: duplicate chunks from multiple query variations are merged before reranking.
- **Reranking**: `CrossEncoderReranker` re-scores retrieved chunks with a cross-encoder model for better relevance ordering.
- **Confidence scoring**: `ConfidenceScorer` computes a multi-factor confidence score using freshness, retrieval quality, source overlap, and consistency.
- **Threshold filtering**: results are filtered by `settings.confidence_threshold`, so only higher-confidence chunks reach the LLM.
- **Evaluation harness**: `backend/app/evaluation/evaluation_report.py` explicitly compares Phase 1 and Phase 2 performance.

## Phase 2 architecture highlights

- `backend/app/main.py`
  - switches backend startup from `ChromaRetriever` to `AdvancedRetriever`
  - enables reranking and query expansion by default

- `backend/app/api/routes.py`
  - chat endpoint now uses the advanced retriever
  - ingest endpoint still parses DOCX, stores email, chunks content, and adds chunks to the retriever

- `backend/app/retrieval/advanced_retriever.py`
  - orchestrates query expansion, hybrid search, deduplication, reranking, confidence scoring, and top-k selection

- `backend/app/retrieval/query_expander.py`
  - generates query variations to improve search recall across email chunks

- `backend/app/retrieval/reranker.py`
  - ranks candidate chunks with a cross-encoder model instead of relying solely on initial retrieval scores

- `backend/app/retrieval/confidence_scorer.py`
  - combines retrieval score, freshness, overlap, and consistency into a single confidence value

- `backend/app/retrieval/pipeline_v2.py`
  - helper logic for reranking and scoring in a reusable pipeline format

## Why Phase 2 matters

Phase 2 keeps the ingest pipeline and storage unchanged, but makes the query path smarter:

- broader query coverage via expansion
- more accurate result ordering via reranking
- better evidence selection via confidence scoring

This means the LLM receives cleaner, more relevant context, which should improve answer quality and reduce hallucinations.

## New Phase 2 workflow

```mermaid
flowchart LR
  U[User / Browser] --> FE[Frontend UI]
  FE --> API[/POST /api/chat/]
  API --> AdvRet[AdvancedRetriever]

  subgraph RetrievalFlow [Phase 2 Query Flow]
    AdvRet --> Expand[QueryExpander
    (expand query variants)]
    Expand --> Hybrid[Hybrid Search
    (BM25 + Chroma dense)]
    Hybrid --> Dedup[Deduplicate chunks]
    Dedup --> Rerank[Cross-Encoder Rerank]
    Rerank --> Score[Confidence Scoring]
    Score --> Filter[Filter by threshold]
    Filter --> LLM[`OllamaLLMClient.generate()`]
  end

  LLM --> API
  API --> FE

  style RetrievalFlow fill:#e8f6ff,stroke:#3498db
  style Expand fill:#f9f9c4
  style Hybrid fill:#f9f9c4
  style Dedup fill:#f9f9c4
  style Rerank fill:#f9f9c4
  style Score fill:#f9f9c4
  style Filter fill:#f9f9c4
```

## Phase 2 workflow (text view)

User / Browser -> Frontend UI -> API chat endpoint -> AdvancedRetriever

AdvancedRetriever steps:
- QueryExpander: create query variants
- Hybrid Search: BM25 + Chroma dense retrieval
- Deduplicate: merge duplicate chunks
- Cross-Encoder Rerank: reorder by relevance
- Confidence Scoring: assign scores to results
- Threshold Filter: keep high-confidence context
- Ollama LLM: generate the final answer

API returns answer back to the Frontend.
