"""
Chunking Pipeline Script - Orchestrates document chunking for Phase 2
Processes extracted documents, chunks them, and validates the output
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from chunker import DocumentChunker
from data_validator import DataValidator
from quality_control import QualityControl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/chunking.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ChunkingPipeline:
    """Pipeline for chunking documents and quality control"""
    
    def __init__(
        self,
        input_dir: str = "data/extracted",
        output_dir: str = "data/processed/chunks",
        chunk_size: int = 750,
        overlap: int = 150,
        boundary: str = "paragraph"
    ):
        """
        Initialize the chunking pipeline
        
        Args:
            input_dir: Directory containing extracted JSON files
            output_dir: Directory to save chunked documents
            chunk_size: Target chunk size in tokens
            overlap: Overlap between chunks in tokens
            boundary: Boundary preservation strategy
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.chunker = DocumentChunker(
            chunk_size=chunk_size,
            overlap=overlap,
            boundary=boundary
        )
        self.validator = DataValidator()
        self.quality_control = QualityControl()
    
    def run(self):
        """Run the chunking pipeline"""
        logger.info("Starting chunking pipeline")
        
        # Load extracted documents
        documents = self._load_documents()
        logger.info(f"Loaded {len(documents)} documents")
        
        if not documents:
            logger.warning("No documents found to process")
            return
        
        # Validate documents
        validation_reports = []
        for doc in documents:
            report = self.validator.validate_document(doc)
            validation_reports.append(report)
            if not report["is_valid"]:
                logger.warning(
                    f"Validation failed for {doc.get('scheme_info', {}).get('scheme_name', 'Unknown')}"
                )
        
        # Chunk documents
        all_chunks = []
        for doc in documents:
            try:
                chunks = self.chunker.chunk_document(doc)
                all_chunks.extend(chunks)
                logger.info(
                    f"Chunked {doc.get('scheme_info', {}).get('scheme_name', 'Unknown')} into {len(chunks)} chunks"
                )
            except Exception as e:
                logger.error(f"Failed to chunk document: {e}")
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        
        # Save chunks
        self._save_chunks(all_chunks)
        
        # Generate quality report
        quality_report = self.quality_control.generate_quality_report(documents)
        self._save_quality_report(quality_report)
        
        # Generate chunking summary
        summary = self._generate_summary(documents, all_chunks, validation_reports, quality_report)
        self._save_summary(summary)
        
        logger.info("Chunking pipeline completed successfully")
    
    def _load_documents(self) -> List[Dict[str, Any]]:
        """
        Load extracted JSON documents
        
        Returns:
            List of document dictionaries
        """
        documents = []
        
        if not self.input_dir.exists():
            logger.error(f"Input directory does not exist: {self.input_dir}")
            return documents
        
        json_files = list(self.input_dir.glob("*.json"))
        
        # Skip summary file
        json_files = [f for f in json_files if f.name != "extraction_summary.json"]
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    doc = json.load(f)
                    documents.append(doc)
                    logger.info(f"Loaded document: {json_file.name}")
            except Exception as e:
                logger.error(f"Failed to load {json_file.name}: {e}")
        
        return documents
    
    def _save_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Save chunks to JSON files
        
        Args:
            chunks: List of chunk dictionaries
        """
        # Save all chunks to a single file
        output_file = self.output_dir / "all_chunks.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(chunks, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(chunks)} chunks to {output_file}")
            
            # Also save chunks per scheme
            chunks_by_scheme = {}
            for chunk in chunks:
                scheme_name = chunk["metadata"]["scheme_name"]
                if scheme_name not in chunks_by_scheme:
                    chunks_by_scheme[scheme_name] = []
                chunks_by_scheme[scheme_name].append(chunk)
            
            for scheme_name, scheme_chunks in chunks_by_scheme.items():
                scheme_slug = scheme_name.lower().replace(" ", "_").replace("-", "_")
                scheme_file = self.output_dir / f"{scheme_slug}_chunks.json"
                
                with open(scheme_file, 'w', encoding='utf-8') as f:
                    json.dump(scheme_chunks, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Saved {len(scheme_chunks)} chunks for {scheme_name}")
        
        except Exception as e:
            logger.error(f"Failed to save chunks: {e}")
    
    def _save_quality_report(self, report: Dict[str, Any]):
        """
        Save quality report to JSON file
        
        Args:
            report: Quality report dictionary
        """
        output_file = self.output_dir / "quality_report.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved quality report to {output_file}")
        
        except Exception as e:
            logger.error(f"Failed to save quality report: {e}")
    
    def _generate_summary(
        self,
        documents: List[Dict[str, Any]],
        chunks: List[Dict[str, Any]],
        validation_reports: List[Dict[str, Any]],
        quality_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate chunking summary
        
        Args:
            documents: List of original documents
            chunks: List of chunked documents
            validation_reports: List of validation reports
            quality_report: Quality control report
        
        Returns:
            Summary dictionary
        """
        summary = {
            "chunking_date": datetime.utcnow().isoformat(),
            "total_documents": len(documents),
            "total_chunks": len(chunks),
            "chunks_per_document": len(chunks) / len(documents) if documents else 0,
            "validation_summary": {
                "valid_documents": sum(1 for r in validation_reports if r["is_valid"]),
                "invalid_documents": sum(1 for r in validation_reports if not r["is_valid"]),
                "total_errors": sum(len(r["errors"]) for r in validation_reports),
                "total_warnings": sum(len(r["warnings"]) for r in validation_reports)
            },
            "quality_score": quality_report["summary"].get("overall_quality_score", 0),
            "chunking_parameters": {
                "chunk_size": self.chunker.chunk_size,
                "overlap": self.chunker.overlap,
                "boundary": self.chunker.boundary
            },
            "chunk_distribution": self._get_chunk_distribution(chunks),
            "schemes_processed": [
                doc.get("scheme_info", {}).get("scheme_name")
                for doc in documents
            ]
        }
        
        return summary
    
    def _get_chunk_distribution(self, chunks: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get distribution of chunk types
        
        Args:
            chunks: List of chunk dictionaries
        
        Returns:
            Dictionary of chunk type counts
        """
        distribution = {}
        
        for chunk in chunks:
            chunk_type = chunk.get("chunk_type", "unknown")
            distribution[chunk_type] = distribution.get(chunk_type, 0) + 1
        
        return distribution
    
    def _save_summary(self, summary: Dict[str, Any]):
        """
        Save summary to JSON file
        
        Args:
            summary: Summary dictionary
        """
        output_file = self.output_dir / "chunking_summary.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved chunking summary to {output_file}")
        
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")


def main():
    """Main entry point"""
    pipeline = ChunkingPipeline(
        input_dir="data/extracted",
        output_dir="data/processed/chunks",
        chunk_size=750,
        overlap=150,
        boundary="paragraph"
    )
    pipeline.run()


if __name__ == "__main__":
    main()
