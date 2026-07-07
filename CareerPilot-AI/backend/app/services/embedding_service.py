from typing import List
import numpy as np
from app.utils.logger import logger

try:
    from sentence_transformers import SentenceTransformer
    _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    EMBEDDINGS_AVAILABLE = True
    logger.info("SentenceTransformer loaded: all-MiniLM-L6-v2")
except Exception as e:
    EMBEDDINGS_AVAILABLE = False
    _embed_model = None
    logger.warning(f"SentenceTransformer not available: {e}. Falling back to TF-IDF.")


def get_embeddings(texts: List[str]) -> np.ndarray:
    """
    Generate embeddings for a list of text chunks.

    Args:
        texts: List of text strings to embed.

    Returns:
        numpy array of shape (len(texts), embedding_dim).
    """
    if not EMBEDDINGS_AVAILABLE or _embed_model is None:
        raise RuntimeError("Embedding model is not available. Install sentence-transformers.")

    try:
        embeddings = _embed_model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        logger.debug(f"Generated embeddings for {len(texts)} chunks.")
        return embeddings
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise RuntimeError(f"Failed to generate embeddings: {e}")


def get_single_embedding(text: str) -> np.ndarray:
    """Generate embedding for a single text string."""
    return get_embeddings([text])[0]
