# Phase-Wise Architecture: Mutual Fund FAQ Assistant (Facts-Only Q&A)

## Overview
This document outlines the detailed phase-wise architecture for building a lightweight Retrieval-Augmented Generation (RAG)-based FAQ assistant for mutual fund schemes. The system prioritizes accuracy, compliance, and transparency over intelligence, ensuring users receive only verified, source-backed financial information.

---

## Phase 1: Data Collection & Corpus Preparation

### 1.1 AMC and Scheme Selection
**Objective**: Select one Asset Management Company (AMC) and 3-5 mutual fund schemes with category diversity.

**Activities**:
- Research and select one AMC (e.g., HDFC, ICICI Prudential, SBI)
- Choose 3-5 schemes across categories:
  - Large-cap funds
  - Flexi-cap funds
  - ELSS (Equity Linked Savings Scheme)
  - Debt funds
  - Hybrid funds
- Document scheme codes, names, and categories

**Selected AMC**: Axis Mutual Fund

**Selected Schemes**:
1. Axis Silver FoF Direct Growth (Fund of Funds - Commodities)
2. Axis Small Cap Fund Direct Growth (Small-cap equity)
3. Axis Flexi Cap Fund Direct Growth (Flexi-cap equity)
4. Axis Gold Fund Direct Growth (Gold - commodity)
5. Axis Nifty India Defence Index Fund Direct Growth (Index fund - Defence)

**Deliverables**:
- AMC selection document
- Scheme selection matrix with categories

### 1.2 Source URL Collection
**Objective**: Collect the official public URLs for the selected schemes.

**Activities**:
- Validate URLs for accessibility
- Extract scheme information from each URL
- Document URL metadata (scheme name, category)

**Selected Scheme URLs (Only Sources for This Project)**:
- https://groww.in/mutual-funds/axis-silver-fof-direct-growth
- https://groww.in/mutual-funds/axis-small-cap-fund-direct-growth
- https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth
- https://groww.in/mutual-funds/axis-gold-fund-direct-growth
- https://groww.in/mutual-funds/axis-nifty-india-defence-index-fund-direct-growth

**Note**: These 5 URLs are the ONLY sources that will be used for this project. No additional URLs from AMC, AMFI, or SEBI will be used.

**Deliverables**:
- Curated URL list with metadata (scheme, document type, source)
- URL validation report

### 1.3 Data Extraction Strategy
**Objective**: Define approach for extracting content from the 5 selected URLs.

**Activities**:
- Evaluate extraction methods:
  - Web scraping (respecting robots.txt)
  - HTML parsing for scheme details
  - Handle dynamic content if present
- Define data format standards
- Plan incremental updates strategy

**Deliverables**:
- Data extraction methodology document
- Format specification

---

## Phase 2: Document Ingestion & Processing

### 2.1 Content Extraction Pipeline
**Objective**: Build pipeline to extract and normalize content from the 5 selected URLs.

**Components**:
- **Web Scraper Module**
  - Fetch HTML content from the 5 Groww URLs
  - Extract relevant sections (scheme details, performance data, risk metrics)
  - Handle dynamic content if present
  
- **Content Normalizer**
  - Standardize text formatting
  - Remove headers/footers
  - Clean special characters

**Deliverables**:
- Extraction pipeline code
- Sample extracted documents

### 2.2 Document Chunking Strategy
**Objective**: Split documents into optimal chunks for retrieval.

**Activities**:
- Define chunking parameters:
  - Chunk size: 500-1000 tokens
  - Overlap: 100-200 tokens
  - Boundary preservation (paragraph/sentence)
- Implement semantic chunking for FAQ content
- Create metadata for each chunk:
  - Source URL
  - Scheme name
  - Document type
  - Last updated date
  - Category tags

**Deliverables**:
- Chunked document corpus
- Chunking configuration

### 2.3 Data Validation & Quality Control
**Objective**: Ensure extracted data accuracy and completeness.

**Activities**:
- Validate numerical data (expense ratios, exit loads)
- Cross-reference facts across sources
- Check for broken links or outdated information
- Implement data freshness tracking

