# services/embeddings.py
import logging
import numpy as np
from typing import List, Union
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating and comparing text embeddings"""
    
    def __init__(self):
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Sentence transformer model loaded")
        except ImportError:
            logger.warning("⚠️  Sentence transformers not available, using mock embeddings")
            self.model = None
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            self.model = None
    
    async def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        try:
            if self.model:
                # Real embedding generation
                embedding = self.model.encode([text])[0]
                return embedding
            else:
                # Mock embedding for testing
                return self._generate_mock_embedding(text)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return self._generate_mock_embedding(text)
    
    def _generate_mock_embedding(self, text: str) -> np.ndarray:
        """Generate mock embedding based on text content"""
        # Simple hash-based mock embedding
        text_hash = hash(text.lower())
        np.random.seed(abs(text_hash) % (2**31))
        return np.random.rand(384)  # MiniLM dimension
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.5  # Default similarity