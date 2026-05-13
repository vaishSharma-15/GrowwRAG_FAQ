# Phase 6: User Interface Development

Streamlit-based frontend for the Mutual Fund FAQ Assistant.

## Features

### UI Components (per Architecture)
- ✅ **Welcome message** - Explains system purpose
- ✅ **Three example questions** - Clickable buttons for quick testing
- ✅ **Query input field** - Text input for custom questions
- ✅ **Submit button** - Primary action button
- ✅ **Response display area** - Formatted answer with metadata
- ✅ **Disclaimer banner** - "Facts-only. No investment advice."

### Additional Features
- Loading spinner during query processing
- Error handling with user-friendly messages
- Source link display
- Refusal reason display (advisory, PII, out-of-scope, unknown scheme, no context)
- Available schemes list (expandable)
- Mobile-responsive design
- API health check indicator

## Running the Frontend

### Prerequisites
```bash
# Backend must be running first
python3 -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
# Install Streamlit
pip install streamlit

# Run the app
cd /Users/vaish/Documents/CursorProjects/MutualFund_RAG_FAQ
streamlit run src/app.py
```

The app will open at `http://localhost:8501`

## Configuration

### Environment Variables
```bash
# Optional: Set custom API URL (default: http://localhost:8000)
export API_BASE_URL="http://localhost:8000"

# Run Streamlit
streamlit run src/app.py
```

## Usage

### Example Workflow

1. **Start Backend**:
   ```bash
   python3 -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend** (in another terminal):
   ```bash
   streamlit run src/app.py
   ```

3. **Open Browser**:
   - Frontend: `http://localhost:8501`
   - API Docs: `http://localhost:8000/docs`

4. **Ask Questions**:
   - Click example buttons, or
   - Type custom question in input field
   - Click "Get Answer"

### Example Questions
- "What is the expense ratio of Axis Flexi Cap Fund?"
- "How does Axis Small Cap Fund perform?"
- "What is the AUM of Axis Silver FoF?"

## UI Design

### Layout
```
┌─────────────────────────────────────┐
│     💰 Mutual Fund FAQ Assistant    │  ← Header
│   Get factual answers about Axis    │  ← Sub-header
│        Mutual Fund schemes          │
├─────────────────────────────────────┤
│ ⚠️ Facts-only. No investment advice │  ← Disclaimer
├─────────────────────────────────────┤
│  [Example 1] [Example 2] [Example 3]│  ← Example buttons
├─────────────────────────────────────┤
│  Your question: [Input field    ]   │  ← Query input
│           [🔍 Get Answer]           │  ← Submit button
├─────────────────────────────────────┤
│  Answer:                            │  ← Response area
│  ┌─────────────────────────────┐    │
│  │ [Generated answer text]     │    │
│  └─────────────────────────────┘    │
│  📄 Source: [URL]                   │  ← Source link
│  Last updated: 2024-05-08           │  ← Metadata
├─────────────────────────────────────┤
│  📋 Available Schemes [expand]      │  ← Schemes list
├─────────────────────────────────────┤
│  Powered by RAG + Groq LLM          │  ← Footer
└─────────────────────────────────────┘
```

### Design Principles (from Architecture)
- ✅ **Clean and simple layout** - Minimalist design
- ✅ **Mobile-responsive** - Streamlit handles this automatically
- ✅ **Clear visual hierarchy** - Headers, sections, visual separation
- ✅ **Accessible design** - High contrast, readable fonts

## Error Handling

### Scenarios Handled

1. **Backend Not Running**:
   - Error message displayed
   - Demo mode explanation
   - Instructions to start backend

2. **Query Refused**:
   - Advisory queries → Redirect to SEBI advisor
   - PII requests → Explain privacy policy
   - Out-of-scope → Clarify scope
   - Unknown scheme → List available schemes

3. **Network Errors**:
   - Timeout handling
   - Connection error messages

## Screenshots

### Main Interface
```
💰 Mutual Fund FAQ Assistant
Get factual answers about Axis Mutual Fund schemes

⚠️ Facts-only information. This system does not provide investment advice.

Try an example question:
[What is the expense ratio] [How does Axis Small Cap] [What is the AUM]

Or ask your own question:
Your question: [What is the expense ratio of Axis Flexi Cap Fund?]
              [🔍 Get Answer]
```

### Response Display
```
Answer:
┌────────────────────────────────────────┐
│ The expense ratio of Axis Flexi Cap   │
│ Fund Direct Growth is 1.05%.         │
└────────────────────────────────────────┘
📄 Source: https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth
Last updated: 2024-05-08
Scheme: Axis Flexi Cap Fund Direct Growth
```

### Refusal Display
```
❌ I cannot provide investment advice. 
   Please consult a SEBI-registered investment advisor.
```

## Architecture Integration

### Data Flow
```
User (Browser)
    ↓
Streamlit Frontend (localhost:8501)
    ↓ HTTP POST /query
FastAPI Backend (localhost:8000)
    ↓
RAG Pipeline
    ↓
Groq LLM + Vector DB
```

### Technology Stack
| Layer | Technology |
|-------|------------|
| Frontend | Streamlit 1.32.0 |
| Backend | FastAPI + Uvicorn |
| LLM | Groq (llama-3.1-8b-instant) |
| Vector DB | ChromaDB |

## Next Steps

Phase 6 is complete. The system now has:
- ✅ Full RAG pipeline (Phases 1-5)
- ✅ Backend API (Phase 4/5)
- ✅ Frontend UI (Phase 6)

### Optional Enhancements
- Chat history / conversation memory
- User feedback (thumbs up/down)
- Dark mode
- Export conversation
- Voice input
- Multi-language support

## Troubleshooting

### Frontend won't start
```bash
# Check if Streamlit is installed
pip install streamlit

# Run with verbose output
streamlit run src/app.py --logger.level=debug
```

### Can't connect to backend
1. Ensure backend is running: `curl http://localhost:8000/health`
2. Check `API_BASE_URL` environment variable
3. Verify firewall settings

### Slow responses
- First query may be slower (model loading)
- Check Groq API latency
- Verify vector DB is indexed

## References

- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PhaseWiseArchitecture.md](/docs/PhaseWiseArchitecture.md) - Phase 6 specifications