**Deliverables**:
- Data quality report
- Validation scripts

---

## Phase 3: Vector Database Setup

### 3.1 Embedding Model Selection
**Objective**: Choose appropriate embedding model for semantic search.

**Evaluation Criteria**:
- Performance on financial domain text
- Model size and inference speed
- Cost considerations
- Language support (English)

**Recommended Options**:
- OpenAI text-embedding-3-small (cost-effective, good performance)
- Sentence Transformers (all-MiniLM-L6-v2 for local deployment)
- BGE-small-en-v1.5 (open source, strong performance)

**Deliverables**:
- Embedding model selection report
- Benchmark results

### 3.2 Vector Database Configuration
**Objective**: Set up vector database for efficient similarity search.

**Technology Options**:
- **ChromaDB** (local, lightweight)
- **Pinecone** (managed, scalable)
- **Weaviate** (hybrid search capabilities)
- **FAISS** (local, high performance)

**Configuration**:
- Index type (HNSW for approximate search)
- Dimensionality (based on embedding model)
- Metadata filtering support
- Batch indexing strategy

**Deliverables**:
- Vector database setup
- Indexing pipeline code

### 3.3 Corpus Indexing
**Objective**: Index chunked documents with embeddings.

**Activities**:
- Generate embeddings for all chunks
- Store vectors with metadata in database
- Test retrieval quality with sample queries
- Optimize index parameters
- **IMPORTANT**: If no relevant information is found for a query, the system will NOT attach any URL or provide fabricated information. The system will politely refuse to answer instead.
- **Privacy Note**: No personal information (PII) will be collected, stored, or included in any responses.

**Deliverables**:
- Indexed vector database
- Retrieval performance metrics
- No-answer handling documentation

---

## Phase 4: RAG Pipeline Development

### 4.1 Retrieval Component
**Objective**: Implement semantic retrieval with metadata filtering.

**Components**:
- **Query Embedder**
  - Convert user query to embedding
  - Handle query preprocessing (lowercase, remove special chars)
  
- **Similarity Search**
  - Perform vector similarity search
  - Retrieve top-k relevant chunks (k=3-5)
  - Apply metadata filters (scheme, category)
  
- **Re-ranking** (Optional)
  - Cross-encoder for better relevance
  - Diversity in retrieved results

**Deliverables**:
- Retrieval module code
- Retrieval evaluation metrics

### 4.2 Context Assembly
**Objective**: Assemble retrieved chunks into coherent context.

**Activities**:
- Deduplicate overlapping chunks
- Order chunks by relevance
- Add source information to context
- Limit context window (e.g., 2000 tokens)

**Deliverables**:
- Context assembly logic
- Sample contexts for queries

### 4.3 Generation Component
**Objective**: Generate factual responses using LLM.

**LLM Selection**:
- **Groq API** (Primary - Fast inference, cost-effective)
  - Models: `llama-3.1-8b-instant` or `mixtral-8x7b-32768`
  - High throughput, low latency
  - Competitive pricing for production use
- Alternative: Llama 3 8B (local deployment if Groq unavailable)

**Prompt Engineering**:
```
You are a facts-only mutual fund FAQ assistant. Answer the user's question based ONLY on the provided context.

Context:
{retrieved_context}

Question: {user_query}

Requirements:
- Answer in maximum 3 sentences
- Include exactly one source link from the context
- No investment advice or recommendations
- No opinions or speculative content
- If information is not in context, politely refuse

Response format:
[Answer]

Source: [URL]
Last updated from sources: [date]
```

**Deliverables**:
- Generation module code
- Prompt templates

### 4.4 Refusal Handling
**Objective**: Implement graceful refusal for non-factual queries.

**Detection Logic**:
- Keyword detection (should, better, recommend, advice)
- Intent classification (advisory vs factual)
- Query type categorization

**Refusal Response Template**:
```
I can only provide factual information about mutual funds and cannot offer investment advice or recommendations. 

For educational resources on mutual fund investing, please visit: [AMFI/SEBI educational link]
```

**Deliverables**:
- Refusal detection logic
- Refusal response templates

---

## Phase 5: Query Processing & Response Generation

