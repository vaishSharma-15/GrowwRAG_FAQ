"""
Retriever Module - Retrieves relevant chunks from vector database
Implements no-answer handling: if no relevant information found, returns refusal WITHOUT any URL
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np

try:
    from src.embedder import TextEmbedder
    from src.vector_db import ChromaVectorDB
except ImportError:
    from embedder import TextEmbedder
    from vector_db import ChromaVectorDB

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Result of a retrieval operation"""
    chunks: List[Dict[str, Any]]
    query: str
    has_answer: bool
    refusal_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentRetriever:
    """Retrieves relevant documents from vector database with no-answer handling"""
    
    def __init__(
        self,
        vector_db: ChromaVectorDB,
        embedder: TextEmbedder,
        min_similarity: float = 0.1,
        top_k: int = 5
    ):
        """
        Initialize the document retriever
        
        Args:
            vector_db: Vector database instance
            embedder: Text embedder instance
            min_similarity: Minimum similarity threshold (0-1)
            top_k: Number of top results to retrieve
        """
        self.vector_db = vector_db
        self.embedder = embedder
        self.min_similarity = min_similarity
        self.top_k = top_k
        
        # Connect to vector database
        self.vector_db.connect()
        
        # Load embedder model
        self.embedder.load_model()
        
        logger.info(f"Retriever initialized with min_similarity={min_similarity}, top_k={top_k}")
    
    def retrieve(
        self,
        query: str,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> RetrievalResult:
        """
        Retrieve relevant chunks for a query
        
        IMPORTANT: If no relevant information is found (all chunks below threshold),
        the system will return a refusal WITHOUT attaching any URL.
        
        Args:
            query: User query text
            filter_metadata: Optional metadata filters (e.g., {"scheme_name": "Axis Flexi Cap Fund"})
        
        Returns:
            RetrievalResult with chunks or refusal message (NO URL attached if no answer)
        """
        logger.info(f"Retrieving for query: '{query}'")
        
        try:
            # Generate query embedding
            query_embedding = self.embedder.embed(query)
            
            # Search vector database
            results = self.vector_db.search(
                query_embedding=query_embedding,
                top_k=self.top_k,
                filter_metadata=filter_metadata,
                min_similarity=self.min_similarity
            )
            
            logger.info(f"Retrieved {len(results)} chunks above threshold {self.min_similarity}")
            
            # Check if any relevant chunks found
            if not results or len(results) == 0:
                # NO RELEVANT INFORMATION FOUND
                # IMPORTANT: Do NOT attach any URL when answer is not found
                return RetrievalResult(
                    chunks=[],
                    query=query,
                    has_answer=False,
                    refusal_message=self._generate_refusal_message(query),
                    metadata={
                        "retrieval_status": "no_relevant_chunks",
                        "min_similarity_threshold": self.min_similarity,
                        "note": "No URL attached - answer not found in corpus"
                    }
                )
            
            # Relevant chunks found - return them with metadata
            return RetrievalResult(
                chunks=results,
                query=query,
                has_answer=True,
                metadata={
                    "retrieval_status": "success",
                    "chunks_retrieved": len(results),
                    "top_similarity": results[0].get("similarity", 0) if results else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            
            # On error, return refusal without URL
            return RetrievalResult(
                chunks=[],
                query=query,
                has_answer=False,
                refusal_message="I apologize, but I'm unable to process your query at this time. Please try again later.",
                metadata={
                    "retrieval_status": "error",
                    "error": str(e),
                    "note": "No URL attached due to retrieval error"
                }
            )
    
    def retrieve_with_fallback(
        self,
        query: str,
        scheme_name: Optional[str] = None,
        category: Optional[str] = None
    ) -> RetrievalResult:
        """
        Retrieve with automatic fallback strategies
        
        1. First try with scheme-specific filter
        2. If no results, try without filters
        3. If still no results, return refusal WITHOUT URL
        
        Args:
            query: User query
            scheme_name: Optional scheme name filter
            category: Optional category filter
        
        Returns:
            RetrievalResult
        """
        # Build filter metadata
        filter_metadata = {}
        if scheme_name:
            filter_metadata["scheme_name"] = scheme_name
        if category:
            filter_metadata["category"] = category
        
        # Try with filters first
        if filter_metadata:
            result = self.retrieve(query, filter_metadata)
            if result.has_answer:
                return result
            
            logger.info("No results with filters, trying without filters...")
        
        # Try without filters
        result = self.retrieve(query, None)
        
        return result
    
    def _generate_refusal_message(self, query: str) -> str:
        """
        Generate refusal message when no relevant information is found
        
        Args:
            query: The original query
        
        Returns:
            Refusal message
        """
        return (
            "I can provide factual information about Axis mutual funds, including: • Scheme details (NAV, expense ratio, exit load) • Risk levels • Fund manager details. For general mutual fund education, please visit the official website of Groww\n\n"
            "https://groww.in\n\n"
            "For personalized investment advice or recommendations, please consult a SEBI-registered investment advisor."
        )
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the vector database collection"""
        return self.vector_db.get_collection_stats()
    
    def test_retrieval(self, test_queries: List[str]) -> List[Dict[str, Any]]:
        """
        Test retrieval with sample queries
        
        Args:
            test_queries: List of test queries
        
        Returns:
            List of test results
        """
        results = []
        
        for query in test_queries:
            result = self.retrieve(query)
            
            results.append({
                "query": query,
                "has_answer": result.has_answer,
                "chunks_retrieved": len(result.chunks),
                "refused": not result.has_answer
            })
            
            if result.has_answer:
                logger.info(f"✓ Query '{query}': Found {len(result.chunks)} chunks")
            else:
                logger.info(f"✗ Query '{query}': No relevant information found (refused)")
        
        return results


class RefusalHandler:
    """Handles cases where no answer can be provided"""
    
    @staticmethod
    def should_refuse(chunks: List[Dict[str, Any]], min_similarity: float = 0.6) -> bool:
        """
        Determine if we should refuse to answer based on retrieved chunks
        
        Args:
            chunks: Retrieved chunks
            min_similarity: Minimum similarity threshold
        
        Returns:
            True if should refuse, False otherwise
        """
        if not chunks:
            return True
        
        # Check if top chunk is below threshold
        top_similarity = chunks[0].get("similarity", 0)
        if top_similarity < min_similarity:
            return True
        
        return False
    
    @staticmethod
    def create_refusal_response(query: str, include_url: bool = True) -> Dict[str, Any]:
        """
        Create refusal response
        
        Args:
            query: Original query
            include_url: Whether to include a URL (default: True to provide an educational link per requirements)
        
        Returns:
            Refusal response dictionary
        """
        response = {
            "answer": (
                "I can provide factual information about Axis mutual funds, including: • Scheme details (NAV, expense ratio, exit load) • Risk levels • Fund manager details. For general mutual fund education, please visit the official website of Groww\n\n"
                "https://groww.in\n\n"
                "For personalized investment advice or recommendations, please consult a SEBI-registered investment advisor."
            ),
            "source": None,
            "source_url": None,
            "has_answer": False,
            "refusal_reason": "no_relevant_information"
        }
        
        if include_url:
            response["source"] = "https://groww.in"
            response["source_url"] = "https://groww.in"
        
        return response
