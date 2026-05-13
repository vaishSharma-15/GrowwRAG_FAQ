"""
Vector Database Module - ChromaDB implementation for storing and retrieving embeddings
Supports metadata filtering and similarity search
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class ChromaVectorDB:
    """ChromaDB-based vector database for storing and retrieving document chunks"""
    
    def __init__(self, persist_directory: str = "data/vector_db/chroma_db", collection_name: str = "mutual_fund_chunks"):
        """
        Initialize ChromaDB vector database
        
        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection to use
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        
        self.client = None
        self.collection = None
        
    def connect(self):
        """Connect to ChromaDB and initialize collection"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            logger.info(f"Connecting to ChromaDB at {self.persist_directory}")
            
            # Create client with persistence
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Mutual Fund FAQ Assistant - Document Chunks",
                    "hnsw:space": "cosine"
                }
            )
            
            logger.info(f"Connected to collection: {self.collection_name}")
            
        except ImportError:
            logger.error("chromadb not installed. Run: pip install chromadb")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise
    
    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: Optional[np.ndarray] = None
    ):
        """
        Add document chunks with embeddings to the database
        
        Args:
            chunks: List of chunk dictionaries
            embeddings: Optional pre-computed embeddings (if None, text will be embedded)
        """
        if self.collection is None:
            self.connect()
        
        if not chunks:
            logger.warning("No chunks to add")
            return
        
        try:
            # Prepare data for ChromaDB
            ids = []
            documents = []
            metadatas = []
            
            for chunk in chunks:
                chunk_id = chunk.get("chunk_id")
                if not chunk_id:
                    logger.warning(f"Skipping chunk without ID: {chunk}")
                    continue
                
                ids.append(chunk_id)
                documents.append(chunk.get("chunk_text", ""))
                
                # Prepare metadata
                metadata = chunk.get("metadata", {})
                metadata["chunk_type"] = chunk.get("chunk_type", "general")
                metadata["chunk_index"] = chunk.get("chunk_index", 0)
                metadatas.append(metadata)
            
            # Add to collection
            if embeddings is not None:
                # Convert embeddings to list format for ChromaDB
                embeddings_list = embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings
                
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=embeddings_list
                )
            else:
                # ChromaDB will generate embeddings using its default embedder
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
            
            logger.info(f"Added {len(ids)} chunks to vector database")
            
        except Exception as e:
            logger.error(f"Failed to add chunks: {e}")
            raise
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_similarity: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using query embedding
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            min_similarity: Minimum similarity threshold (0-1)
        
        Returns:
            List of search results with metadata and similarity scores
        """
        if self.collection is None:
            self.connect()
        
        try:
            # Convert embedding to list
            query_embedding_list = query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding
            
            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding_list],
                n_results=top_k,
                where=filter_metadata,
                include=["documents", "metadatas", "distances", "embeddings"]
            )
            
            # Format results
            formatted_results = []
            
            if results and results["ids"]:
                for i in range(len(results["ids"][0])):
                    # ChromaDB returns cosine distance (1 - cosine similarity)
                    distance = results["distances"][0][i]
                    similarity = 1 - distance
                    
                    # Only include results above threshold
                    if similarity >= min_similarity:
                        formatted_results.append({
                            "chunk_id": results["ids"][0][i],
                            "text": results["documents"][0][i] if results["documents"] else "",
                            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                            "similarity": similarity,
                            "distance": distance
                        })
            
            logger.info(f"Search returned {len(formatted_results)} results above threshold {min_similarity}")
            return formatted_results
            
        except Exception as e:
            error_str = str(e)
            if "does not exist" in error_str and "Collection" in error_str:
                logger.warning(f"Collection reference stale, reconnecting... ({error_str})")
                try:
                    self.connect()
                    # Retry once
                    results = self.collection.query(
                        query_embeddings=[query_embedding_list],
                        n_results=top_k,
                        where=filter_metadata,
                        include=["documents", "metadatas", "distances", "embeddings"]
                    )
                    
                    formatted_results = []
                    if results and results["ids"]:
                        for i in range(len(results["ids"][0])):
                            distance = results["distances"][0][i]
                            similarity = 1 - distance
                            if similarity >= min_similarity:
                                formatted_results.append({
                                    "chunk_id": results["ids"][0][i],
                                    "text": results["documents"][0][i] if results["documents"] else "",
                                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                                    "similarity": similarity,
                                    "distance": distance
                                })
                    logger.info(f"Retry search returned {len(formatted_results)} results")
                    return formatted_results
                except Exception as retry_e:
                    logger.error(f"Search retry failed: {retry_e}")
                    raise retry_e
            else:
                logger.error(f"Search failed: {e}")
                raise
    
    def search_by_text(
        self,
        query_text: str,
        embedder,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_similarity: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search using text query (automatically embeds the query)
        
        Args:
            query_text: Text query
            embedder: Embedder instance to generate query embedding
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of search results
        """
        # Generate query embedding
        query_embedding = embedder.embed(query_text)
        
        # Perform search
        return self.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata,
            min_similarity=min_similarity
        )
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        if self.collection is None:
            self.connect()
        
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "persist_directory": str(self.persist_directory)
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}
    
    def reset_collection(self):
        """Reset/delete the collection"""
        if self.client is None:
            self.connect()
        
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
            
            # Recreate collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Mutual Fund FAQ Assistant - Document Chunks",
                    "hnsw:space": "cosine"
                }
            )
            logger.info(f"Recreated collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            raise
    
    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Get all chunks from the collection"""
        if self.collection is None:
            self.connect()
        
        try:
            results = self.collection.get(
                include=["documents", "metadatas"]
            )
            
            chunks = []
            if results and results["ids"]:
                for i in range(len(results["ids"])):
                    chunks.append({
                        "chunk_id": results["ids"][i],
                        "text": results["documents"][i] if results["documents"] else "",
                        "metadata": results["metadatas"][i] if results["metadatas"] else {}
                    })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to get all chunks: {e}")
            return []


def get_vector_db(db_type: str = "chromadb", **kwargs) -> ChromaVectorDB:
    """
    Factory function to get vector database instance
    
    Args:
        db_type: Type of vector database ('chromadb' only for now)
        **kwargs: Additional arguments for database initialization
    
    Returns:
        Vector database instance
    """
    if db_type == "chromadb":
        return ChromaVectorDB(**kwargs)
    else:
        raise ValueError(f"Unsupported vector database type: {db_type}")