### 5.1 Query Preprocessing
**Objective**: Clean and normalize user queries.

**Activities**:
- Lowercase conversion
- Remove special characters
- Expand abbreviations (SIP → Systematic Investment Plan)
- Spell correction
- Query classification (factual vs advisory)

**Deliverables**:
- Query preprocessing pipeline
- Classification model/rules

### 5.2 End-to-End RAG Pipeline
**Objective**: Integrate all components into unified pipeline.

**Pipeline Flow**:
1. Receive user query
2. Preprocess query
3. Classify query type (factual/advisory)
4. If advisory → return refusal
5. If factual → retrieve relevant chunks
6. Assemble context
7. Generate response
8. Format response with source and date
9. Return to user

**Deliverables**:
- Integrated RAG pipeline
- Pipeline documentation

### 5.3 Response Formatting
**Objective**: Ensure consistent response format.

**Format Requirements**:
- Maximum 3 sentences for answer
- Exactly one source link
- Footer with last updated date
- Clear separation of answer and metadata

**Deliverables**:
- Response formatter module
- Format validation tests

---

## Phase 6: User Interface Development

### 6.1 UI Design
**Objective**: Create minimal, user-friendly interface.

**Components**:
- Welcome message explaining system purpose
- Three example questions (clickable)
- Query input field
- Submit button
- Response display area
- Visible disclaimer: "Facts-only. No investment advice."

**Design Principles**:
- Clean and simple layout
- Mobile-responsive
- Clear visual hierarchy
- Accessible design

**Deliverables**:
- UI mockups/wireframes
- Design specification

### 6.2 Frontend Implementation
**Objective**: Build the user interface.

**Technology Stack Options**:
- **Streamlit** (Python, rapid prototyping)
- **Gradio** (Python, simple UI)
- **React + FastAPI** (production-grade)
- **Flask + HTML/CSS/JS** (lightweight)

**Features**:
- Query input with example buttons
- Response display with source links
- Loading states
- Error handling
- Disclaimer banner

**Deliverables**:
- Frontend application code
- UI styling

### 6.3 Backend API
**Objective**: Expose RAG pipeline as API endpoints.

**Endpoints**:
- `POST /query` - Submit question
- `GET /health` - Health check
- `GET /schemes` - List available schemes

**API Specification**:
```
POST /query
Request: {"query": "What is the expense ratio of Axis Flexi Cap Fund?"}
Response: {
  "answer": "The expense ratio of Axis Flexi Cap Fund Direct Growth is 1.05%.",
  "source": "https://axismf.com/factsheet/...",
  "last_updated": "2024-05-08"
}
```

**Deliverables**:
- API implementation
- API documentation

### 6.4 UI-Backend Integration
**Objective**: Connect frontend to backend API.

**Activities**:
- Configure API endpoints in frontend
- Implement error handling
- Add loading indicators
- Test end-to-end flow

**Deliverables**:
- Integrated application
- Integration tests

---

## Phase 7: Testing & Validation

### 7.1 Unit Testing
**Objective**: Test individual components.

**Test Coverage**:
- Document extraction tests
- Chunking logic tests
- Embedding generation tests
- Retrieval accuracy tests
- Response generation tests
- Refusal detection tests

**Deliverables**:
- Unit test suite
- Test coverage report

### 7.2 Integration Testing
**Objective**: Test component interactions.

**Test Scenarios**:
- End-to-end query flow
- Error handling for missing data
- API response validation
- UI-backend communication

**Deliverables**:
- Integration test suite
- Test results

### 7.3 Quality Assurance Testing
**Objective**: Validate against requirements.

**Test Cases**:
- Factual query accuracy (expense ratio, exit load, etc.)
- Source citation presence and validity
- Response length constraints (≤3 sentences)
- Refusal handling for advisory queries
- Data privacy compliance (no PII collection)
- Source authenticity (official sources only)

**Deliverables**:
- QA test report
- Bug fixes

### 7.4 User Acceptance Testing
**Objective**: Validate with target users.

**Activities**:
- Test with retail investors
- Test with customer support teams
- Collect feedback on:
  - Response accuracy
  - UI usability
  - Response clarity
  - Overall satisfaction

