from typing import List
import numpy as np
import google.generativeai as genai
from app.utils.logger import logger
from app.services.gemini_service import gemini_api_key_var, GEMINI_CONFIGURED, _api_key, _gemini_lock

def get_embeddings(texts: List[str]) -> np.ndarray:
    """
    Generate embeddings for a list of text chunks using Google Gemini API.
    If the API key is not set, falls back to deterministic mock vectors.
    """
    custom_key = gemini_api_key_var.get()
    api_key = custom_key if custom_key else (_api_key if GEMINI_CONFIGURED else None)
    
    if api_key:
        try:
            with _gemini_lock:
                genai.configure(api_key=api_key)
                response = genai.embed_content(
                    model="models/text-embedding-004",
                    content=texts,
                    task_type="retrieval_document"
                )
                embeddings = response.get("embedding", [])
                if embeddings:
                    return np.array(embeddings, dtype=np.float32)
        except Exception as e:
            logger.error(f"Gemini embedding generation failed: {e}")
            
    # Deterministic fallback to avoid sentence-transformers dependency (OOM issues on Render)
    dim = 768
    logger.warning("Using fallback deterministic mock embeddings.")
    res = []
    for text in texts:
        # Generate deterministic seed from text
        char_sum = sum(ord(c) for c in text)
        rng = np.random.default_rng(char_sum % (2**32))
        vector = rng.standard_normal(dim)
        # Normalize vector to unit length (so Inner Product acts like cosine similarity)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        res.append(vector)
    return np.array(res, dtype=np.float32)


def get_single_embedding(text: str) -> np.ndarray:
    """Generate embedding for a single text string."""
    return get_embeddings([text])[0]
