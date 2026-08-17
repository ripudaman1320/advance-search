# Email RAG Chatbot - Executive Summary

## Overview
This project is a production-inspired Retrieval-Augmented Generation (RAG) application for answering questions over personal email data. It ingests email documents, stores their metadata, splits them into searchable chunks, retrieves the most relevant chunks for a question, and sends only that evidence to a local LLM for answer generation.

## Why this project exists
Emails are large, unstructured, and often contain critical business information that general-purpose LLMs do not inherently know. This system grounds the model in the user’s own email history so responses are accurate, contextual, and traceable to source material.

## Architecture at a glance
- Frontend UI using Gradio
- FastAPI backend exposing chat and ingestion APIs
- SQLite for email metadata and document storage
- ChromaDB for vector storage and semantic retrieval
- BM25 for keyword-based retrieval
- Cross-encoder reranker for better relevance ordering
- Confidence scoring to filter weak evidence
- Ollama LLM for grounded answer generation
- Hallucination detection and fallback handling for safer responses

## Main workflow
1. Upload DOCX emails
2. Parse sender, subject, body, and timestamp
3. Save the email into SQLite
4. Split the content into semantic chunks
5. Embed and store chunks in ChromaDB
6. On a user question, expand the query and run hybrid search
7. Deduplicate and rerank the retrieved chunks
8. Score the evidence by confidence
9. Pass only high-confidence context to the LLM
10. Validate the answer and return a safe fallback if needed

## Key technical strengths
- Hybrid retrieval improves both exact-match and semantic recall
- Reranking increases relevance before generation
- Confidence filtering keeps only strong evidence
- NLI-based hallucination detection helps catch contradictions
- Fallback logic protects the app from low-quality answers

## Data flow summary
- Ingest flow: DOCX email → parse → SQLite → chunk → ChromaDB
- Query flow: question → expansion → BM25 + dense retrieval → dedupe → rerank → confidence filter → LLM → validation/fallback

## Deployment direction
For AWS, the recommended approach is:
- ECS Fargate or EKS for the FastAPI backend
- S3 for uploaded email files
- ALB or CloudFront in front of the API/frontend
- RDS for metadata storage at scale
- OpenSearch/Pinecone/managed vector DB for retrieval
- Bedrock/SageMaker or GPU-hosted Ollama for LLM inference
- CloudWatch + Secrets Manager for operations and security

## Risk and mitigation
The main risk in RAG systems is hallucination and low-quality context. This project mitigates that through query expansion, hybrid retrieval, reranking, confidence thresholds, NLI contradiction detection, and response validation.

## Bottom line
This is a strong local-first RAG architecture prototype with the right production instincts: grounded retrieval, evidence filtering, and safety checks. It is a practical foundation for a larger email intelligence or enterprise knowledge assistant.