**Deliverables**:
- UAT report
- Feedback analysis

---

## Phase 8: Deployment & Monitoring

### 8.1 Deployment Strategy
**Objective**: Deploy application to production.

**Deployment Options**:
- **Cloud Platforms**:
  - AWS (EC2, Lambda, RDS)
  - Google Cloud (Cloud Run, Cloud SQL)
  - Azure (App Service, Azure SQL)
  
- **PaaS Options**:
  - Render
  - Railway
  - Heroku
  
- **Self-hosted**:
  - Docker containers
  - Kubernetes

**Deliverables**:
- Deployment configuration
- Production environment

### 8.2 Monitoring & Logging
**Objective**: Set up monitoring for system health.

**Monitoring Components**:
- Application performance monitoring
- API response times
- Error tracking
- User query analytics
- Retrieval quality metrics

**Logging**:
- Query logs (anonymized, no PII)
- Response logs
- Error logs
- System health logs

**Deliverables**:
- Monitoring dashboard
- Logging configuration

### 8.3 Maintenance & Updates
**Objective**: Plan for ongoing maintenance and automated data updates.

**Activities**:
- Regular data refresh (factsheet updates)
- Source URL validation
- Performance optimization
- Bug fixes and patches
- Feature enhancements based on feedback

**Automated Data Refresh (GitHub Actions)**:
- **Workflow**: `.github/workflows/data-refresh.yml`
- **Schedule**: Daily at 6:00 AM IST (cron: `0 1 * * *` UTC)
- **Process**:
  1. Trigger scheduled workflow
  2. Run Phase 1 extraction pipeline (scrape latest data from 5 URLs)
  3. Run Phase 2 chunking pipeline (process and validate new data)
  4. Run Phase 3 indexing pipeline (update vector database)
  5. Validate data quality
  6. Commit updated data to repository (optional)
  7. Send notification on success/failure

**GitHub Actions Workflow Example**:
```yaml
name: Daily Data Refresh
on:
  schedule:
    - cron: '0 1 * * *'  # Daily at 6:30 AM IST
  workflow_dispatch:  # Allow manual trigger

jobs:
  refresh-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run Phase 1 - Extract Data
        run: python src/pipeline.py
      - name: Run Phase 2 - Process Chunks
        run: python src/chunking_pipeline.py
      - name: Run Phase 3 - Index Vectors
        run: python src/indexing_pipeline.py
      - name: Commit updated data
        run: |
          git config user.name "Data Bot"
          git config user.email "bot@example.com"
          git add data/
          git commit -m "Daily data refresh: $(date)" || echo "No changes"
          git push
```

**Deliverables**:
- Maintenance schedule
- Update procedures
- GitHub Actions workflow files
- Data refresh automation documentation

### 8.4 Documentation
**Objective**: Create comprehensive documentation.

**Documentation Types**:
- **README**: Setup instructions, architecture overview
- **API Documentation**: Endpoint specifications
- **User Guide**: How to use the system
- **Developer Guide**: Code structure and contribution guidelines
- **Known Limitations**: Document constraints and edge cases
- **Disclaimer**: Legal compliance text

**Deliverables**:
- Complete documentation suite
- Contributor guidelines

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│  (Streamlit/React)                                          │
│  - Welcome message                                          │
│  - Example questions                                        │
│  - Query input                                              │
│  - Response display                                         │
│  - Disclaimer banner                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP API
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend API (FastAPI/Flask)               │
│  - Query preprocessing                                      │
│  - Intent classification                                    │
│  - Response formatting                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    RAG Pipeline                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Query      │  │  Retrieval   │  │  Generation  │     │
│  │ Embedder     │→ │  Engine      │→ │  Module      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                 │              │
│         ▼                 ▼                 ▼              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Refusal    │  │  Context     │  │   Response   │     │
│  │  Detector    │  │  Assembler   │  │  Formatter   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 Vector Database                              │
│  (ChromaDB/Pinecone/Weaviate)                               │
│  - Embedded chunks                                          │
│  - Metadata (source, scheme, date)                          │
│  - Similarity search index                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Document Processing Pipeline                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Web        │  │   PDF        │  │  Content     │     │
│  │   Scraper    │  │   Parser     │  │  Normalizer  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                 │              │
│         └─────────────────┴─────────────────┘              │
│                           ▼                                 │
│                  ┌──────────────┐                          │
│                  │   Chunking   │                          │
│                  │   Strategy   │                          │
│                  └──────────────┘                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Data Sources                               │
│  - 5 Groww scheme URLs:                                     │
│    • Axis Silver FoF Direct Growth                          │
│    • Axis Small Cap Fund Direct Growth                      │
│    • Axis Flexi Cap Fund Direct Growth                      │
│    • Axis Gold Fund Direct Growth                           │
│    • Axis Nifty India Defence Index Fund Direct Growth       │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack Recommendations

