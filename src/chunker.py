"""
Document Chunker Module - Splits extracted documents into chunks for vector database
Implements semantic chunking with boundary preservation
"""

import logging
import re
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Chunks documents into optimal sizes for retrieval"""
    
    def __init__(
        self,
        chunk_size: int = 750,
        overlap: int = 150,
        boundary: str = "paragraph"
    ):
        """
        Initialize the document chunker
        
        Args:
            chunk_size: Target chunk size in tokens (default: 750)
            overlap: Overlap between chunks in tokens (default: 150)
            boundary: Boundary preservation strategy (paragraph, sentence)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.boundary = boundary
    
    def chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk a document into smaller pieces
        
        Args:
            document: Extracted document dictionary
        
        Returns:
            List of chunk dictionaries with metadata
        """
        try:
            # Convert document to text
            text = self._document_to_text(document)
            
            # Split text into chunks
            text_chunks = self._split_text(text)
            
            # Create chunk dictionaries with metadata
            chunks = self._create_chunks_with_metadata(
                text_chunks, document
            )
            
            logger.info(
                f"Chunked document into {len(chunks)} chunks"
            )
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to chunk document: {e}")
            raise
    
    def _document_to_text(self, document: Dict[str, Any]) -> str:
        """
        Convert document dictionary to text string
        
        Args:
            document: Document dictionary
        
        Returns:
            Text representation of document
        """
        sections = []
        
        # Scheme information
        scheme_info = document.get("scheme_info", {})
        sections.append(f"Scheme Name: {scheme_info.get('scheme_name', 'N/A')}")
        sections.append(f"Scheme Code: {scheme_info.get('scheme_code', 'N/A')}")
        sections.append(f"Category: {scheme_info.get('category', 'N/A')}")
        sections.append(f"Sub-Category: {scheme_info.get('sub_category', 'N/A')}")
        sections.append("")
        
        # Financial details
        financial = document.get("financial_details", {})
        sections.append("Financial Details:")
        sections.append(f"Expense Ratio: {financial.get('expense_ratio', 'N/A')}%")
        sections.append(f"Exit Load: {financial.get('exit_load', 'N/A')}")
        sections.append(f"Minimum Investment: ₹{financial.get('minimum_investment', 'N/A')}")
        sections.append(f"SIP Amount: ₹{financial.get('sip_amount', 'N/A')}")
        sections.append(f"NAV: ₹{financial.get('nav', 'N/A')}")
        sections.append(f"NAV Date: {financial.get('nav_date', 'N/A')}")
        sections.append("")
        
        # Risk and returns
        risk_returns = document.get("risk_and_returns", {})
        sections.append("Risk and Returns:")
        sections.append(f"Risk Level: {risk_returns.get('risk_level', 'N/A')}")
        sections.append(f"Benchmark: {risk_returns.get('benchmark', 'N/A')}")
        sections.append(f"AUM: ₹{risk_returns.get('aum', 'N/A')} Cr")
        
        returns = risk_returns.get("returns", {})
        if returns:
            sections.append("Returns:")
            for period, value in returns.items():
                if value is not None:
                    sections.append(f"  {period.replace('_', ' ').title()}: {value}%")
        sections.append("")
        
        # Fund management
        fund_mgmt = document.get("fund_management", {})
        sections.append("Fund Management:")
        sections.append(f"Fund Manager: {fund_mgmt.get('fund_manager', 'N/A')}")
        if fund_mgmt.get('fund_manager_experience'):
            sections.append(f"Experience: {fund_mgmt.get('fund_manager_experience')}")
        sections.append("")
        
        # Portfolio
        portfolio = document.get("portfolio", {})
        if portfolio.get("holdings"):
            sections.append("Top Holdings:")
            for holding in portfolio["holdings"][:5]:
                name = holding.get("name", "N/A")
                percentage = holding.get("percentage", "N/A")
                sections.append(f"  {name}: {percentage}%")
        
        return "\n".join(sections)
    
    def _split_text(self, text: str) -> List[str]:
        """
        Split text into chunks based on boundary preservation
        
        Args:
            text: Text to split
        
        Returns:
            List of text chunks
        """
        if self.boundary == "paragraph":
            return self._split_by_paragraph(text)
        elif self.boundary == "sentence":
            return self._split_by_sentence(text)
        else:
            return self._split_by_token(text)
    
    def _split_by_paragraph(self, text: str) -> List[str]:
        """
        Split text by paragraphs
        
        Args:
            text: Text to split
        
        Returns:
            List of paragraph-based chunks
        """
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_length = 0
        
        for paragraph in paragraphs:
            paragraph_length = len(paragraph.split())
            
            # If paragraph alone exceeds chunk size, split it
            if paragraph_length > self.chunk_size:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                # Split long paragraph by sentences
                sentences = self._split_paragraph_by_sentences(paragraph)
                for sentence in sentences:
                    sentence_length = len(sentence.split())
                    if current_length + sentence_length > self.chunk_size:
                        if current_chunk:
                            chunks.append("\n\n".join(current_chunk))
                        current_chunk = [sentence]
                        current_length = sentence_length
                    else:
                        current_chunk.append(sentence)
                        current_length += sentence_length
            else:
                # Add paragraph to current chunk
                if current_length + paragraph_length > self.chunk_size:
                    if current_chunk:
                        chunks.append("\n\n".join(current_chunk))
                    current_chunk = [paragraph]
                    current_length = paragraph_length
                else:
                    current_chunk.append(paragraph)
                    current_length += paragraph_length
        
        # Add remaining chunk
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        
        # Add overlap
        chunks = self._add_overlap(chunks)
        
        return chunks
    
    def _split_by_sentence(self, text: str) -> List[str]:
        """
        Split text by sentences
        
        Args:
            text: Text to split
        
        Returns:
            List of sentence-based chunks
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length > self.chunk_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        chunks = self._add_overlap(chunks)
        
        return chunks
    
    def _split_by_token(self, text: str) -> List[str]:
        """
        Split text by tokens (simple word-based)
        
        Args:
            text: Text to split
        
        Returns:
            List of token-based chunks
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk = " ".join(words[i:i + self.chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def _split_paragraph_by_sentences(self, paragraph: str) -> List[str]:
        """
        Split a long paragraph into sentences
        
        Args:
            paragraph: Paragraph to split
        
        Returns:
            List of sentences
        """
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        return sentences
    
    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """
        Add overlap between chunks
        
        Args:
            chunks: List of chunks
        
        Returns:
            Chunks with overlap
        """
        if self.overlap == 0 or len(chunks) <= 1:
            return chunks
        
        overlapped_chunks = []
        
        for i, chunk in enumerate(chunks):
            if i == 0:
                overlapped_chunks.append(chunk)
            else:
                # Get overlap from previous chunk
                previous_chunk = chunks[i - 1]
                previous_words = previous_chunk.split()
                overlap_words = previous_words[-self.overlap:]
                overlap_text = " ".join(overlap_words)
                
                # Prepend overlap to current chunk
                overlapped_chunk = f"{overlap_text} {chunk}"
                overlapped_chunks.append(overlapped_chunk)
        
        return overlapped_chunks
    
    def _create_chunks_with_metadata(
        self,
        text_chunks: List[str],
        document: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create chunk dictionaries with metadata
        
        Args:
            text_chunks: List of text chunks
            document: Original document dictionary
        
        Returns:
            List of chunk dictionaries with metadata
        """
        chunks_with_metadata = []
        
        scheme_info = document.get("scheme_info", {})
        metadata = document.get("metadata", {})
        
        for i, text_chunk in enumerate(text_chunks):
            chunk_dict = {
                "chunk_id": f"{scheme_info.get('scheme_code', 'unknown')}_chunk_{i+1}",
                "chunk_text": text_chunk,
                "chunk_index": i,
                "chunk_type": self._determine_chunk_type(text_chunk),
                "metadata": {
                    "source_url": metadata.get("source_url"),
                    "scheme_name": scheme_info.get("scheme_name"),
                    "scheme_code": scheme_info.get("scheme_code"),
                    "category": scheme_info.get("category"),
                    "sub_category": scheme_info.get("sub_category"),
                    "document_type": "scheme_details",
                    "last_updated": metadata.get("last_updated"),
                    "chunked_at": datetime.utcnow().isoformat(),
                    "chunking_version": "1.0.0"
                }
            }
            chunks_with_metadata.append(chunk_dict)
        
        return chunks_with_metadata
    
    def _determine_chunk_type(self, text: str) -> str:
        """
        Determine the type of chunk based on content
        
        Args:
            text: Chunk text
        
        Returns:
            Chunk type (general, financial, risk, portfolio)
        """
        text_lower = text.lower()
        
        if "expense ratio" in text_lower or "nav" in text_lower or "exit load" in text_lower:
            return "financial"
        elif "risk level" in text_lower or "benchmark" in text_lower or "returns" in text_lower:
            return "risk"
        elif "holdings" in text_lower or "portfolio" in text_lower:
            return "portfolio"
        else:
            return "general"
