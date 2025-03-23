"""Service for generating embeddings and performing similarity search."""
import json
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union

import numpy as np
from loguru import logger
from sentence_transformers import SentenceTransformer
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.models.base import CatalogEntity, EmbeddingMixin
from src.utils.errors import EmbeddingError

T = TypeVar('T', bound=CatalogEntity)


class EmbeddingService:
    """Service for generating and managing embeddings for catalog entities."""
    
    _instance = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize embedding model."""
        if self._initialized:
            return
            
        try:
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info(f"Initialized embedding model: {settings.EMBEDDING_MODEL}")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise EmbeddingError(f"Failed to initialize embedding model: {e}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding vector for the given text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        try:
            # Generate embedding
            embedding = self.model.encode(text)
            
            # Convert to Python list for JSON serialization
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise EmbeddingError(f"Failed to generate embedding: {e}")
    
    def generate_entity_embedding(self, entity: Union[CatalogEntity, EmbeddingMixin]) -> List[float]:
        """
        Generate embedding for a catalog entity.
        
        Args:
            entity: Catalog entity instance
            
        Returns:
            Embedding vector
            
        Raises:
            EmbeddingError: If entity doesn't support embeddings or generation fails
        """
        if not isinstance(entity, EmbeddingMixin):
            raise EmbeddingError(f"Entity type doesn't support embeddings: {type(entity)}")
        
        try:
            # Get text representation for embedding
            text = entity.get_text_for_embedding()
            
            # Generate embedding
            return self.generate_embedding(text)
        except Exception as e:
            logger.error(f"Failed to generate entity embedding: {e}")
            raise EmbeddingError(f"Failed to generate entity embedding: {e}")
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0-1)
            
        Raises:
            EmbeddingError: If computation fails
        """
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Compute cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            similarity = dot_product / (norm1 * norm2)
            
            # Handle potential numerical issues
            similarity = min(1.0, max(-1.0, similarity))
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Failed to compute similarity: {e}")
            raise EmbeddingError(f"Failed to compute similarity: {e}")
    
    def find_similar_entities(
        self, 
        query_embedding: List[float],
        embeddings: List[Dict[str, Any]],
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find similar entities based on embedding similarity.
        
        Args:
            query_embedding: Query embedding vector
            embeddings: List of dictionaries containing id, name, and embedding
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of dictionaries with id, name, and similarity score
            
        Raises:
            EmbeddingError: If similarity search fails
        """
        try:
            results = []
            
            for item in embeddings:
                if "embedding" not in item or not item["embedding"]:
                    continue
                    
                similarity = self.compute_similarity(query_embedding, item["embedding"])
                
                if similarity >= threshold:
                    results.append({
                        "id": item["id"],
                        "name": item["name"],
                        "similarity": similarity
                    })
            
            # Sort by similarity (descending)
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Return top k results
            return results[:top_k]
        except Exception as e:
            logger.error(f"Failed to find similar entities: {e}")
            raise EmbeddingError(f"Failed to find similar entities: {e}")


# Global embedding service instance
embedding_service = EmbeddingService()