### Core Components
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Backend | Python (FastAPI) | Widely used, great for ML/AI |
| Frontend | Streamlit | Rapid development, Python-native |
| Vector DB | ChromaDB | Local, lightweight, easy setup |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) | Local deployment, no API costs |
| LLM | Groq API (llama-3.1-8b-instant) | Fast inference, cost-effective |
| Document Processing | PyPDF2, BeautifulSoup | Reliable for PDF/HTML parsing |

### Alternative Options
| Component | Alternative | Use Case |
|-----------|-------------|----------|
| Frontend | React + Next.js | Production-grade web app |
| Vector DB | Pinecone | Managed, scalable deployment |
| Embeddings | Sentence Transformers | Local deployment, no API costs |
| LLM | Llama 3 8B | Open source, local inference |

---

## Success Metrics

### Technical Metrics
- Retrieval accuracy: >90% relevant chunks in top-3
- Response generation: <2 seconds per query
- Source citation accuracy: 100% (all responses have valid source)
- Refusal detection: >95% accuracy for advisory queries

### User Experience Metrics
- Query success rate: >90% factual queries answered
- Response clarity: User satisfaction >4/5
- UI usability: Task completion rate >95%

### Compliance Metrics
- 100% adherence to facts-only constraint
- 100% source citation presence
- 0% investment advice provided
- 0% PII collection or storage

---

## Risk Mitigation

### Technical Risks
| Risk | Mitigation |
|------|------------|
| Source URL changes | Regular URL validation, fallback sources |
| Embedding model drift | Periodic re-evaluation of model performance |
| API rate limits | Implement caching, rate limit handling |
| Data freshness | Scheduled data refresh pipeline |

### Compliance Risks
| Risk | Mitigation |
|------|------------|
| Accidental advice | Strict prompt engineering, refusal detection |
| Source authenticity | Whitelist official sources only |
| Data privacy | No PII collection, anonymized logging |

### Operational Risks
| Risk | Mitigation |
|------|------------|
| Service downtime | Health checks, auto-restart mechanisms |
| Cost overruns | Monitor API usage, implement cost alerts |
| Scalability issues | Load testing, horizontal scaling plan |

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Data Collection | 1-2 weeks | None |
| Phase 2: Document Processing | 1-2 weeks | Phase 1 |
| Phase 3: Vector Database | 1 week | Phase 2 |
| Phase 4: RAG Pipeline | 2-3 weeks | Phase 3 |
| Phase 5: Query Processing | 1 week | Phase 4 |
| Phase 6: UI Development | 1-2 weeks | Phase 5 |
| Phase 7: Testing | 1-2 weeks | Phase 6 |
| Phase 8: Deployment | 1 week | Phase 7 |

**Total Estimated Duration**: 8-13 weeks

---

## Conclusion

This phase-wise architecture provides a comprehensive roadmap for building a compliant, accurate, and user-friendly Mutual Fund FAQ Assistant. The system prioritizes factual accuracy and regulatory compliance over advanced features, ensuring users receive trustworthy, source-backed information without any investment advice or recommendations.

The modular design allows for iterative development and testing at each phase, with clear deliverables and success criteria to track progress. The technology stack balances ease of development with production readiness, while the risk mitigation strategies address technical, compliance, and operational challenges.
