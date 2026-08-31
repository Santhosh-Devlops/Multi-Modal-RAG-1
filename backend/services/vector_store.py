import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import VECTOR_INDEX_DIR

class VectorStore:
    def __init__(self):
        self.index_dir = Path(VECTOR_INDEX_DIR)
        self.meta_file = self.index_dir / "vector_metadata.json"
        self.vec_file = self.index_dir / "vectors.npy"
        
        self.vectors: np.ndarray = np.empty((0, 384), dtype=np.float32)
        self.metadata: List[Dict[str, Any]] = []
        self.load()

    def add_item(self, vector: List[float], meta: Dict[str, Any]):
        """Add a single vector and its metadata into store."""
        vec_arr = np.array(vector, dtype=np.float32).reshape(1, -1)
        # Normalize
        norm = np.linalg.norm(vec_arr)
        if norm > 0:
            vec_arr = vec_arr / norm
            
        if self.vectors.shape[0] == 0:
            self.vectors = vec_arr
        else:
            self.vectors = np.vstack([self.vectors, vec_arr])
        self.metadata.append(meta)

    def add_batch(self, vectors: List[List[float]], metadata_list: List[Dict[str, Any]]):
        """Add multiple items in batch and persist to disk."""
        if not vectors:
            return
        vec_arr = np.array(vectors, dtype=np.float32)
        # Normalize rows
        norms = np.linalg.norm(vec_arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        vec_arr = vec_arr / norms
        
        if self.vectors.shape[0] == 0:
            self.vectors = vec_arr
        else:
            self.vectors = np.vstack([self.vectors, vec_arr])
        self.metadata.extend(metadata_list)
        self.save()

    def search(
        self, 
        query_vector: List[float], 
        top_k: int = 5, 
        domain_filter: Optional[str] = None,
        doc_id_filter: Optional[int] = None,
        user_id_filter: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform cosine similarity search with optional domain/doc/user filters.
        """
        if self.vectors.shape[0] == 0:
            return []
            
        q_vec = np.array(query_vector, dtype=np.float32).reshape(1, -1)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm
            
        # Cosine similarity matrix multiplication
        sims = np.dot(self.vectors, q_vec.T).flatten()
        
        # Apply filters (Strict User Privacy Isolation)
        candidate_indices = []
        for idx, meta in enumerate(self.metadata):
            # User privacy check
            chunk_user_id = meta.get("user_id")
            if user_id_filter is not None and chunk_user_id is not None and chunk_user_id != user_id_filter:
                continue
            if domain_filter and meta.get("domain", "").lower() != domain_filter.lower() and domain_filter.lower() != "all":
                continue
            if doc_id_filter is not None and meta.get("document_id") != doc_id_filter:
                continue
            candidate_indices.append((idx, float(sims[idx])))
            
        # Fallback: If strict domain filter yielded 0 results, search all documents authorized for this user
        if not candidate_indices and len(self.metadata) > 0:
            for idx, meta in enumerate(self.metadata):
                chunk_user_id = meta.get("user_id")
                if user_id_filter is not None and chunk_user_id is not None and chunk_user_id != user_id_filter:
                    continue
                if doc_id_filter is not None and meta.get("document_id") != doc_id_filter:
                    continue
                candidate_indices.append((idx, float(sims[idx])))
            
        # Sort by similarity score descending
        candidate_indices.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in candidate_indices[:top_k]:
            item = dict(self.metadata[idx])
            item["semantic_score"] = max(0.0, min(1.0, score))
            results.append(item)
            
        return results

    def delete_document(self, doc_id: int):
        """Remove all chunks associated with a specific document."""
        if self.vectors.shape[0] == 0:
            return
            
        keep_indices = [i for i, m in enumerate(self.metadata) if m.get("document_id") != doc_id]
        if len(keep_indices) == len(self.metadata):
            return
            
        if len(keep_indices) == 0:
            self.vectors = np.empty((0, 384), dtype=np.float32)
            self.metadata = []
        else:
            self.vectors = self.vectors[keep_indices]
            self.metadata = [self.metadata[i] for i in keep_indices]
        self.save()

    def clear(self):
        """Clear all stored vectors."""
        self.vectors = np.empty((0, 384), dtype=np.float32)
        self.metadata = []
        self.save()

    def save(self):
        """Persist vectors and metadata to disk."""
        np.save(str(self.vec_file), self.vectors)
        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def load(self):
        """Load persisted vector store from disk."""
        if self.vec_file.exists() and self.meta_file.exists():
            try:
                self.vectors = np.load(str(self.vec_file))
                with open(self.meta_file, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                print(f"Error loading vector store: {e}")
                self.vectors = np.empty((0, 384), dtype=np.float32)
                self.metadata = []

# Global vector store singleton
vector_store = VectorStore()
