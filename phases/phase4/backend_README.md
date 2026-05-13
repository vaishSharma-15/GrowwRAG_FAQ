# Phase 4 Backend API

FastAPI backend exposing the RAG pipeline as REST API endpoints.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/query` | POST | Submit question, get answer |
| `/health` | GET | Health check |
| `/schemes` | GET | List available schemes |
| `/stats` | GET | Usage statistics |
| `/docs` | GET | Auto-generated Swagger UI |

## Running the Backend

### Install Dependencies
```bash
pip install fastapi uvicorn python-multipart
```

### Start Server
```bash
# From project root
cd /Users/vaish/Documents/CursorProjects/MutualFund_RAG_FAQ

# Development (with auto-reload)
python3 -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

# Or directly
python3 src/api.py
```

### Verify Server
```bash
curl http://localhost:8000/health
```

## API Usage Examples

### 1. Query Endpoint
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the expense ratio of Axis Flexi Cap Fund?"}'
```

**Response:**
```json
{
  "answer": "The expense ratio of Axis Flexi Cap Fund Direct Growth is 1.05%.",
  "source_url": "https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth",
  "last_updated": "2024-05-08",
  "scheme_name": "Axis Flexi Cap Fund Direct Growth",
  "has_answer": true,
  "refusal_reason": null,
  "query_timestamp": "2024-05-10T12:00:00Z"
}
```

### 2. Health Check
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "vector_db_connected": true,
  "groq_available": true,
  "timestamp": "2024-05-10T12:00:00Z",
  "version": "1.0.0"
}
```

### 3. List Schemes
```bash
curl http://localhost:8000/schemes
```

**Response:**
```json
{
  "schemes": [
    {
      "name": "Axis Flexi Cap Fund Direct Growth",
      "code": "120496",
      "category": "Equity",
      "sub_category": "Flexi-cap",
      "url": "https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth"
    }
  ],
  "total": 5
}
```

## Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI with interactive API testing.

## Frontend Integration

### Example JavaScript Fetch
```javascript
async function askQuestion(query) {
  const response = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });
  
  const data = await response.json();
  return {
    answer: data.answer,
    source: data.source_url,
    hasAnswer: data.has_answer
  };
}

// Usage
askQuestion("What is the expense ratio of Axis Flexi Cap Fund?")
  .then(result => console.log(result));
```

## Configuration

### Environment Variables
```bash
export GROQ_API_KEY="your-api-key"
export LOG_LEVEL="INFO"
```

### CORS
Backend allows all origins (`["*"]`) for development. In production, restrict to your frontend domain.

## Architecture

```
Frontend (Phase 6)
    ↓ HTTP Request
FastAPI Backend (src/api.py)
    ↓ Calls
RAG Pipeline (src/rag_pipeline.py)
    ↓ Uses
Retriever → Vector DB → Groq LLM
```

## Next Step: Frontend (Phase 6)

Backend is ready for frontend integration. Frontend can:
1. Call `/schemes` to show available options
2. Call `/query` to submit user questions
3. Call `/health` for connection status

Ready for Phase 6 frontend development!
