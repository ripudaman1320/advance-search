# Email RAG Chatbot - Recruiter/One-Page Overview

## Project summary
The Email RAG Chatbot is a production-inspired Retrieval-Augmented Generation (RAG) application designed to answer questions from personal email history using grounded evidence. Instead of asking a large language model to rely on general knowledge, the system retrieves relevant email snippets and uses them as context before generating an answer.

## Problem it solves
Email communication is rich in operational context but usually fragmented, unstructured, and difficult to search efficiently. Organizations and individuals need a way to ask natural-language questions like:
- What were the open blockers in the project?
- Who mentioned the release timeline?
- Which past email discussed the QA issue?

A regular LLM alone is not reliable enough for this, because it may forget details or hallucinate. This project solves that by grounding the model in retrieved email evidence.

## Core architecture
- Frontend: Gradio-based UI for chat and email ingestion
- Backend: FastAPI service exposing chat and ingestion APIs
- Storage: SQLite for email metadata and source documents
- Search: ChromaDB for vector retrieval + BM25 for keyword retrieval
- Retrieval pipeline: query expansion, hybrid search, deduplication, reranking, confidence scoring
- LLM layer: Ollama for local LLM inference
- Safety layer: NLI hallucination detection, answer validation, and fallback logic

## End-to-end flow
1. Upload email DOCX files
2. Parse sender, subject, body, and timestamp
3. Save the document in SQLite
4. Split the content into semantic chunks
5. Embed and index chunks in ChromaDB
6. User asks a question
7. Expand the query and retrieve candidate chunks using BM25 + semantic search
8. Rerank and filter weak results using confidence scoring
9. Pass the strongest evidence to the LLM
10. Validate the answer and apply fallback if needed

## Why this is a good RAG design
This project uses the right production patterns:
- hybrid retrieval for higher recall
- reranking for better precision
- confidence thresholds to reduce noise
- grounded generation using only retrieved snippets
- safety checks to prevent unsupported answers

## Key technologies
- Python
- FastAPI
- Gradio
- SQLite
- ChromaDB
- SentenceTransformers
- BM25
- Ollama
- Cross-encoders for reranking and NLI

## What makes it production-minded
The project goes beyond a simple Q&A demo by adding:
- document-level metadata tracking
- chunk provenance for answer sourcing
- retrieval confidence scoring
- hallucination detection using NLI
- response validation and fallback handling
- evaluation metrics for retrieval quality

## Deployment strategy (AWS example)
For cloud deployment, I would use:
- ECS Fargate or EKS for the backend
- S3 for uploaded email documents
- ALB or CloudFront in front of the app
- RDS for metadata storage at scale
- OpenSearch / Pinecone / managed vector DB for retrieval
- Bedrock, SageMaker, or GPU-backed Ollama for LLM inference
- CloudWatch + Secrets Manager for observability and secrets

## Interview-ready summary
This project demonstrates a practical, end-to-end RAG architecture for enterprise-style document Q&A. It combines semantic search, retrieval optimization, and answer safety checks to improve both relevance and trustworthiness. The design balances local-first simplicity with production patterns that are relevant for real-world AI applications.

## One-sentence pitch
I built a grounded email question-answering system that retrieves relevant evidence from personal email history, summarizes it with an LLM, and includes safety checks so the answer stays supported by the source data.
