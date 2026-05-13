"""
Embedding Module - Generates embeddings for text using sentence-transformers
Uses all-MiniLM-L6-v2 for local deployment (cost-effective, good performance)
"""

import logging
from typing import List, Union
import numpy as np

logger = logging.getLogger(__name__)


class TextEmbedder:
    """Generate embeddings for text chunks using sentence-transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the text embedder
        
        Args:
            model_name: Name of the sentence-transformers model to use
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # all-MiniLM-L6-v2 produces 384-dimensional embeddings
        
    def load_model(self):
        """Load the embedding model"""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dim}")
            except ImportError:
                logger.error("sentence-transformers not installed. Run: pip install sentence-transformers")
                raise
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise
    
    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text(s)
        
        Args:
            texts: Single text string or list of text strings
        
        Returns:
            Numpy array of embeddings (2D if list input, 1D if single input)
        """
        if self.model is None:
            self.load_model()
        
        try:
            # Ensure texts is a list
            if isinstance(texts, str):
                texts = [texts]
                single_input = True
            else:
                single_input = False
            
            # Generate embeddings
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            
            logger.info(f"Generated {len(texts)} embeddings of dimension {embeddings.shape[1]}")
            
            # Return 1D array if single input, 2D if multiple
            if single_input:
                return embeddings[0]
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def embed_chunks(self, chunks: List[dict]) -> np.ndarray:
        """
        Generate embeddings for document chunks
        
        Args:
            chunks: List of chunk dictionaries with 'chunk_text' field
        
        Returns:
            Numpy array of embeddings
        """
        texts = [chunk.get("chunk_text", "") for chunk in chunks]
        return self.embed(texts)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings"""
        return self.embedding_dim
    
    def cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Cosine similarity score (0-1)
        """
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)


class OpenAIEmbedder:
    """Alternative embedder using OpenAI API (if sentence-transformers not available)"""
    
    def __init__(self, model_name: str = "text-embedding-3-small"):
        """
        Initialize OpenAI embedder
        
        Args:
            model_name: OpenAI embedding model name
        """
        self.model_name = model_name
        self.embedding_dim = 1536  # text-embedding-3-small dimension
        
    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings using OpenAI API
        
        Args:
            texts: Single text string or list of text strings
        
        Returns:
            Numpy array of embeddings
        """
        try:
            import openai
            
            # Ensure texts is a list
            if isinstance(texts, str):
                texts = [texts]
            
            logger.info(f"Generating embeddings using OpenAI API for {len(texts)} texts")
            
            response = openai.Embedding.create(
                model=self.model_name,
                input=texts
            )
            
            embeddings = np.array([item["embedding"] for item in response["data"]])
            
            return embeddings if len(embeddings) > 1 else embeddings[0]
            
        except ImportError:
            logger.error("openai not installed. Run: pip install openai")
            raise
        except Exception as e:
            logger.error(f"Failed to generate OpenAI embeddings: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings"""
        return self.embedding_dim


def get_embedder(embedder_type: str = "local", **kwargs) -> TextEmbedder:
    """
    Factory function to get appropriate embedder
    
    Args:
        embedder_type: 'local' for sentence-transformers, 'openai' for OpenAI API
        **kwargs: Additional arguments for embedder initialization
    
    Returns:
        Embedder instance
    """
    if embedder_type == "openai":
        return OpenAIEmbedder(**kwargs)
    else:
        return TextEmbedder(**kwargs)
