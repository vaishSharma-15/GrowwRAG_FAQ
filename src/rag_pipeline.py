"""
RAG Pipeline - Main orchestrator for Phase 4
Integrates retrieval, context assembly, refusal detection, and Groq LLM generation
"""

import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

try:
    from src.embedder import TextEmbedder
    from src.vector_db import ChromaVectorDB
    from src.retriever import DocumentRetriever, RetrievalResult
    from src.context_assembler import ContextAssembler
    from src.refusal_detector import RefusalDetector, RefusalCheck
    from src.groq_client import GroqClient
except ImportError:
    from embedder import TextEmbedder
    from vector_db import ChromaVectorDB
    from retriever import DocumentRetriever, RetrievalResult
    from context_assembler import ContextAssembler
    from refusal_detector import RefusalDetector, RefusalCheck
    from groq_client import GroqClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/phase4/rag_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


@dataclass
class RAGResponse:
    """Response from RAG pipeline"""
    answer: str
    source_url: Optional[str]
    last_updated: Optional[str]
    scheme_name: Optional[str]
    has_answer: bool
    refusal_reason: Optional[str]
    usage_stats: Dict[str, Any]


class RAGPipeline:
    """Complete RAG pipeline with Groq LLM integration"""
    
    def __init__(
        self,
        vector_db_path: str = "data/vector_db/chroma_db",
        model_name: str = "all-MiniLM-L6-v2",
        groq_model: str = "llama-3.1-8b-instant",
        min_similarity: float = 0.1,
        top_k: int = 5,
        max_context_tokens: int = 2000,
        groq_api_key: Optional[str] = None
    ):
        """
        Initialize RAG pipeline
        
        Args:
            vector_db_path: Path to vector database
            model_name: Embedding model name
            groq_model: Groq LLM model name
            min_similarity: Minimum similarity threshold for retrieval
            top_k: Number of chunks to retrieve
            max_context_tokens: Maximum tokens in assembled context
            groq_api_key: Groq API key (or from env)
        """
        logger.info("Initializing RAG Pipeline")
        
        # Initialize components
        self.embedder = TextEmbedder(model_name=model_name)
        self.vector_db = ChromaVectorDB(persist_directory=vector_db_path)
        self.retriever = DocumentRetriever(
            vector_db=self.vector_db,
            embedder=self.embedder,
            min_similarity=min_similarity,
            top_k=top_k
        )
        self.context_assembler = ContextAssembler(max_context_tokens=max_context_tokens)
        self.refusal_detector = RefusalDetector(min_similarity_threshold=min_similarity)
        
        # Initialize Groq client
        api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if api_key:
            self.groq_client = GroqClient(
                api_key=api_key,
                model=groq_model,
                temperature=0.1,
                max_tokens=500
            )
            logger.info(f"Groq client initialized with model: {groq_model}")
        else:
            logger.warning("Groq API key not found - LLM generation disabled")
            self.groq_client = None
        
        self.usage_stats = {
            "total_queries": 0,
            "answered_queries": 0,
            "refused_queries": 0,
            "total_tokens_used": 0,
            "total_cost": 0.0
        }
        
        logger.info("RAG Pipeline initialized successfully")
    
    def query(self, user_query: str) -> RAGResponse:
        """
        Process user query through RAG pipeline
        
        Args:
            user_query: User's question
        
        Returns:
            RAGResponse with answer and metadata
        """
        logger.info(f"=" * 60)
        logger.info(f"Processing query: '{user_query}'")
        logger.info(f"=" * 60)
        
        self.usage_stats["total_queries"] += 1
        
        try:
            # Step 0: Check for greeting queries (return fixed response)
            logger.info("Step 0: Checking for greeting queries...")
            greeting_patterns = ["can you help me", "hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
            if any(pattern in user_query.lower() for pattern in greeting_patterns):
                logger.info("Greeting query detected, returning fixed response")
                return RAGResponse(
                    answer="Hello! How can I help you with Axis Mutual Fund schemes today?",
                    source_url=None,
                    last_updated=None,
                    scheme_name=None,
                    has_answer=True,
                    refusal_reason=None,
                    usage_stats=self.usage_stats.copy()
                )
            
            # Step 1: Check for refusal conditions (before retrieval)
            logger.info("Step 1: Checking refusal conditions...")
            refusal_check = self.refusal_detector.check_query(user_query, has_context=True)
            
            if refusal_check.should_refuse:
                logger.info(f"Query refused: {refusal_check.reason}")
                self.usage_stats["refused_queries"] += 1
                
                return RAGResponse(
                    answer=refusal_check.refusal_message,
                    source_url=None,
                    last_updated=None,
                    scheme_name=None,
                    has_answer=False,
                    refusal_reason=refusal_check.reason,
                    usage_stats=self.usage_stats.copy()
                )
            
            # Step 2: Retrieve relevant chunks
            logger.info("Step 2: Retrieving relevant chunks...")
            retrieval_result = self.retriever.retrieve(user_query)
            
            if not retrieval_result.has_answer or not retrieval_result.chunks:
                logger.info("No relevant chunks found")
                self.usage_stats["refused_queries"] += 1
                
                return RAGResponse(
                    answer=retrieval_result.refusal_message or "I can provide factual information about Axis mutual funds, including: • Scheme details (NAV, expense ratio, exit load) • Risk levels • Fund manager details. For general mutual fund education, please visit the official website of Groww\n\n"
                    "https://groww.in\n\n"
                    "For personalized investment advice or recommendations, please consult a SEBI-registered investment advisor.",
                    source_url=None,
                    last_updated=None,
                    scheme_name=None,
                    has_answer=False,
                    refusal_reason="no_relevant_chunks",
                    usage_stats=self.usage_stats.copy()
                )
            
            # Step 3: Assemble context
            logger.info("Step 3: Assembling context...")
            assembled = self.context_assembler.assemble(
                chunks=retrieval_result.chunks,
                query=user_query
            )
            
            if not assembled.get("context"):
                logger.warning("Context assembly resulted in empty context")
                self.usage_stats["refused_queries"] += 1
                
                return RAGResponse(
                    answer="I couldn't find relevant information to answer your question.",
                    source_url=None,
                    last_updated=None,
                    scheme_name=None,
                    has_answer=False,
                    refusal_reason="empty_context",
                    usage_stats=self.usage_stats.copy()
                )
            
            # Step 4: Format context for LLM
            context_for_prompt = self.context_assembler.format_for_prompt(assembled)
            
            # Step 5: Generate response with Groq
            logger.info("Step 4: Generating response with Groq...")
            
            if not self.groq_client:
                logger.error("Groq client not available")
                return RAGResponse(
                    answer="LLM service temporarily unavailable.",
                    source_url=None,
                    last_updated=None,
                    scheme_name=None,
                    has_answer=False,
                    refusal_reason="llm_unavailable",
                    usage_stats=self.usage_stats.copy()
                )
            
            # Get primary source
            primary_source = self.context_assembler.get_source_for_answer(assembled, 0)
            
            # Generate with Groq
            groq_response = self.groq_client.generate_response(
                context=context_for_prompt,
                query=user_query
            )
            
            answer = groq_response.get("answer", "")
            
            # Update usage stats
            usage = groq_response.get("usage", {})
            self.usage_stats["total_tokens_used"] += usage.get("total_tokens", 0)
            
            # Estimate cost
            cost = self.groq_client.estimate_cost(
                usage.get("prompt_tokens", 0),
                usage.get("completion_tokens", 0)
            )
            self.usage_stats["total_cost"] += cost
            
            logger.info(f"Response generated. Tokens used: {usage.get('total_tokens', 0)}")
            
            # Parse answer to extract source if LLM included it
            parsed_answer = self._parse_answer(answer)
            
            # If no source in answer, use primary source
            if not parsed_answer.get("source_url") and primary_source.get("url"):
                parsed_answer["source_url"] = primary_source.get("url")
            
            self.usage_stats["answered_queries"] += 1
            
            return RAGResponse(
                answer=parsed_answer.get("answer", answer),
                source_url=parsed_answer.get("source_url") or primary_source.get("url"),
                last_updated=primary_source.get("last_updated"),
                scheme_name=primary_source.get("scheme_name"),
                has_answer=True,
                refusal_reason=None,
                usage_stats=self.usage_stats.copy()
            )
            
        except Exception as e:
            logger.error(f"RAG pipeline error: {e}", exc_info=True)
            return RAGResponse(
                answer="An error occurred while processing your request. Please try again later.",
                source_url=None,
                last_updated=None,
                scheme_name=None,
                has_answer=False,
                refusal_reason="error",
                usage_stats=self.usage_stats.copy()
            )
    
    def _parse_answer(self, answer: str) -> Dict[str, str]:
        """
        Parse LLM response to extract answer and source
        
        Args:
            answer: Raw LLM response
        
        Returns:
            Parsed answer components
        """
        result = {
            "answer": answer,
            "source_url": None,
            "last_updated": None
        }
        
        # Try to extract source URL
        lines = answer.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if 'source:' in line_lower or 'source :' in line_lower:
                # Extract URL after "Source:"
                url_start = line.find('http')
                if url_start != -1:
                    result["source_url"] = line[url_start:].strip()
                    # Remove this line from answer
                    result["answer"] = result["answer"].replace(line, '').strip()
            
            if 'last updated' in line_lower or 'last updated:' in line_lower:
                # Extract date
                parts = line.split(':')
                if len(parts) > 1:
                    result["last_updated"] = parts[1].strip()
                    result["answer"] = result["answer"].replace(line, '').strip()
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline usage statistics"""
        return self.usage_stats.copy()
    
    def test_pipeline(self, test_queries: List[str]) -> List[Dict[str, Any]]:
        """
        Test pipeline with sample queries
        
        Args:
            test_queries: List of test queries
        
        Returns:
            List of test results
        """
        results = []
        
        for query in test_queries:
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing query: {query}")
            
            response = self.query(query)
            
            results.append({
                "query": query,
                "has_answer": response.has_answer,
                "answer_preview": response.answer[:100] + "..." if len(response.answer) > 100 else response.answer,
                "source": response.source_url,
                "refusal_reason": response.refusal_reason
            })
            
            status = "✓ ANSWERED" if response.has_answer else "✗ REFUSED"
            logger.info(f"Result: {status}")
            if response.refusal_reason:
                logger.info(f"Reason: {response.refusal_reason}")
        
        return results


def main():
    """Test RAG pipeline"""
    import sys
    
    # Check for Groq API key
    if not os.getenv("GROQ_API_KEY"):
        print("WARNING: GROQ_API_KEY not set. Set it to test LLM generation.")
        print("Example: export GROQ_API_KEY='your-api-key'")
    
    # Initialize pipeline
    pipeline = RAGPipeline()
    
    # Test queries
    test_queries = [
        "What is the expense ratio of Axis Flexi Cap Fund?",
        "Tell me about Axis Small Cap Fund exit load",
        "What is the NAV of Axis Gold Fund?",
        "Should I invest in Axis Flexi Cap Fund?",  # Should refuse - advisory
        "What is HDFC Top 100 Fund?",  # Should refuse - unknown scheme
    ]
    
    print("\n" + "="*60)
    print("RAG Pipeline Test")
    print("="*60)
    
    results = pipeline.test_pipeline(test_queries)
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    answered = sum(1 for r in results if r["has_answer"])
    refused = sum(1 for r in results if not r["has_answer"])
    
    print(f"Total queries: {len(results)}")
    print(f"Answered: {answered}")
    print(f"Refused: {refused}")
    
    # Print usage stats
    stats = pipeline.get_stats()
    print(f"\nTotal tokens used: {stats['total_tokens_used']}")
    print(f"Estimated cost: ${stats['total_cost']:.4f}")


if __name__ == "__main__":
    main()
