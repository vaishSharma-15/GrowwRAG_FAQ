"""
Groq LLM Client Module - Integration with Groq API for fast LLM inference
Uses llama-3.1-8b-instant or mixtral-8x7b-32768 models
"""

import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GroqResponse:
    """Response from Groq API"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


class GroqClient:
    """Client for Groq API LLM inference"""
    
    # Available models
    MODELS = {
        "llama-3.1-8b-instant": {
            "description": "Fast, cost-effective for factual Q&A",
            "max_tokens": 8192,
            "context_window": 128000
        },
        "mixtral-8x7b-32768": {
            "description": "High quality, larger context window",
            "max_tokens": 32768,
            "context_window": 32768
        },
        "llama-3.1-70b-versatile": {
            "description": "Highest quality, versatile tasks",
            "max_tokens": 8192,
            "context_window": 128000
        }
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.1,
        max_tokens: int = 500
    ):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key (or from GROQ_API_KEY env var)
            model: Model name to use
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = None
        
        if not self.api_key:
            logger.warning("Groq API key not provided. Set GROQ_API_KEY environment variable.")
        
        logger.info(f"Groq client initialized with model: {model}")
    
    def _get_client(self):
        """Get or create Groq client"""
        if self.client is None:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq client connected successfully")
            except ImportError:
                logger.error("groq package not installed. Run: pip install groq")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                raise
        return self.client
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> GroqResponse:
        """
        Generate response from LLM
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max_tokens
        
        Returns:
            GroqResponse with generated content
        """
        try:
            client = self._get_client()
            
            # Build messages
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Make API call
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                top_p=0.9,
                stop=None
            )
            
            # Extract response
            content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            logger.info(f"Generated {usage['completion_tokens']} tokens (finish_reason: {finish_reason})")
            
            return GroqResponse(
                content=content,
                model=self.model,
                usage=usage,
                finish_reason=finish_reason
            )
            
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            raise
    
    def generate_response(
        self,
        context: str,
        query: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate RAG response using context and query
        
        Args:
            context: Retrieved context from vector database
            query: User query
            system_prompt: Optional custom system prompt
        
        Returns:
            Dictionary with answer, source, and metadata
        """
        default_system_prompt = """You are a facts-only mutual fund FAQ assistant. 
Answer the user's question based ONLY on the provided context.
Requirements:
- Answer in maximum 3 sentences
- No investment advice or recommendations
- No opinions or speculative content
- If information is not in context, politely refuse"""
        
        prompt = f"""Context:
{context}

Question: {query}

Requirements:
- Answer in maximum 3 sentences
- Include exactly one source link from the context
- No investment advice or recommendations
- No opinions or speculative content
- If information is not in context, politely refuse

Response format:
[Answer]

Source: [URL]
Last updated from sources: [date]"""
        
        try:
            response = self.generate(
                prompt=prompt,
                system_prompt=system_prompt or default_system_prompt,
                temperature=0.1,
                max_tokens=500
            )
            
            return {
                "answer": response.content,
                "model": response.model,
                "usage": response.usage,
                "finish_reason": response.finish_reason
            }
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return {
                "answer": "I apologize, but I'm unable to process your request at this time. Please try again later.",
                "error": str(e),
                "model": self.model
            }
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models with details"""
        return self.MODELS
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate API cost (approximate)
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            Estimated cost in USD
        """
        # Pricing as of 2024 (approximate)
        pricing = {
            "llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},  # per 1M tokens
            "mixtral-8x7b-32768": {"input": 0.24, "output": 0.24},
            "llama-3.1-70b-versatile": {"input": 0.59, "output": 0.79}
        }
        
        model_pricing = pricing.get(self.model, pricing["llama-3.1-8b-instant"])
        
        input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
        output_cost = (output_tokens / 1_000_000) * model_pricing["output"]
        
        return input_cost + output_cost


def create_groq_client(
    model: str = "llama-3.1-8b-instant",
    **kwargs
) -> GroqClient:
    """
    Factory function to create Groq client
    
    Args:
        model: Model name
        **kwargs: Additional arguments for GroqClient
    
    Returns:
        GroqClient instance
    """
    return GroqClient(model=model, **kwargs)
