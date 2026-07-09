from chromadb import Client
from chromadb.config import Settings as ChromaSettings
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from app.models.schemas import RetrievalResult

class ChromaRetriever:
    """Hybrid retrieval using ChromaDB + BM25 + Dense embeddings"""
    
    # def __init__(self, chroma_db_path: str, embedding_model: str = "all-MiniLM-L6-v2"):
    def __init__(self, chroma_db_path: str, embedding_model: str = "paraphrase-MiniLM-L6-v2"):
        # Initialize Chroma
        # self.client = chromadb.Client(
        #     ChromaSettings(
        #         chroma_db_impl="duckdb",
        #         persist_directory=chroma_db_path,
        #         anonymized_telemetry=False,
        #     )
        # )
        self.client = Client(
            settings=ChromaSettings(
                chroma_api_impl="chromadb.api.rust.RustBindingsAPI",
                persist_directory=chroma_db_path,
                is_persistent=True,
                anonymized_telemetry=False,
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="email_chunks",
            metadata={"hnsw:space": "cosine"}
        )

        # print('Chroma collection metadata ====================================>>>>>>>>>>>>>', self.collection.get()['metadatas'])

        # Load embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # BM25 components
        self.bm25_index = None
        self.chunk_ids = []
        self.chunk_contents = {}
        self._load_existing_chunks()
    
    def add_chunks(self, chunks: list[dict]):
        """Add chunks to Chroma and build BM25 index"""
        if not chunks:
            return
        
        # Extract data
        ids = [chunk['metadata']['source_doc_id'] + "_" + str(chunk['metadata']['chunk_index']) 
               for chunk in chunks]
        documents = [chunk['content'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents, convert_to_numpy=True).tolist()
        
        # Store in Chroma
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        # Build BM25 index
        tokenized_docs = [doc.lower().split() for doc in documents]
        self.bm25_index = BM25Okapi(tokenized_docs)
        self.chunk_ids = ids
        self.chunk_contents = {id_: doc for id_, doc in zip(ids, documents)}
        
        print(f"✓ Added {len(chunks)} chunks to Chroma")
    
    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """Hybrid retrieval: BM25 + Dense + Ensemble"""

        # print(f"Check chunk ids: {self.chunk_ids}")
        
        if not self.chunk_ids:
            return []
        
        # ===== BM25 Retrieval =====
        print(f"Performing BM25 retrieval for query: {query}")
        query_tokens = query.lower().split()
        bm25_scores = self.bm25_index.get_scores(query_tokens)
        
        # Normalize BM25 scores to [0, 1]
        bm25_scores_norm = (bm25_scores - bm25_scores.min()) / (bm25_scores.max() - bm25_scores.min() + 1e-6)
        
        bm25_results = {
            self.chunk_ids[i]: bm25_scores_norm[i]
            for i in np.argsort(-bm25_scores)[:top_k * 2]
        }
        
        # ===== Dense Retrieval via Chroma =====
        query_embedding = self.embedding_model.encode(query).tolist()
        dense_results_raw = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2
        )
        
        dense_results = {}
        if dense_results_raw['distances'] and len(dense_results_raw['distances'][0]) > 0:
            # Convert distance to similarity (distance is 1 - cosine similarity for cosine space)
            for id_, distance in zip(
                dense_results_raw['ids'][0],
                dense_results_raw['distances'][0]
            ):
                similarity = 1 - distance  # Convert distance back to similarity
                dense_results[id_] = max(0, similarity)  # Clamp to [0, 1]
        
        # ===== Ensemble: Combine scores =====
        combined_scores = {}
        for chunk_id in set(list(bm25_results.keys()) + list(dense_results.keys())):
            bm25_score = bm25_results.get(chunk_id, 0)
            dense_score = dense_results.get(chunk_id, 0)
            
            # Weighted combination: 40% BM25, 60% dense
            combined = 0.4 * bm25_score + 0.6 * dense_score
            combined_scores[chunk_id] = combined
        
        # Get top-k by combined score
        top_results = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        print(f"Top {len(top_results)} combined results: {[id for id, score in top_results]}")
        # Fetch full chunk data from Chroma
        results = []
        for chunk_id, score in top_results:
            # Query Chroma for metadata
            chunk_data = self.collection.get(ids=[chunk_id])
            
            if chunk_data['metadatas']:
                metadata = chunk_data['metadatas'][0]
                results.append(
                    RetrievalResult(
                        chunk_id=chunk_id,
                        content=chunk_data['documents'][0],
                        score=float(score),
                        confidence=min(float(score), 1.0),
                        source_doc_id=metadata.get('source_doc_id', ''),
                        sender=metadata.get('sender', ''),
                        timestamp=metadata.get('timestamp', ''),
                    )
                )
        
        return results
    
    def _load_existing_chunks(self):
        """Populate BM25 state and chunk_ids from existing persisted Chroma data."""
        try:
            result = self.collection.get(include=["documents", "metadatas"])
            ids = result.get("ids", []) or []
            documents = result.get("documents", []) or []

            if not ids:
                print("No existing chunks found in Chroma collection.")
                return

            self.chunk_ids = list(ids)
            self.chunk_contents = {
                chunk_id: doc for chunk_id, doc in zip(ids, documents)
            }

            tokenized_docs = [
                doc.lower().split() if isinstance(doc, str) else []
                for doc in documents
            ]
            self.bm25_index = BM25Okapi(tokenized_docs)

            print(f"✓ Loaded {len(ids)} existing chunks from Chroma")
        except Exception as exc:
            print(f"Could not load existing chunks from Chroma: {exc}")
    
    def delete_collection(self):
        """Delete collection (for testing)"""
        self.client.delete_collection(name="email_chunks")
        self.bm25_index = None
        self.chunk_ids = []
        self.chunk_contents = {}