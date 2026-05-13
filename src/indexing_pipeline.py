"""
Phase 3 Indexing Pipeline - Indexes chunked documents into vector database
Generates embeddings and stores them with metadata for retrieval
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from src.embedder import TextEmbedder
from src.vector_db import ChromaVectorDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/phase3/indexing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class IndexingPipeline:
    """Pipeline for indexing chunked documents into vector database"""
    
    def __init__(
        self,
        input_dir: str = "data/processed/chunks",
        vector_db_path: str = "data/vector_db/chroma_db",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the indexing pipeline
        
        Args:
            input_dir: Directory containing chunked documents
            vector_db_path: Path to vector database
            model_name: Name of embedding model to use
        """
        self.input_dir = Path(input_dir)
        self.vector_db_path = Path(vector_db_path)
        
        # Initialize components
        self.embedder = TextEmbedder(model_name=model_name)
        self.vector_db = ChromaVectorDB(
            persist_directory=str(vector_db_path),
            collection_name="mutual_fund_chunks"
        )
        
        # Statistics
        self.stats = {
            "total_chunks": 0,
            "indexed_chunks": 0,
            "failed_chunks": 0,
            "embeddings_generated": 0
        }
    
    def run(self):
        """Run the indexing pipeline"""
        logger.info("=" * 60)
        logger.info("Starting Phase 3: Vector Database Setup and Indexing")
        logger.info("=" * 60)
        
        try:
            # Step 1: Load chunks
            chunks = self._load_chunks()
            if not chunks:
                logger.error("No chunks found to index. Exiting.")
                return False
            
            self.stats["total_chunks"] = len(chunks)
            logger.info(f"Loaded {len(chunks)} chunks for indexing")
            
            # Step 2: Load embedding model
            logger.info("Loading embedding model...")
            self.embedder.load_model()
            logger.info(f"Model loaded: {self.embedder.model_name}")
            
            # Step 3: Connect to vector database
            logger.info("Connecting to vector database...")
            self.vector_db.connect()
            stats = self.vector_db.get_collection_stats()
            logger.info(f"Connected to collection: {stats}")
            
            # Step 4: Generate embeddings
            logger.info("Generating embeddings...")
            embeddings = self._generate_embeddings(chunks)
            
            if embeddings is None or len(embeddings) == 0:
                logger.error("Failed to generate embeddings. Exiting.")
                return False
            
            self.stats["embeddings_generated"] = len(embeddings)
            logger.info(f"Generated {len(embeddings)} embeddings of dimension {embeddings.shape[1]}")
            
            # Step 5: Index chunks in vector database
            logger.info("Indexing chunks in vector database...")
            self._index_chunks(chunks, embeddings)
            
            # Step 6: Generate report
            self._generate_report()
            
            logger.info("=" * 60)
            logger.info("Phase 3 indexing completed successfully!")
            logger.info(f"Total chunks indexed: {self.stats['indexed_chunks']}")
            logger.info(f"Failed: {self.stats['failed_chunks']}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Indexing pipeline failed: {e}", exc_info=True)
            return False
    
    def _load_chunks(self) -> List[Dict[str, Any]]:
        """
        Load chunked documents from input directory
        
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        
        if not self.input_dir.exists():
            logger.error(f"Input directory does not exist: {self.input_dir}")
            return chunks
        
        # Look for all_chunks.json or individual chunk files
        all_chunks_file = self.input_dir / "all_chunks.json"
        
        if all_chunks_file.exists():
            # Load from consolidated file
            try:
                with open(all_chunks_file, 'r', encoding='utf-8') as f:
                    chunks = json.load(f)
                logger.info(f"Loaded {len(chunks)} chunks from {all_chunks_file}")
            except Exception as e:
                logger.error(f"Failed to load {all_chunks_file}: {e}")
        else:
            # Load from individual scheme files
            chunk_files = list(self.input_dir.glob("*_chunks.json"))
            
            for chunk_file in chunk_files:
                try:
                    with open(chunk_file, 'r', encoding='utf-8') as f:
                        file_chunks = json.load(f)
                        chunks.extend(file_chunks)
                        logger.info(f"Loaded {len(file_chunks)} chunks from {chunk_file.name}")
                except Exception as e:
                    logger.error(f"Failed to load {chunk_file}: {e}")
        
        return chunks
    
    def _generate_embeddings(self, chunks: List[Dict[str, Any]]) -> Any:
        """
        Generate embeddings for chunks
        
        Args:
            chunks: List of chunk dictionaries
        
        Returns:
            Numpy array of embeddings
        """
        try:
            # Extract text from chunks
            texts = [chunk.get("chunk_text", "") for chunk in chunks]
            
            # Generate embeddings in batches to avoid memory issues
            batch_size = 32
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                logger.info(f"Processing batch {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size}")
                
                batch_embeddings = self.embedder.embed(batch)
                all_embeddings.append(batch_embeddings)
            
            # Concatenate all embeddings
            import numpy as np
            embeddings = np.vstack(all_embeddings)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return None
    
    def _index_chunks(self, chunks: List[Dict[str, Any]], embeddings: Any):
        """
        Index chunks with embeddings in vector database
        
        Args:
            chunks: List of chunk dictionaries
            embeddings: Numpy array of embeddings
        """
        try:
            # Add chunks to database
            self.vector_db.add_chunks(chunks, embeddings)
            
            self.stats["indexed_chunks"] = len(chunks)
            logger.info(f"Successfully indexed {len(chunks)} chunks")
            
            # Verify indexing
            stats = self.vector_db.get_collection_stats()
            logger.info(f"Vector database stats: {stats}")
            
        except Exception as e:
            logger.error(f"Failed to index chunks: {e}")
            self.stats["failed_chunks"] = len(chunks)
            raise
    
    def _generate_report(self):
        """Generate indexing report"""
        report = {
            "indexing_date": datetime.utcnow().isoformat(),
            "model_name": self.embedder.model_name,
            "embedding_dimension": self.embedder.get_embedding_dimension(),
            "vector_db_path": str(self.vector_db_path),
            "statistics": self.stats,
            "collection_stats": self.vector_db.get_collection_stats()
        }
        
        report_path = self.vector_db_path / "indexing_report.json"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Indexing report saved to {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to save report: {e}")


def main():
    """Main entry point"""
    pipeline = IndexingPipeline()
    success = pipeline.run()
    
    if success:
        logger.info("Phase 3 completed successfully!")
        return 0
    else:
        logger.error("Phase 3 failed!")
        return 1


if __name__ == "__main__":
    exit(main())
