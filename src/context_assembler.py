"""
Context Assembler Module - Assembles retrieved chunks into coherent context
Handles deduplication, ordering, and context window limits
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ContextAssembler:
    """Assembles retrieved chunks into context for LLM generation"""
    
    def __init__(self, max_context_tokens: int = 2000, max_chunks: int = 5):
        """
        Initialize context assembler
        
        Args:
            max_context_tokens: Maximum tokens in assembled context
            max_chunks: Maximum number of chunks to include
        """
        self.max_context_tokens = max_context_tokens
        self.max_chunks = max_chunks
    
    def assemble(
        self,
        chunks: List[Dict[str, Any]],
        query: str
    ) -> Dict[str, Any]:
        """
        Assemble retrieved chunks into coherent context
        
        Args:
            chunks: List of retrieved chunks with metadata
            query: Original user query
        
        Returns:
            Dictionary with assembled context and metadata
        """
        if not chunks:
            return {
                "context": "",
                "sources": [],
                "total_chunks": 0,
                "total_tokens": 0
            }
        
        try:
            # Step 1: Deduplicate chunks
            deduplicated = self._deduplicate_chunks(chunks)
            logger.info(f"Deduplicated {len(chunks)} chunks to {len(deduplicated)}")
            
            # Step 2: Order by relevance
            ordered = self._order_by_relevance(deduplicated)
            
            # Step 3: Limit chunks
            limited = ordered[:self.max_chunks]
            
            # Step 4: Format context
            context_parts = []
            sources = []
            
            for i, chunk in enumerate(limited, 1):
                # Format chunk text
                chunk_text = chunk.get("text", "").strip()
                if not chunk_text:
                    continue
                
                # Add chunk with source marker
                context_parts.append(f"[Document {i}]\n{chunk_text}\n")
                
                # Extract source information
                metadata = chunk.get("metadata", {})
                source_info = {
                    "chunk_id": chunk.get("chunk_id", f"chunk_{i}"),
                    "scheme_name": metadata.get("scheme_name", "Unknown"),
                    "source_url": metadata.get("source_url", ""),
                    "last_updated": metadata.get("last_updated", ""),
                    "similarity": chunk.get("similarity", 0.0),
                    "chunk_type": chunk.get("chunk_type", "general")
                }
                sources.append(source_info)
            
            # Join context parts
            assembled_context = "\n".join(context_parts)
            
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            estimated_tokens = len(assembled_context) // 4
            
            # If context exceeds limit, truncate
            if estimated_tokens > self.max_context_tokens:
                logger.warning(f"Context too long ({estimated_tokens} tokens), truncating")
                assembled_context = self._truncate_context(
                    assembled_context, 
                    self.max_context_tokens
                )
                estimated_tokens = self.max_context_tokens
            
            return {
                "context": assembled_context,
                "sources": sources,
                "total_chunks": len(limited),
                "total_tokens": estimated_tokens,
                "original_chunks": len(chunks),
                "deduplicated_chunks": len(deduplicated)
            }
            
        except Exception as e:
            logger.error(f"Context assembly failed: {e}")
            return {
                "context": "",
                "sources": [],
                "error": str(e),
                "total_chunks": 0,
                "total_tokens": 0
            }
    
    def _deduplicate_chunks(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate chunks based on chunk_id
        
        Args:
            chunks: List of chunks
        
        Returns:
            Deduplicated list
        """
        seen_ids = set()
        deduplicated = []
        
        for chunk in chunks:
            chunk_id = chunk.get("chunk_id")
            if chunk_id and chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                deduplicated.append(chunk)
            elif not chunk_id:
                # Include chunks without ID (shouldn't happen)
                deduplicated.append(chunk)
        
        return deduplicated
    
    def _order_by_relevance(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Order chunks by relevance score (similarity)
        
        Args:
            chunks: List of chunks
        
        Returns:
            Ordered list (highest similarity first)
        """
        return sorted(
            chunks,
            key=lambda x: x.get("similarity", 0.0),
            reverse=True
        )
    
    def _truncate_context(self, context: str, max_tokens: int) -> str:
        """
        Truncate context to fit within token limit
        
        Args:
            context: Full context string
            max_tokens: Maximum tokens allowed
        
        Returns:
            Truncated context
        """
        # Rough approximation: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        
        if len(context) <= max_chars:
            return context
        
        # Find last complete sentence before limit
        truncated = context[:max_chars]
        last_period = truncated.rfind('.')
        
        if last_period > 0:
            return truncated[:last_period + 1]
        else:
            return truncated
    
    def format_for_prompt(self, assembled_context: Dict[str, Any]) -> str:
        """
        Format assembled context for LLM prompt
        
        Args:
            assembled_context: Output from assemble()
        
        Returns:
            Formatted context string
        """
        context = assembled_context.get("context", "")
        sources = assembled_context.get("sources", [])
        
        if not context:
            return "No relevant information found."
        
        # Add source summary at the end
        source_urls = []
        latest_date = None
        
        for source in sources:
            url = source.get("source_url", "")
            if url and url not in source_urls:
                source_urls.append(url)
            
            date_str = source.get("last_updated", "")
            if date_str:
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    if latest_date is None or date > latest_date:
                        latest_date = date
                except ValueError:
                    pass
        
        # Format source info
        source_info = f"\n\nSources: {', '.join(source_urls) if source_urls else 'Unknown'}"
        if latest_date:
            source_info += f"\nLast Updated: {latest_date.strftime('%Y-%m-%d')}"
        
        return context + source_info
    
    def get_source_for_answer(
        self,
        assembled_context: Dict[str, Any],
        answer_chunk_index: int = 0
    ) -> Dict[str, str]:
        """
        Get the primary source for an answer
        
        Args:
            assembled_context: Output from assemble()
            answer_chunk_index: Which chunk provided the answer (default: first)
        
        Returns:
            Source information dictionary
        """
        sources = assembled_context.get("sources", [])
        
        if not sources:
            return {
                "url": "",
                "scheme_name": "Unknown",
                "last_updated": ""
            }
        
        # Get the most relevant source (first by default)
        primary_source = sources[min(answer_chunk_index, len(sources) - 1)]
        
        return {
            "url": primary_source.get("source_url", ""),
            "scheme_name": primary_source.get("scheme_name", "Unknown"),
            "last_updated": primary_source.get("last_updated", ""),
            "similarity": str(primary_source.get("similarity", 0.0))
        }


class SimpleContextAssembler(ContextAssembler):
    """Simplified context assembler for basic use cases"""
    
    def assemble(
        self,
        chunks: List[Dict[str, Any]],
        query: str
    ) -> str:
        """
        Simple assembly - just join chunk texts
        
        Args:
            chunks: List of chunks
            query: User query
        
        Returns:
            Simple context string
        """
        if not chunks:
            return ""
        
        texts = []
        for chunk in chunks[:self.max_chunks]:
            text = chunk.get("text", "").strip()
            if text:
                texts.append(text)
        
        return "\n\n".join(texts)
