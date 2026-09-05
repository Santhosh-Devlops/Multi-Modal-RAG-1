import hashlib
import logging
from typing import List, Optional

import numpy as np

from config import EMBEDDING_MODEL, EMBEDDING_MODEL_FALLBACKS, USE_LOCAL_EMBEDDING_MODEL
from services import huggingface as hf_client

logger = logging.getLogger("embedding_service")

_local_model = None
_local_model_load_attempted = False


def _get_local_model():
    """Lazily load a local sentence-transformers model, if the package is
    installed. Never raises - returns None and logs once if it isn't
    installed or fails to load, so the rest of the app is unaffected."""
    global _local_model, _local_model_load_attempted
    if _local_model is not None or _local_model_load_attempted or not USE_LOCAL_EMBEDDING_MODEL:
        return _local_model
    _local_model_load_attempted = True
    try:
        from sentence_transformers import SentenceTransformer
        _local_model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Loaded local sentence-transformers model '%s' for embeddings.", EMBEDDING_MODEL)
    except ImportError:
        logger.info(
            "sentence-transformers not installed - embeddings will use the HF API "
            "(rate-limited/curated model list) or the local hash fallback instead. "
            "`pip install sentence-transformers` for reliable, network-free embeddings."
        )
    except Exception as e:
        logger.warning("Failed to load local embedding model '%s': %s", EMBEDDING_MODEL, e)
    return _local_model


class EmbeddingService:
    EMBEDDING_DIM = 384  # Standard MiniLM dimension

    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        """
        Generate a normalized dense embedding for a piece of text.

        Order of attempts:
        1. A local sentence-transformers model, if the package is installed
           (`pip install sentence-transformers`) - real semantic embedding,
           no network call, no rate limits, no "model not supported by
           provider" surprises. This is the recommended path.
        2. The Hugging Face feature-extraction API, trying EMBEDDING_MODEL
           then EMBEDDING_MODEL_FALLBACKS in turn (see huggingface.py) -
           used only if no local model is available.
        3. A deterministic local hashed bag-of-words projection as a last
           resort so retrieval never hard-fails. This gives keyword-level
           matching, not real semantic similarity.
        """
        if not text or not text.strip():
            return [0.0] * cls.EMBEDDING_DIM

        clean_input = text.strip()

        local_model = _get_local_model()
        if local_model is not None:
            try:
                vec = np.asarray(local_model.encode(clean_input), dtype=np.float32)
                return cls._normalize_and_resize(vec)
            except Exception as e:
                logger.warning("Local embedding inference failed, falling back: %s", e)

        remote_vec = hf_client.get_embedding(clean_input, [EMBEDDING_MODEL, *EMBEDDING_MODEL_FALLBACKS])
        if remote_vec:
            return cls._normalize_and_resize(np.array(remote_vec, dtype=np.float32))

        return cls._local_fallback_embedding(clean_input)

    @classmethod
    def _normalize_and_resize(cls, vec: np.ndarray) -> List[float]:
        if vec.shape[0] != cls.EMBEDDING_DIM:
            vec = cls._resize(vec, cls.EMBEDDING_DIM)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    @staticmethod
    def _resize(vec: np.ndarray, target_dim: int) -> np.ndarray:
        if vec.shape[0] == target_dim:
            return vec
        if vec.shape[0] > target_dim:
            return vec[:target_dim]
        return np.pad(vec, (0, target_dim - vec.shape[0]))

    @classmethod
    def _local_fallback_embedding(cls, clean_input: str) -> List[float]:
        """Deterministic offline fallback: hashed bag-of-words + character
        bigrams. Not a real semantic embedding, but keeps the app fully
        functional (keyword-level retrieval) with zero external dependency."""
        words = clean_input.lower().split()
        vector = np.zeros(cls.EMBEDDING_DIM, dtype=np.float32)

        for idx, word in enumerate(words):
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            pos1 = h % cls.EMBEDDING_DIM
            pos2 = (h >> 16) % cls.EMBEDDING_DIM
            pos3 = (h >> 32) % cls.EMBEDDING_DIM

            weight = 1.0 / (1.0 + 0.1 * idx)  # higher weight for front words/title
            vector[pos1] += weight
            vector[pos2] += weight * 0.5
            vector[pos3] -= weight * 0.3

            for i in range(len(word) - 1):
                bg = word[i:i + 2]
                bgh = int(hashlib.md5(bg.encode("utf-8")).hexdigest(), 16)
                bg_pos = bgh % cls.EMBEDDING_DIM
                vector[bg_pos] += 0.15

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        else:
            vector[0] = 1.0

        return vector.tolist()

    @classmethod
    def get_embeddings_batch(cls, texts: List[str]) -> List[List[float]]:
        """Batch embedding generation."""
        return [cls.get_embedding(t) for t in texts]
