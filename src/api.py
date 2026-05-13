"""
FastAPI Backend for Mutual Fund FAQ Assistant
Exposes RAG pipeline as REST API endpoints
"""

import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import RAG pipeline
try:
    from src.rag_pipeline import RAGPipeline
except ImportError:
    from rag_pipeline import RAGPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global RAG pipeline instance
rag_pipeline: Optional[RAGPipeline] = None

# Known schemes in the corpus
KNOWN_SCHEMES = [
    {
        "name": "Axis Silver FoF Direct Growth",
        "code": "120555",
        "category": "Fund of Funds",
        "sub_category": "Commodities",
        "url": "https://groww.in/mutual-funds/axis-silver-fof-direct-growth"
    },
    {
        "name": "Axis Small Cap Fund Direct Growth",
        "code": "120503",
        "category": "Equity",
        "sub_category": "Small-cap",
        "url": "https://groww.in/mutual-funds/axis-small-cap-fund-direct-growth"
    },
    {
        "name": "Axis Flexi Cap Fund Direct Growth",
        "code": "120496",
        "category": "Equity",
        "sub_category": "Flexi-cap",
        "url": "https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth"
    },
    {
        "name": "Axis Gold Fund Direct Growth",
        "code": "120551",
        "category": "Commodity",
        "sub_category": "Gold",
        "url": "https://groww.in/mutual-funds/axis-gold-fund-direct-growth"
    },
    {
        "name": "Axis Nifty India Defence Index Fund Direct Growth",
        "code": "120595",
        "category": "Index",
        "sub_category": "Thematic Index - Defence",
        "url": "https://groww.in/mutual-funds/axis-nifty-india-defence-index-fund-direct-growth"
    }
]


# Pydantic Models for API
class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str = Field(..., min_length=1, max_length=500, description="User question about mutual funds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the expense ratio of Axis Flexi Cap Fund?"
            }
        }


class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    answer: str = Field(..., description="Generated answer")
    source_url: Optional[str] = Field(None, description="Source URL for the information")
    last_updated: Optional[str] = Field(None, description="Last updated date from source")
    scheme_name: Optional[str] = Field(None, description="Related scheme name")
    has_answer: bool = Field(..., description="Whether an answer was found")
    refusal_reason: Optional[str] = Field(None, description="Reason for refusal if no answer")
    query_timestamp: str = Field(..., description="Timestamp of the query")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The expense ratio of Axis Flexi Cap Fund Direct Growth is 1.05%.",
                "source_url": "https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth",
                "last_updated": "2024-05-08",
                "scheme_name": "Axis Flexi Cap Fund Direct Growth",
                "has_answer": True,
                "refusal_reason": None,
                "query_timestamp": "2024-05-10T12:00:00Z"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    vector_db_connected: bool = Field(..., description="Vector database connection status")
    groq_available: bool = Field(..., description="Groq LLM availability")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")


class SchemesResponse(BaseModel):
    """Response model for schemes endpoint"""
    schemes: List[Dict[str, Any]] = Field(..., description="List of available schemes")
    total: int = Field(..., description="Total number of schemes")


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    logger.info("=" * 60)
    logger.info("Starting Mutual Fund FAQ Assistant API")
    logger.info("=" * 60)
    
    global rag_pipeline
    try:
        logger.info("Initializing RAG Pipeline...")
        rag_pipeline = RAGPipeline()
        logger.info("✓ RAG Pipeline initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize RAG Pipeline: {e}")
        rag_pipeline = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")


# Create FastAPI app
app = FastAPI(
    title="Mutual Fund FAQ Assistant API",
    description="Facts-only RAG-based FAQ assistant for Axis Mutual Fund schemes",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Mutual Fund FAQ Assistant API",
        "version": "1.0.0",
        "description": "Facts-only RAG-based FAQ assistant for Axis Mutual Fund schemes",
        "endpoints": {
            "query": "/query (POST)",
            "health": "/health (GET)",
            "schemes": "/schemes (GET)"
        },
        "documentation": "/docs"
    }


@app.post(
    "/query",
    response_model=QueryResponse,
    tags=["RAG"],
    responses={
        200: {"model": QueryResponse, "description": "Successful response"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def query(request: QueryRequest):
    """
    Submit a question and get an answer from the RAG system
    
    - **query**: User question about mutual funds (max 500 characters)
    - Returns: Answer with source URL if available
    
    The system will:
    1. Check for advisory/PII/out-of-scope queries
    2. Retrieve relevant chunks from vector database
    3. Generate answer using Groq LLM
    4. Return formatted response with source
    """
    if rag_pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG Pipeline not initialized. Please check server logs."
        )
    
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Process query through RAG pipeline
        response = rag_pipeline.query(request.query)
        
        logger.info(f"Query processed. Has answer: {response.has_answer}")
        
        return QueryResponse(
            answer=response.answer,
            source_url=response.source_url,
            last_updated=response.last_updated,
            scheme_name=response.scheme_name,
            has_answer=response.has_answer,
            refusal_reason=response.refusal_reason,
            query_timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"]
)
async def health():
    """
    Health check endpoint
    
    Returns system status and component availability
    """
    vector_db_ok = False
    groq_ok = False
    
    if rag_pipeline:
        try:
            # Check vector DB
            stats = rag_pipeline.get_stats()
            vector_db_ok = stats.get("total_queries", 0) >= 0  # Basic check
            
            # Check Groq
            groq_ok = rag_pipeline.groq_client is not None
        except Exception as e:
            logger.warning(f"Health check warning: {e}")
    
    return HealthResponse(
        status="healthy" if rag_pipeline else "degraded",
        vector_db_connected=vector_db_ok,
        groq_available=groq_ok,
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )


@app.get(
    "/schemes",
    response_model=SchemesResponse,
    tags=["Data"]
)
async def schemes():
    """
    Get list of available mutual fund schemes
    
    Returns all Axis Mutual Fund schemes in the knowledge base
    """
    return SchemesResponse(
        schemes=KNOWN_SCHEMES,
        total=len(KNOWN_SCHEMES)
    )


@app.get("/stats", tags=["System"])
async def stats():
    """Get RAG pipeline usage statistics"""
    if rag_pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG Pipeline not initialized"
        )
    
    return rag_pipeline.get_stats()


# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "detail": "An unexpected error occurred",
        "error_code": "INTERNAL_ERROR"
    }


# Run with: uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
