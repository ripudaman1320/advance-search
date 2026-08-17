# Email RAG Chatbot - Interview Answer Sheet

## 1. Explain this project end-to-end
This project is an email-based RAG system. It ingests DOCX email files, parses metadata, stores the email in SQLite, breaks it into chunks, embeds the chunks, and indexes them in ChromaDB. When a user asks a question, the system expands the query, retrieves relevant chunks using BM25 + vector search, reranks them, filters weak evidence, and sends the best context to a local LLM. Then it validates the answer and returns a safe fallback if the answer is unsupported or contradictory.

## 2. What are the data flows?
There are two main flows:
- Ingestion flow: email upload → parse → SQLite store → chunking → embeddings → ChromaDB
- Query flow: question → expansion → hybrid retrieval → dedup → rerank → confidence filter → LLM generation → validation → final response

## 3. What is advanced retrieval doing? Explain in detail with example
Advanced retrieval makes the system more accurate and reliable. It expands the user query into alternate variants, retrieves candidates using both lexical and semantic methods, removes duplicates, reranks results with a cross-encoder, and filters by confidence. Example: if a user asks, “What are the project blockers?”, the system may expand the query to include terms like “issues”, “pending”, and “open problems”, then identify the email chunks discussing blocked frontend work or unresolved QA issues before generating an answer.

## 4. What are the evaluations used and their purpose of usage? Does it reduce hallucination?
The project uses retrieval metrics such as MRR and precision@k, and it includes RAGAS-style evaluation hooks. These metrics help assess whether the retriever is finding the right evidence. They improve the system indirectly by helping fine-tune retrieval quality. However, direct hallucination reduction comes mainly from NLI contradiction detection, answer validation, and fallback logic.

## 5. What are the fallback mechanisms used?
Fallbacks are triggered when:
- no strong retrieval results are found
- retrieval confidence is low
- the generated answer contradicts the email context
- the answer has low coverage or weak support
In such cases, the app responds with a safe message instead of returning an unsupported answer.

## 6. If you need to deploy this to a cloud provider like AWS, what strategy would you use?
I would run the FastAPI backend on ECS Fargate or EKS, host the frontend on S3 + CloudFront or Amplify, store uploaded files on S3, keep metadata in RDS, and use a managed vector database or OpenSearch for retrieval. For the LLM, I’d either use Bedrock/SageMaker or a GPU-backed Ollama setup. Monitoring would be via CloudWatch and secrets via Secrets Manager.

## 7. What is NLI used in this project and its purpose? Why did you use it?
NLI stands for Natural Language Inference. It evaluates whether the generated answer is entailed by or contradicts the retrieved context. In this project, it helps detect hallucinations by comparing the answer against the email evidence. It was used because LLMs often sound confident even when unsupported, and NLI provides a practical safety layer.

## 8. Can you describe a challenge faced in this project? How did you solve it?
The main challenge was noisy, weak, or vaguely related retrieval results. Too many irrelevant chunks can mislead the LLM. The solution was a layered retrieval pipeline: query expansion, hybrid BM25 + vector search, deduplication, reranking, confidence filtering, and answer validation. This improved both retrieval quality and answer trustworthiness.

## 9. Describe some pros and cons of this design
Pros:
- Strong retrieval quality through hybrid search and reranking
- Better answer grounding from email evidence
- Local-first design is privacy-friendly
- Guardrails reduce hallucination risk
- Easy to understand and extend

Cons:
- Local deployment can be limiting at scale
- Retrieval and reranking models can be computationally heavy
- Some validation logic is heuristic rather than fully semantic
- The architecture is still a prototype compared with large production SaaS systems

## 10. Why is this a good RAG design?
Because it follows the key production pattern: retrieve only relevant context, constrain the LLM to that context, validate the answer, and block unsafe output when evidence is weak. That is the essential foundation of a trustworthy RAG system.
