import os
import pickle
import numpy as np
from typing import List, Tuple
from app.services.embedding_service import get_embeddings, get_single_embedding
from app.utils.helper import chunk_text
from app.utils.constants import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS
from app.utils.logger import logger
from app.config import settings

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS not available. RAG search will be disabled.")


def _get_index_path(resume_id: int) -> str:
    return os.path.join(settings.vector_db_path, f"resume_{resume_id}.index")


def _get_chunks_path(resume_id: int) -> str:
    return os.path.join(settings.vector_db_path, f"resume_{resume_id}_chunks.pkl")


def build_resume_index(resume_id: int, resume_text: str) -> bool:
    """
    Chunk resume text, generate embeddings, and store a FAISS index.

    Args:
        resume_id: Database ID of the resume (used as index filename).
        resume_text: Full text of the resume.

    Returns:
        True if successful, False otherwise.
    """
    if not FAISS_AVAILABLE:
        logger.warning("FAISS unavailable — skipping index build.")
        return False

    try:
        chunks = chunk_text(resume_text, CHUNK_SIZE, CHUNK_OVERLAP)
        if not chunks:
            logger.warning(f"No chunks generated for resume {resume_id}.")
            return False

        embeddings = get_embeddings(chunks)
        dim = embeddings.shape[1]

        index = faiss.IndexFlatIP(dim)  # Inner product (works with normalized embeddings)
        index.add(embeddings.astype(np.float32))

        faiss.write_index(index, _get_index_path(resume_id))
        with open(_get_chunks_path(resume_id), "wb") as f:
            pickle.dump(chunks, f)

        logger.info(f"Built FAISS index for resume {resume_id} with {len(chunks)} chunks.")
        return True

    except Exception as e:
        logger.error(f"Failed to build FAISS index for resume {resume_id}: {e}")
        return False


def search_resume_index(resume_id: int, query: str, top_k: int = TOP_K_RESULTS) -> List[str]:
    """
    Search the FAISS index for chunks most relevant to the query.

    Args:
        resume_id: ID of the resume whose index to search.
        query: User's natural language question.
        top_k: Number of top chunks to retrieve.

    Returns:
        List of relevant text chunks.
    """
    if not FAISS_AVAILABLE:
        return []

    index_path = _get_index_path(resume_id)
    chunks_path = _get_chunks_path(resume_id)

    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        logger.warning(f"No FAISS index found for resume {resume_id}.")
        return []

    try:
        index = faiss.read_index(index_path)
        with open(chunks_path, "rb") as f:
            chunks: List[str] = pickle.load(f)

        query_embedding = get_single_embedding(query).reshape(1, -1).astype(np.float32)
        distances, indices = index.search(query_embedding, min(top_k, len(chunks)))

        results = [chunks[i] for i in indices[0] if i < len(chunks)]
        logger.debug(f"RAG search returned {len(results)} chunks for resume {resume_id}.")
        return results

    except Exception as e:
        logger.error(f"FAISS search failed for resume {resume_id}: {e}")
        return []


def delete_resume_index(resume_id: int) -> None:
    """Remove stored FAISS index and chunks for a deleted resume."""
    for path in [_get_index_path(resume_id), _get_chunks_path(resume_id)]:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"Deleted index file: {path}")
