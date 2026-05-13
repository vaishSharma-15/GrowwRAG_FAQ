# Edge Cases: Mutual Fund FAQ Assistant (Facts-Only Q&A)

## Overview
This document outlines potential edge cases, challenges, and failure scenarios for all phases of the Mutual Fund FAQ Assistant project, along with mitigation strategies.

---

# Phase 1: Data Collection & Corpus Preparation

## 1.1 AMC and Scheme Selection

### Edge Cases

#### EC1.1.1: AMC Website Unavailable
**Scenario**: Axis Mutual Fund website is temporarily down or experiencing high latency.
- **Impact**: Cannot access scheme information
- **Mitigation**: 
  - Implement retry logic with exponential backoff
  - Use cached data if available
  - Have alternative data sources as backup (though not primary)

#### EC1.1.2: Scheme Information Incomplete
**Scenario**: One or more of the 5 selected schemes have incomplete or missing information on the Groww URLs.
- **Impact**: Limited data available for certain schemes
- **Mitigation**:
  - Document which fields are missing
  - Proceed with available data
  - Clearly mark incomplete data in the corpus

#### EC1.1.3: Scheme Category Mismatch
**Scenario**: The actual category of a scheme differs from expected categorization (e.g., a fund labeled as "flexi-cap" behaving differently).
- **Impact**: Incorrect metadata and filtering
- **Mitigation**:
  - Validate scheme categories against AMFI classification
  - Cross-reference with multiple sources
  - Document any discrepancies

#### EC1.1.4: Duplicate Scheme Detection
**Scenario**: Similar or duplicate schemes with slight variations (e.g., Direct vs Regular plan).
- **Impact**: Data redundancy and confusion
- **Mitigation**:
  - Use unique scheme codes (ISIN/PAN)
  - Clearly distinguish between plan types
  - Only include Direct Growth plans as specified

## 1.2 Source URL Collection

### Edge Cases

#### EC1.2.1: URL Accessibility Issues
**Scenario**: One or more of the 5 Groww URLs return 404, 403, or other error codes.
- **Impact**: Cannot extract data from affected URLs
- **Mitigation**:
  - Implement comprehensive URL validation before extraction
  - Log all accessibility issues
  - Alert if critical URLs are unavailable

#### EC1.2.2: URL Structure Changes
**Scenario**: Groww changes URL structure or redirects to different pages.
- **Impact**: Scraping logic fails
- **Mitigation**:
  - Monitor URL patterns
  - Implement flexible URL matching
  - Handle redirects gracefully

#### EC1.2.3: Dynamic Content Loading
**Scenario**: Groww pages load content dynamically via JavaScript that isn't captured by simple HTTP requests.
- **Impact**: Scraped content is incomplete or empty
- **Mitigation**:
  - Use headless browser (Selenium/Playwright) for dynamic content
  - Identify API endpoints if available
  - Implement wait logic for content loading

#### EC1.2.4: Rate Limiting
**Scenario**: Groww implements rate limiting, blocking scraping attempts.
- **Impact**: Incomplete data extraction
- **Mitigation**:
  - Implement rate limiting in scraper
  - Add delays between requests
  - Use rotating user agents if necessary
  - Respect robots.txt

#### EC1.2.5: Anti-Scraping Measures
**Scenario**: Groww implements CAPTCHA or other anti-bot measures.
- **Impact**: Scraping blocked
- **Mitigation**:
  - Monitor for CAPTCHA challenges
  - Implement CAPTCHA solving if legal and necessary
  - Consider manual data extraction as fallback

## 1.3 Data Extraction Strategy

### Edge Cases

#### EC1.3.1: Inconsistent HTML Structure
**Scenario**: The 5 URLs have different HTML structures or layouts.
- **Impact**: Scraping logic needs to handle multiple templates
- **Mitigation**:
  - Build flexible scrapers with multiple selectors
  - Use CSS selectors that are robust to layout changes
  - Implement schema validation for extracted data

#### EC1.3.2: Missing Critical Fields
**Scenario**: Critical fields (expense ratio, exit load, etc.) are missing from one or more URLs.
- **Impact**: Incomplete corpus, inability to answer certain queries
- **Mitigation**:
  - Document missing fields per scheme
  - Implement graceful handling in RAG pipeline
  - Provide clear error messages when data is unavailable

#### EC1.3.3: Data Format Inconsistencies
**Scenario**: Numerical data formatted differently across URLs (e.g., "1.05%", "1.05 percent", "105 basis points").
- **Impact**: Data parsing errors, incorrect values
- **Mitigation**:
  - Implement robust data normalization
  - Handle multiple format variations
  - Store both raw and normalized values

#### EC1.3.4: Special Characters and Encoding Issues
**Scenario**: Text contains special characters, emojis, or non-UTF-8 encoding.
- **Impact**: Text corruption, embedding generation errors
- **Mitigation**:
  - Implement proper encoding handling
  - Clean special characters while preserving meaning
  - Test embedding generation with cleaned text

#### EC1.3.5: Temporal Data Changes
**Scenario**: Data on URLs changes between extraction and indexing (e.g., NAV updates daily).
- **Impact**: Stale data in corpus
- **Mitigation**:
  - Implement timestamp tracking for each extraction
  - Schedule regular data refresh
  - Display "Last updated" information in responses

#### EC1.3.6: Empty or Minimal Content
**Scenario**: A URL contains minimal or placeholder content.
- **Impact**: Insufficient data for meaningful retrieval
- **Mitigation**:
  - Detect and flag minimal content
  - Set minimum content thresholds
  - Exclude from corpus if insufficient data

## Cross-Phase Edge Cases

#### EC1.CP1: Single Source Dependency
**Scenario**: Relying on only 5 URLs from a single platform (Groww).
- **Impact**: If Groww changes or becomes unavailable, entire system fails
- **Mitigation**:
  - Document this dependency clearly
  - Implement robust error handling
  - Have manual fallback procedures
  - Consider adding backup sources in future iterations

#### EC1.CP2: Data Freshness vs. Stability
**Scenario**: Balancing the need for fresh data (daily NAV updates) with stable embeddings.
- **Impact**: Frequent re-indexing required vs. stale data
- **Mitigation**:
  - Separate static data (scheme details) from dynamic data (NAV)
  - Implement incremental updates
  - Cache embeddings for unchanged content

---

# Phase 2: Document Ingestion & Processing

## 2.1 Content Extraction Pipeline

### Edge Cases

#### EC2.1.1: Web Scraper Timeout
**Scenario**: Scraper hangs or times out waiting for page load.
- **Impact**: Incomplete extraction, pipeline stall
- **Mitigation**:
  - Implement configurable timeouts
  - Use async scraping with concurrent requests
  - Add timeout per page and overall timeout

#### EC2.1.2: JavaScript Rendering Issues
**Scenario**: Content requires JavaScript execution but scraper doesn't execute JS.
- **Impact**: Extracted content is empty or incomplete
- **Mitigation**:
  - Use headless browser (Selenium/Playwright/Puppeteer)
  - Wait for specific DOM elements before extraction
  - Implement fallback to API endpoints if available

#### EC2.1.3: Anti-Bot Detection
**Scenario**: Groww detects scraper behavior and blocks requests.
- **Impact**: Scraping blocked, IP banned temporarily
- **Mitigation**:
  - Use realistic user agents
  - Implement request throttling
  - Rotate user agents if necessary
  - Respect robots.txt and rate limits

#### EC2.1.4: Session/Cookie Requirements
**Scenario**: Pages require session cookies or authentication.
- **Impact**: Cannot access content
- **Mitigation**:
  - Implement session management
  - Handle cookie persistence
  - Test authentication requirements upfront

#### EC2.1.5: Pagination and Infinite Scroll
**Scenario**: Content loaded via pagination or infinite scroll.
- **Impact**: Only first page/content extracted
- **Mitigation**:
  - Detect pagination patterns
  - Implement scroll handling for infinite scroll
  - Extract all paginated content

#### EC2.1.6: Malformed HTML
**Scenario**: HTML is malformed or doesn't follow standards.
- **Impact**: Parser fails or extracts incorrect data
- **Mitigation**:
  - Use robust HTML parsers (BeautifulSoup with lxml)
  - Implement error recovery
  - Log parsing warnings

#### EC2.1.7: Content Normalization Failures
**Scenario**: Text normalization fails due to unexpected characters or formats.
- **Impact**: Corrupted text, downstream processing errors
- **Mitigation**:
  - Implement comprehensive character encoding handling
  - Use Unicode normalization (NFC/NFD)
  - Log normalization failures with context

## 2.2 Document Chunking Strategy

### Edge Cases

#### EC2.2.1: Optimal Chunk Size Mismatch
**Scenario**: Chunk size (500-1000 tokens) is too small or too large for optimal retrieval.
- **Impact**: Poor retrieval accuracy, inefficient context use
- **Mitigation**:
  - Experiment with different chunk sizes
  - A/B test retrieval performance
  - Allow per-scheme chunk size tuning

#### EC2.2.2: Context Break at Sentence Boundary
**Scenario**: Chunk splits mid-sentence or mid-concept.
- **Impact**: Incomplete information, confusing retrieval
- **Mitigation**:
  - Implement sentence boundary detection
  - Prefer splitting at natural breaks (paragraphs, sections)
  - Use semantic chunking when possible

#### EC2.2.3: Overlap Insufficient
**Scenario**: Overlap (100-200 tokens) is insufficient to capture context.
- **Impact**: Important information split across chunks
- **Mitigation**:
  - Increase overlap for complex topics
  - Implement variable overlap based on content density
  - Test retrieval with different overlap values

#### EC2.2.4: Too Much Overlap
**Scenario**: Excessive overlap causes redundancy and bloat.
- **Impact**: Larger vector database, slower retrieval
- **Mitigation**:
  - Monitor overlap efficiency
  - Deduplicate highly similar chunks
  - Adjust overlap based on content type

#### EC2.2.5: Metadata Loss
**Scenario**: Critical metadata (source URL, scheme name) not attached to chunks.
- **Impact**: Cannot attribute responses to sources
- **Mitigation**:
  - Validate metadata attachment during chunking
  - Implement metadata schema validation
  - Test retrieval with metadata filtering

#### EC2.2.6: Small Content Chunks
**Scenario**: Content too small to create meaningful chunks (e.g., short FAQ answers).
- **Impact**: Chunks lack context, poor retrieval
- **Mitigation**:
  - Implement minimum chunk size threshold
  - Combine small chunks with related content
  - Flag small chunks for manual review

#### EC2.2.7: Large Content Chunks
**Scenario**: Single document too large (e.g., comprehensive factsheet).
- **Impact**: Chunking produces many similar chunks, redundancy
- **Mitigation**:
  - Implement section-based chunking for large documents
  - Use hierarchical chunking (document → section → paragraph)
  - Deduplicate similar chunks

#### EC2.2.8: Multilingual Content
**Scenario**: Content contains non-English text or mixed languages.
- **Impact**: Embedding model may not handle well, retrieval issues
- **Mitigation**:
  - Detect language before embedding
  - Use multilingual embedding models if needed
  - Translate or filter non-English content

## 2.3 Data Validation & Quality Control

### Edge Cases

#### EC2.3.1: Numerical Data Validation Failures
**Scenario**: Numerical data (expense ratios, exit loads) fails validation checks.
- **Impact**: Invalid data in corpus, incorrect responses
- **Mitigation**:
  - Implement range validation (e.g., expense ratio 0-5%)
  - Cross-reference with expected ranges
  - Flag and quarantine invalid data
  - Manual review of flagged data

#### EC2.3.2: Date Format Inconsistencies
**Scenario**: Dates in various formats (DD/MM/YYYY, MM-DD-YYYY, "Jan 2024").
- **Impact**: Date parsing errors, incorrect "last updated" information
- **Mitigation**:
  - Implement flexible date parsing
  - Normalize all dates to ISO format
  - Handle ambiguous dates with context

#### EC2.3.3: Cross-Reference Discrepancies
**Scenario**: Same metric has different values across sources or sections.
- **Impact**: Conflicting information in corpus
- **Mitigation**:
  - Implement conflict detection
  - Use most recent or most authoritative source
  - Document discrepancies in metadata
  - Prefer scheme-specific data over general data

#### EC2.3.4: Broken Internal Links
**Scenario**: Extracted content contains broken or relative links.
- **Impact**: Source citations may fail
- **Mitigation**:
  - Convert relative links to absolute
  - Validate all extracted URLs
  - Store original URLs in metadata

#### EC2.3.5: Data Freshness Issues
**Scenario**: Data is outdated (e.g., old NAV values, discontinued scheme).
- **Impact**: Stale information provided to users
- **Mitigation**:
  - Implement timestamp validation
  - Set maximum age threshold for data
  - Flag outdated data for refresh
  - Display data age in responses

#### EC2.3.6: Duplicate Content Across Schemes
**Scenario**: Generic content (e.g., AMC disclaimers) appears in multiple schemes.
- **Impact**: Redundant chunks, inefficient retrieval
- **Mitigation**:
  - Detect and deduplicate content
  - Store common content separately
  - Reference common content instead of duplicating

#### EC2.3.7: Missing Critical Information
**Scenario**: Critical information (risk level, benchmark) missing for a scheme.
- **Impact**: Cannot answer common queries
- **Mitigation**:
  - Implement completeness checks
  - Flag missing critical fields
  - Provide graceful handling in RAG pipeline
  - Document limitations

#### EC2.3.8: Data Type Mismatches
**Scenario**: Expected numeric field contains text, or vice versa.
- **Impact**: Parsing errors, type conversion failures
- **Mitigation**:
  - Implement type validation
  - Handle type conversions gracefully
  - Log type mismatches for review

## Cross-Phase Edge Cases

#### EC2.CP1: Extraction Quality vs. Speed
**Scenario**: Balancing thorough extraction with processing speed.
- **Impact**: Trade-off between data completeness and pipeline efficiency
- **Mitigation**:
  - Implement incremental extraction
  - Prioritize critical fields first
  - Allow parallel extraction for non-dependent fields

#### EC2.CP2: Schema Evolution
**Scenario**: Groww page structure changes over time.
- **Impact**: Scraping logic becomes outdated
- **Mitigation**:
  - Monitor extraction success rates
  - Implement schema versioning
  - Build flexible scrapers with multiple selectors
  - Alert on significant extraction failures

#### EC2.CP3: Content Volume Management
**Scenario**: 5 URLs produce unexpectedly large or small content volumes.
- **Impact**: Storage issues or insufficient corpus
- **Mitigation**:
  - Monitor content size per URL
  - Implement content size limits
  - Adjust chunking strategy based on volume

---

# Phase 3: Vector Database Setup

## 3.1 Embedding Model Selection

### Edge Cases

#### EC3.1.1: Embedding Model API Rate Limits
**Scenario**: Embedding API (e.g., OpenAI) hits rate limits during bulk embedding generation.
- **Impact**: Slow or failed embedding generation
- **Mitigation**:
  - Implement rate limit handling with exponential backoff
  - Use batch embedding with optimal batch size
  - Cache embeddings to avoid re-generation
  - Consider local embedding models as backup

#### EC3.1.2: Embedding Model Unavailable
**Scenario**: Embedding API service is down or experiencing outages.
- **Impact**: Cannot generate embeddings, indexing blocked
- **Mitigation**:
  - Implement retry logic with circuit breaker pattern
  - Have backup embedding model (local)
  - Queue embedding requests for later processing
  - Monitor API status

#### EC3.1.3: Embedding Dimension Mismatch
**Scenario**: Selected embedding model produces different dimensions than expected.
- **Impact**: Vector database schema incompatibility
- **Mitigation**:
  - Validate embedding dimensions before indexing
  - Document model specifications
  - Re-index if model changes
  - Use dimension-agnostic vector DB if possible

#### EC3.1.4: Poor Domain Performance
**Scenario**: Embedding model performs poorly on financial domain text.
- **Impact**: Poor retrieval accuracy, irrelevant results
- **Mitigation**:
  - Benchmark multiple models on sample financial text
  - Fine-tune embedding model if using local model
  - Use domain-specific models if available
  - Implement re-ranking to improve relevance

#### EC3.1.5: Token Limit Exceeded
**Scenario**: Text chunk exceeds embedding model's token limit.
- **Impact**: Embedding generation fails or truncates
- **Mitigation**:
  - Implement token counting before embedding
  - Split oversized chunks further
  - Use models with higher token limits
  - Log and flag oversized chunks

#### EC3.1.6: Embedding Cost Overruns
**Scenario**: Embedding API costs exceed budget due to large corpus.
- **Impact**: Project budget issues
- **Mitigation**:
  - Monitor embedding costs in real-time
  - Implement cost alerts
  - Use cost-effective models (e.g., text-embedding-3-small)
  - Consider local models for cost savings

#### EC3.1.7: Multilingual Content Handling
**Scenario**: Content contains non-English text that embedding model doesn't handle well.
- **Impact**: Poor embeddings for multilingual content
- **Mitigation**:
  - Detect language before embedding
  - Use multilingual embedding models
  - Filter or translate non-English content
  - Separate embeddings by language

## 3.2 Vector Database Configuration

### Edge Cases

#### EC3.2.1: Vector Database Connection Failures
**Scenario**: Cannot connect to vector database (ChromaDB, Pinecone, etc.).
- **Impact**: Cannot store or retrieve embeddings
- **Mitigation**:
  - Implement connection retry logic
  - Use connection pooling
  - Have fallback database option
  - Monitor database health

#### EC3.2.2: Insufficient Memory/Disk Space
**Scenario**: Vector database runs out of memory or disk space during indexing.
- **Impact**: Indexing fails, partial corpus indexed
- **Mitigation**:
  - Monitor memory and disk usage
  - Implement batch indexing with size limits
  - Use disk-based vector databases if memory constrained
  - Prune or compress embeddings if needed

#### EC3.2.3: Index Build Timeout
**Scenario**: Vector index build takes too long or times out.
- **Impact**: Indexing incomplete, system unusable
- **Mitigation**:
  - Use approximate indexes (HNSW) for faster builds
  - Build index incrementally
  - Tune index parameters (ef_construction, M)
  - Monitor build progress

#### EC3.2.4: Metadata Schema Changes
**Scenario**: Need to add or modify metadata fields after initial indexing.
- **Impact**: Schema migration required, potential data loss
- **Mitigation**:
  - Use flexible schema (JSON metadata)
  - Implement schema versioning
  - Plan for schema evolution upfront
  - Test schema changes on subset first

#### EC3.2.5: Vector Database Service Limits
**Scenario**: Managed vector database (Pinecone) hits service limits (dimensions, vectors).
- **Impact**: Cannot index all chunks or upgrade required
- **Mitigation**:
  - Monitor usage against limits
  - Optimize chunking to reduce vector count
  - Plan for tier upgrades
  - Consider self-hosted alternatives

#### EC3.2.6: Concurrent Access Issues
**Scenario**: Multiple processes try to access/modify database simultaneously.
- **Impact**: Race conditions, data corruption
- **Mitigation**:
  - Implement proper locking mechanisms
  - Use transactional operations
  - Design for single-writer, multiple-readers
  - Test concurrent access patterns

#### EC3.2.7: Backup and Recovery Failures
**Scenario**: Vector database backup fails or cannot be restored.
- **Impact**: Data loss, inability to recover from failures
- **Mitigation**:
  - Implement regular automated backups
  - Test backup restoration procedures
  - Store backups in multiple locations
  - Document recovery procedures

## 3.3 Corpus Indexing

### Edge Cases

#### EC3.3.1: Batch Size Too Large
**Scenario**: Embedding or indexing batch size too large for API or memory.
- **Impact**: API errors, memory issues
- **Mitigation**:
  - Implement dynamic batch sizing
  - Monitor memory usage during batching
  - Use optimal batch size (test empirically)
  - Implement graceful batch size reduction

#### EC3.3.2: Embedding Generation Failures
**Scenario**: Individual chunks fail embedding generation (invalid text, API errors).
- **Impact**: Partial corpus indexed, missing data
- **Mitigation**:
  - Implement per-chunk error handling
  - Log failed chunks for review
  - Retry failed chunks with smaller batches
  - Continue indexing despite individual failures

#### EC3.3.3: Duplicate Vectors
**Scenario**: Duplicate or near-duplicate chunks create duplicate vectors.
- **Impact**: Wasted storage, retrieval redundancy
- **Mitigation**:
  - Detect duplicates before embedding
  - Use deduplication during chunking
  - Implement vector deduplication
  - Monitor duplicate rates

#### EC3.3.4: Metadata Attachment Failures
**Scenario**: Metadata fails to attach to vectors during indexing.
- **Impact**: Cannot filter or attribute results
- **Mitigation**:
  - Validate metadata before indexing
  - Implement metadata schema validation
  - Test metadata retrieval after indexing
  - Log metadata attachment failures

#### EC3.3.5: Index Quality Degradation
**Scenario**: Vector index quality degrades over time or with poor parameters.
- **Impact**: Retrieval accuracy decreases
- **Mitigation**:
  - Monitor retrieval metrics over time
  - Re-index with optimized parameters
  - Use index maintenance operations
  - A/B test index configurations

#### EC3.3.6: Slow Indexing Performance
**Scenario**: Indexing takes too long for practical use.
- **Impact**: Long deployment cycles, difficulty with updates
- **Mitigation**:
  - Implement parallel embedding generation
  - Use batch operations
  - Optimize index parameters
  - Consider incremental indexing

#### EC3.3.7: Empty or Invalid Chunks
**Scenario**: Chunks with empty or invalid content slip through to indexing.
- **Impact**: Wasted vectors, retrieval noise
- **Mitigation**:
  - Validate chunk content before embedding
  - Filter empty or too-short chunks
  - Implement content quality checks
  - Log and review invalid chunks

#### EC3.3.8: Index Corruption
**Scenario**: Vector index becomes corrupted during or after indexing.
- **Impact**: Retrieval fails or returns incorrect results
- **Mitigation**:
  - Implement index integrity checks
  - Use database transaction logs
  - Have backup/restore procedures
  - Monitor index health metrics

## Cross-Phase Edge Cases

#### EC3.CP1: Model-Database Compatibility
**Scenario**: Embedding model changes but vector database expects old dimensions.
- **Impact**: Incompatibility, re-indexing required
- **Mitigation**:
  - Document model-database dependencies
  - Version embeddings and index
  - Plan for model migration
  - Test model changes in staging

#### EC3.CP2: Scaling Challenges
**Scenario**: Corpus grows beyond initial vector database capacity.
- **Impact**: Performance degradation, storage limits
- **Mitigation**:
  - Monitor growth trends
  - Plan for scaling (horizontal/vertical)
  - Implement sharding if needed
  - Use scalable database options

#### EC3.CP3: Cost Management
**Scenario**: Vector database costs (especially managed services) grow with corpus size.
- **Impact**: Budget overruns
- **Mitigation**:
  - Monitor costs regularly
  - Implement cost optimization (pruning, compression)
  - Set budget alerts
  - Consider self-hosted alternatives

---

# Phase 4: RAG Pipeline Development

## 4.1 Retrieval Component

### Edge Cases

#### EC4.1.1: No Relevant Chunks Found
**Scenario**: Query returns no relevant chunks or empty results.
- **Impact**: Cannot answer user's question
- **Mitigation**:
  - Implement fallback to broader search
  - Return graceful "information not available" response
  - Log query for corpus improvement
  - Suggest related queries

#### EC4.1.2: Too Many Relevant Chunks
**Scenario**: Query returns too many relevant chunks, overwhelming context.
- **Impact**: Context window exceeded, poor generation
- **Mitigation**:
  - Implement relevance thresholding
  - Use re-ranking to prioritize
  - Limit to top-k chunks (k=3-5)
  - Implement diversity sampling

#### EC4.1.3: Low Relevance Results
**Scenario**: Retrieved chunks have low semantic similarity to query.
- **Impact**: Poor quality responses, hallucinations
- **Mitigation**:
  - Implement relevance score threshold
  - Use re-ranking with cross-encoder
  - Expand query with synonyms
  - Return "information not found" if below threshold

#### EC4.1.4: Metadata Filtering Failures
**Scenario**: Metadata filters (scheme, category) fail or return no results.
- **Impact**: Cannot narrow down to specific scheme
- **Mitigation**:
  - Validate metadata before filtering
  - Implement fallback without filters
  - Log filter failures
  - Test filter combinations

#### EC4.1.5: Query Embedding Failures
**Scenario**: Query embedding generation fails (API error, invalid text).
- **Impact**: Retrieval blocked
- **Mitigation**:
  - Implement retry logic
  - Use fallback embedding model
  - Log embedding failures
  - Return graceful error to user

#### EC4.1.6: Cross-Scheme Confusion
**Scenario**: Query about one scheme retrieves chunks from different scheme.
- **Impact**: Incorrect information provided
- **Mitigation**:
  - Implement strict scheme filtering
  - Add scheme name to context
  - Validate scheme mentions in response
  - Use metadata for disambiguation

#### EC4.1.7: Outdated Information Retrieved
**Scenario**: Retrieved chunks contain outdated information (old NAV, discontinued features).
- **Impact**: Incorrect responses to users
- **Mitigation**:
  - Use timestamp-based filtering
  - Prioritize recent chunks
  - Display "last updated" in response
  - Implement regular corpus refresh

#### EC4.1.8: Ambiguous Queries
**Scenario**: Query is ambiguous (e.g., "What is the expense ratio?" without specifying scheme).
- **Impact**: Cannot determine which scheme to query
- **Mitigation**:
  - Implement query clarification
  - Ask user to specify scheme
  - Provide information for all schemes
  - Suggest specific queries

## 4.2 Context Assembly

### Edge Cases

#### EC4.2.1: Context Window Exceeded
**Scenario**: Assembled context exceeds LLM's context window.
- **Impact**: Truncated context, incomplete information
- **Mitigation**:
  - Implement context length limiting
  - Prioritize most relevant chunks
  - Summarize chunks if needed
  - Use models with larger context windows

#### EC4.2.2: Chunk Overlap Redundancy
**Scenario**: Retrieved chunks have significant overlap, creating redundancy.
- **Impact**: Wasted context space, confusing context
- **Mitigation**:
  - Deduplicate overlapping chunks
  - Implement overlap detection
  - Merge similar chunks
  - Use diversity sampling

#### EC4.2.3: Context Incoherence
**Scenario**: Retrieved chunks don't form a coherent narrative.
- **Impact**: LLM struggles to generate coherent response
- **Mitigation**:
  - Re-rank for coherence
  - Add transition text between chunks
  - Limit to highly relevant chunks
  - Implement context ordering strategies

#### EC4.2.4: Missing Source Information
**Scenario**: Source URL or metadata missing from context.
- **Impact**: Cannot provide citation
- **Mitigation**:
  - Validate source information before assembly
  - Include source in chunk metadata
  - Fallback to scheme-level source
  - Log missing source cases

#### EC4.2.5: Conflicting Information in Context
**Scenario**: Retrieved chunks contain conflicting information.
- **Impact**: LLM may generate confused or incorrect response
- **Mitigation**:
  - Detect conflicts during assembly
  - Prioritize more recent or authoritative sources
  - Flag conflicts in prompt
  - Return disclaimer if conflict detected

#### EC4.2.6: Too Little Context
**Scenario**: Very limited context retrieved (1-2 short chunks).
- **Impact**: Insufficient information for complete answer
- **Mitigation**:
  - Implement minimum context threshold
  - Return partial answer with disclaimer
  - Expand retrieval if too little context
  - Suggest user ask more specific question

## 4.3 Generation Component

### Edge Cases

#### EC4.3.1: LLM API Rate Limits
**Scenario**: LLM API hits rate limits during high query volume.
- **Impact**: Slow or failed responses
- **Mitigation**:
  - Implement rate limit handling with backoff
  - Use request queuing
  - Cache common queries
  - Implement fallback model

#### EC4.3.2: LLM Service Unavailable
**Scenario**: LLM API service is down or experiencing outages.
- **Impact**: Cannot generate responses
- **Mitigation**:
  - Implement retry logic with circuit breaker
  - Use cached responses if available
  - Have backup LLM provider
  - Return graceful error message

#### EC4.3.3: Hallucinations
**Scenario**: LLM generates information not present in context.
- **Impact**: Incorrect or fabricated information
- **Mitigation**:
  - Strict prompt engineering (context-only)
  - Use temperature=0 for deterministic outputs
  - Implement post-generation fact-checking
  - Require source citations

#### EC4.3.4: Response Too Long
**Scenario**: Generated response exceeds 3-sentence limit.
- **Impact**: Violates requirements, poor user experience
- **Mitigation**:
  - Enforce sentence limit in prompt
  - Implement post-generation truncation
  - Use constrained decoding
  - Validate response length

#### EC4.3.5: Missing Source Citation
**Scenario**: LLM fails to include source link in response.
- **Impact**: Violates requirements, lack of transparency
- **Mitigation**:
  - Require citation in prompt
  - Implement post-generation validation
  - Auto-append source if missing
  - Format source explicitly

#### EC4.3.6: Investment Advice Generated
**Scenario**: LLM generates advice or recommendations despite instructions.
- **Impact**: Compliance violation, regulatory issues
- **Mitigation**:
  - Strict negative constraints in prompt
  - Post-generation keyword detection
  - Implement refusal override
  - Human review of edge cases

#### EC4.3.7: Generic or Vague Responses
**Scenario**: LLM generates generic responses not specific to query.
- **Impact**: Poor user experience, low value
- **Mitigation**:
  - Improve context quality
  - Use more specific prompts
  - Implement response quality validation
  - Re-rank retrieved chunks

#### EC4.3.8: Technical Jargon in Response
**Scenario**: LLM uses complex financial jargon users may not understand.
- **Impact**: User confusion, poor accessibility
- **Mitigation**:
  - Instruct for simple language in prompt
  - Implement jargon detection
  - Add glossary or explanations
  - Test with non-expert users

## 4.4 Refusal Handling

### Edge Cases

#### EC4.4.1: False Positive Refusal
**Scenario**: Legitimate factual query incorrectly classified as advisory.
- **Impact**: User cannot get valid information
- **Mitigation**:
  - Refine classification rules
  - Use ML classifier instead of keywords
  - Allow user override
  - Log false positives for improvement

#### EC4.4.2: False Negative Refusal
**Scenario**: Advisory query slips through and gets answered.
- **Impact**: Compliance violation
- **Mitigation**:
  - Strengthen detection rules
  - Use ensemble of detection methods
  - Post-generation validation
  - Human review of responses

#### EC4.4.3: Ambiguous Query Classification
**Scenario**: Query could be factual or advisory depending on interpretation.
- **Impact**: Inconsistent handling
- **Mitigation**:
  - Implement conservative classification (refuse if unsure)
  - Ask user for clarification
  - Provide partial factual information
  - Document edge cases

#### EC4.4.4: Refusal Response Too Generic
**Scenario**: Refusal response doesn't provide helpful guidance.
- **Impact**: Poor user experience
- **Mitigation**:
  - Provide specific educational links
  - Suggest rephrased queries
  - Explain what types of questions can be answered
  - Make refusal responses helpful

#### EC4.4.5: User Frustration with Refusals
**Scenario**: User repeatedly gets refusals and becomes frustrated.
- **Impact**: Poor user experience, system abandonment
- **Mitigation**:
  - Provide clear examples of answerable questions
  - Suggest alternative phrasings
  - Explain system limitations upfront
  - Collect feedback for improvement

## Cross-Phase Edge Cases

#### EC4.CP1: End-to-End Latency
**Scenario**: Total RAG pipeline latency too long for good UX.
- **Impact**: Poor user experience, abandonment
- **Mitigation**:
  - Optimize each component (retrieval, generation)
  - Implement caching for common queries
  - Use faster models where possible
  - Implement streaming responses

#### EC4.CP2: Quality vs. Speed Trade-off
**Scenario**: Higher quality retrieval/generation vs. faster response time.
- **Impact**: Need to balance user experience with accuracy
- **Mitigation**:
  - A/B test different configurations
  - Implement tiered quality (fast vs. accurate)
  - Let user choose quality level
  - Monitor both metrics

#### EC4.CP3: Cost Accumulation
**Scenario**: LLM API costs accumulate with high query volume.
- **Impact**: Budget overruns
- **Mitigation**:
  - Monitor costs in real-time
  - Implement query caching
  - Use cost-effective models
  - Set usage limits

---

# Phase 5: Query Processing & Response Generation

## 5.1 Query Preprocessing

### Edge Cases

#### EC5.1.1: Empty or Null Query
**Scenario**: User submits empty query or null input.
- **Impact**: Processing error, wasted API calls
- **Mitigation**:
  - Validate query before processing
  - Return helpful error message
  - Provide example questions
  - Log empty query attempts

#### EC5.1.2: Extremely Long Query
**Scenario**: User submits very long query (paragraphs of text).
- **Impact**: Token limit exceeded, slow processing
- **Mitigation**:
  - Implement query length limits
  - Truncate with warning
  - Summarize long queries
  - Ask user to rephrase

#### EC5.1.3: Special Characters and Emojis
**Scenario**: Query contains special characters, emojis, or unusual symbols.
- **Impact**: Embedding errors, processing failures
- **Mitigation**:
  - Clean special characters while preserving meaning
  - Handle emojis appropriately
  - Test embedding with cleaned queries
  - Log unusual character patterns

#### EC5.1.4: Non-English Query
**Scenario**: User submits query in non-English language.
- **Impact**: Poor embedding match, retrieval failure
- **Mitigation**:
  - Detect language before processing
  - Translate query if multilingual support not available
  - Return language not supported message
  - Consider multilingual models

#### EC5.1.5: Typos and Spelling Errors
**Scenario**: Query contains typos or spelling mistakes.
- **Impact**: Poor retrieval, irrelevant results
- **Mitigation**:
  - Implement spell correction
  - Use fuzzy matching
  - Suggest corrected query
  - Leverage embedding robustness to minor errors

#### EC5.1.6: Abbreviation Expansion Issues
**Scenario**: Query uses abbreviations that expand incorrectly (e.g., "SIP" could mean different things).
- **Impact**: Wrong interpretation, poor retrieval
- **Mitigation**:
  - Use context-aware expansion
  - Maintain domain-specific abbreviation dictionary
  - Keep original query for fallback
  - Test expansion accuracy

#### EC5.1.7: Query Classification Errors
**Scenario**: Query misclassified as advisory when factual, or vice versa.
- **Impact**: Incorrect handling, compliance issues
- **Mitigation**:
  - Use ensemble of classification methods
  - Implement confidence scoring
  - Allow manual review of edge cases
  - Refine classification rules based on feedback

#### EC5.1.8: Multiple Questions in One Query
**Scenario**: User asks multiple questions in a single query.
- **Impact**: Confusing response, incomplete answers
- **Mitigation**:
  - Detect multiple questions
  - Split into separate queries
  - Answer primary question first
  - Ask user to separate questions

## 5.2 End-to-End RAG Pipeline

### Edge Cases

#### EC5.2.1: Pipeline Component Failure
**Scenario**: One component in pipeline fails (embedding, retrieval, generation).
- **Impact**: Pipeline stalls, error propagates
- **Mitigation**:
  - Implement graceful degradation
  - Try alternative methods for failed component
  - Return partial results if possible
  - Log component failures

#### EC5.2.2: Pipeline Timeout
**Scenario**: Entire pipeline takes too long to complete.
- **Impact**: User abandonment, poor UX
- **Mitigation**:
  - Implement timeout per component
  - Use async processing
  - Return partial results on timeout
  - Optimize slow components

#### EC5.2.3: State Inconsistency
**Scenario**: Pipeline components have inconsistent state (e.g., cached vs fresh data).
- **Impact**: Inconsistent responses
- **Mitigation**:
  - Implement state validation
  - Use consistent data sources
  - Invalidate caches appropriately
  - Monitor state consistency

#### EC5.2.4: Concurrent Query Handling
**Scenario**: Multiple users submit queries simultaneously.
- **Impact**: Resource contention, slow responses
- **Mitigation**:
  - Implement request queuing
  - Use connection pooling
  - Scale horizontally if needed
  - Monitor concurrent request capacity

#### EC5.2.5: Pipeline Version Mismatch
**Scenario**: Different components use different versions (e.g., old embedding model, new LLM).
- **Impact**: Incompatibility, degraded performance
- **Mitigation**:
  - Version all components
  - Test compatibility before deployment
  - Use feature flags for gradual rollout
  - Document version dependencies

## 5.3 Response Formatting

### Edge Cases

#### EC5.3.1: Response Contains Markdown or HTML
**Scenario**: LLM generates response with markdown or HTML tags.
- **Impact**: Display issues, security concerns
- **Mitigation**:
  - Strip markdown/HTML before display
  - Sanitize output
  - Use plain text format
  - Test display with various formats

#### EC5.3.2: Source Link Malformed
**Scenario**: Generated source link is malformed or invalid.
- **Impact**: Broken citation, user confusion
- **Mitigation**:
  - Validate URL format
  - Use stored source URL from metadata
  - Fallback to scheme page if specific link invalid
  - Log malformed URLs

#### EC5.3.3: Date Format Inconsistencies
**Scenario**: "Last updated" date in various formats or invalid.
- **Impact**: User confusion, inconsistent display
- **Mitigation**:
  - Normalize all dates to standard format
  - Validate date before display
  - Use relative time (e.g., "2 days ago")
  - Handle missing dates gracefully

#### EC5.3.4: Response Truncation Issues
**Scenario**: Response truncated mid-sentence or mid-word.
- **Impact**: Incomplete information, poor UX
- **Mitigation**:
  - Implement sentence-level truncation
  - Adjust generation to fit limits
  - Use ellipsis for truncation
  - Avoid hard truncation

#### EC5.3.5: Missing Required Fields
**Scenario**: Response missing answer, source, or date.
- **Impact**: Incomplete response, requirement violation
- **Mitigation**:
  - Validate response format before returning
  - Auto-fill missing fields if possible
  - Return error if critical fields missing
  - Log validation failures

#### EC5.3.6: Response Encoding Issues
**Scenario**: Response contains characters that don't display correctly.
- **Impact**: Display corruption, user confusion
- **Mitigation**:
  - Use UTF-8 encoding consistently
  - Test with various character sets
  - Implement encoding validation
  - Handle encoding errors gracefully

#### EC5.3.7: Response Too Technical
**Scenario**: Response uses technical terms beyond user understanding.
- **Impact**: User confusion, poor accessibility
- **Mitigation**:
  - Simplify language in generation
  - Add explanations for technical terms
  - Provide glossary
  - Test with non-expert users

#### EC5.3.8: Response Contains Disclaimers in Answer
**Scenario**: LLM includes disclaimers within the answer text.
- **Impact**: Violates sentence limit, cluttered response
- **Mitigation**:
  - Separate disclaimers from answer
  - Use dedicated disclaimer field
  - Strip disclaimers from answer
  - Keep answer focused

## Cross-Phase Edge Cases

#### EC5.CP1: Query-Response Mismatch
**Scenario**: Generated response doesn't actually answer the user's question.
- **Impact**: Poor user experience, frustration
- **Mitigation**:
  - Implement response relevance validation
  - Use re-ranking for better matching
  - Allow user feedback on relevance
  - Monitor relevance metrics

#### EC5.CP2: Caching Invalidation
**Scenario**: Cached responses become outdated after data refresh.
- **Impact**: Stale responses returned to users
- **Mitigation**:
  - Implement cache invalidation on data refresh
  - Use time-based cache expiration
  - Version cache keys
  - Monitor cache hit rates

#### EC5.CP3: Error Propagation
**Scenario**: Errors from earlier phases (bad data, poor retrieval) propagate to final response.
- **Impact**: Poor quality responses, user dissatisfaction
- **Mitigation**:
  - Implement error handling at each stage
  - Validate outputs between phases
  - Use fallback strategies
  - Log errors for debugging

---

# Phase 6: User Interface Development

## 6.1 UI Design

### Edge Cases

#### EC6.1.1: Mobile Responsiveness Issues
**Scenario**: UI doesn't display correctly on mobile devices or different screen sizes.
- **Impact**: Poor user experience on mobile, accessibility issues
- **Mitigation**:
  - Use responsive design frameworks
  - Test on various devices and screen sizes
  - Implement mobile-first design
  - Use CSS Grid/Flexbox for layout

#### EC6.1.2: Accessibility Compliance
**Scenario**: UI not accessible to users with disabilities (screen readers, keyboard navigation).
- **Impact**: Exclusion of users with disabilities, compliance issues
- **Mitigation**:
  - Follow WCAG 2.1 guidelines
  - Implement ARIA labels
  - Ensure keyboard navigation
  - Test with screen readers
  - Use sufficient color contrast

#### EC6.1.3: Browser Compatibility
**Scenario**: UI breaks or looks different on certain browsers (Safari, Firefox, Edge).
- **Impact**: Inconsistent user experience
- **Mitigation**:
  - Test on major browsers
  - Use standard CSS/JS
  - Implement progressive enhancement
  - Use browser compatibility libraries if needed

#### EC6.1.4: Slow Loading Times
**Scenario**: UI takes too long to load, especially on slow connections.
- **Impact**: User abandonment, poor UX
- **Mitigation**:
  - Optimize asset loading
  - Implement lazy loading
  - Use CDN for static assets
  - Minimize JavaScript bundle size
  - Show loading indicators

#### EC6.1.5: Example Questions Not Clickable
**Scenario**: Example questions displayed but not interactive.
- **Impact**: Missed opportunity for user guidance
- **Mitigation**:
  - Make examples clickable
  - Pre-fill query input on click
  - Provide visual feedback
  - Test example functionality

#### EC6.1.6: Disclaimer Not Prominent
**Scenario**: "Facts-only. No investment advice." disclaimer not visible or overlooked.
- **Impact**: Users may misunderstand system capabilities
- **Mitigation**:
  - Make disclaimer prominent and persistent
  - Use contrasting colors
  - Place disclaimer near query input
  - Require acknowledgment on first use

#### EC6.1.7: Dark Mode Issues
**Scenario**: UI doesn't support dark mode or has contrast issues in dark mode.
- **Impact**: Poor user experience for dark mode users
- **Mitigation**:
  - Implement system-wide dark mode
  - Test contrast in both modes
  - Use CSS variables for theming
  - Allow manual mode toggle

## 6.2 Frontend Implementation

### Edge Cases

#### EC6.2.1: API Connection Failures
**Scenario**: Frontend cannot connect to backend API.
- **Impact**: UI non-functional, error displayed to user
- **Mitigation**:
  - Implement retry logic
  - Show helpful error messages
  - Provide offline indication
  - Log connection failures

#### EC6.2.2: API Timeout
**Scenario**: API request times out, leaving UI in loading state.
- **Impact**: User waits indefinitely, poor UX
- **Mitigation**:
  - Implement request timeout
  - Show timeout error message
  - Allow retry
  - Set reasonable timeout values

#### EC6.2.3: Malformed API Response
**Scenario**: Backend returns unexpected response format.
- **Impact**: UI crashes or displays incorrectly
- **Mitigation**:
  - Validate response structure
  - Implement error boundaries
  - Show graceful error message
  - Log malformed responses

#### EC6.2.4: State Management Issues
**Scenario**: UI state gets out of sync (e.g., loading state stuck).
- **Impact**: Confusing UI, incorrect behavior
- **Mitigation**:
  - Use robust state management
  - Implement state validation
  - Provide reset mechanisms
  - Test state transitions

#### EC6.2.5: Form Validation Failures
**Scenario**: Query input validation fails or behaves unexpectedly.
- **Impact**: User cannot submit queries
- **Mitigation**:
  - Implement client-side validation
  - Show clear validation messages
  - Provide real-time feedback
  - Test edge cases (empty, too long, special chars)

#### EC6.2.6: Memory Leaks
**Scenario**: Frontend accumulates memory over time, causing performance degradation.
- **Impact**: Slow UI, browser crashes
- **Mitigation**:
  - Profile memory usage
  - Clean up event listeners
  - Unmount components properly
  - Use React.memo or similar optimizations

#### EC6.2.7: JavaScript Errors
**Scenario**: Unhandled JavaScript errors break UI functionality.
- **Impact**: Partial or complete UI failure
- **Mitigation**:
  - Implement global error handling
  - Use error boundaries
  - Log errors for debugging
  - Show user-friendly error messages

## 6.3 Backend API

### Edge Cases

#### EC6.3.1: API Rate Limiting
**Scenario**: API hits rate limits due to high traffic.
- **Impact**: Requests rejected, service unavailable
- **Mitigation**:
  - Implement rate limiting at API level
  - Return 429 status with retry-after header
  - Implement request queuing
  - Monitor API usage

#### EC6.3.2: API Authentication Failures
**Scenario**: API authentication fails (expired tokens, invalid keys).
- **Impact**: API calls rejected, service unavailable
- **Mitigation**:
  - Implement token refresh logic
  - Use secure token storage
  - Monitor authentication failures
  - Implement graceful degradation

#### EC6.3.3: Invalid Request Payload
**Scenario**: Frontend sends invalid or malformed request to API.
- **Impact**: API returns error, user sees error
- **Mitigation**:
  - Validate request payload at API
  - Return detailed error messages
  - Implement request schema validation
  - Log validation failures

#### EC6.3.4: Database Connection Failures
**Scenario**: API cannot connect to vector database.
- **Impact**: Cannot retrieve data, API errors
- **Mitigation**:
  - Implement connection retry logic
  - Use connection pooling
  - Return graceful error message
  - Monitor database health

#### EC6.3.5: Concurrent Request Overload
**Scenario**: Too many concurrent requests overwhelm API.
- **Impact**: Slow responses, timeouts
- **Mitigation**:
  - Implement request queuing
  - Use load balancing
  - Scale horizontally
  - Implement circuit breaker pattern

#### EC6.3.6: API Version Conflicts
**Scenario**: Frontend and backend use different API versions.
- **Impact**: Request/response mismatch, errors
- **Mitigation**:
  - Version API endpoints
  - Document API versions
  - Implement backward compatibility
  - Use API gateway for version management

#### EC6.3.7: CORS Issues
**Scenario**: Cross-Origin Resource Sharing (CORS) blocks requests.
- **Impact**: Frontend cannot call API
- **Mitigation**:
  - Configure CORS properly
  - Use same origin if possible
  - Test CORS configuration
  - Document CORS policies

## 6.4 UI-Backend Integration

### Edge Cases

#### EC6.4.1: Network Interruption During Request
**Scenario**: Network connection drops during API request.
- **Impact**: Request fails, user confusion
- **Mitigation**:
  - Implement retry logic
  - Show network error message
  - Allow manual retry
  - Save draft query if possible

#### EC6.4.2: Slow API Response
**Scenario**: API takes too long to respond, UI appears frozen.
- **Impact**: Poor user experience, user abandonment
- **Mitigation**:
  - Implement loading indicators
  - Use timeout with retry
  - Show progress feedback
  - Optimize API performance

#### EC6.4.3: Response Display Errors
**Scenario**: API response valid but UI fails to display correctly.
- **Impact**: User sees error or blank response
- **Mitigation**:
  - Validate response before display
  - Implement error boundaries
  - Test display with various response formats
  - Log display errors

#### EC6.4.4: State Synchronization Issues
**Scenario**: Frontend state gets out of sync with backend state.
- **Impact**: Inconsistent behavior, confusion
- **Mitigation**:
  - Implement state reconciliation
  - Use server state as source of truth
  - Implement optimistic updates with rollback
  - Test state synchronization

#### EC6.4.5: Session Management Issues
**Scenario**: User session expires or becomes invalid during use.
- **Impact**: User logged out unexpectedly, lost work
- **Mitigation**:
  - Implement session refresh
  - Warn before session expires
  - Save user queries locally
  - Allow seamless re-authentication

#### EC6.4.6: WebSocket/Streaming Issues
**Scenario**: If using streaming responses, connection drops or errors.
- **Impact**: Partial response, incomplete information
- **Mitigation**:
  - Implement reconnection logic
  - Buffer responses
  - Fallback to non-streaming if needed
  - Handle partial responses gracefully

## Cross-Phase Edge Cases

#### EC6.CP1: Performance Degradation
**Scenario**: Overall system performance degrades over time (memory leaks, database bloat).
- **Impact**: Slow UI, poor user experience
- **Mitigation**:
  - Monitor performance metrics
  - Implement regular maintenance
  - Profile and optimize bottlenecks
  - Implement auto-scaling

#### EC6.CP2: Security Vulnerabilities
**Scenario**: Security vulnerabilities in frontend or backend (XSS, CSRF, injection).
- **Impact**: Security breach, data exposure
- **Mitigation**:
  - Implement security best practices
  - Regular security audits
  - Use security headers
  - Sanitize all inputs/outputs
  - Implement CSRF protection

#### EC6.CP3: User Experience Inconsistencies
**Scenario**: Inconsistent UX across different parts of the application.
- **Impact**: User confusion, poor learnability
- **Mitigation**:
  - Create design system
  - Follow UX patterns consistently
  - Conduct UX testing
  - Document design decisions

---

# Phase 7: Testing & Validation

## 7.1 Unit Testing

### Edge Cases

#### EC7.1.1: Test Data Availability
**Scenario**: Insufficient or unrealistic test data for unit tests.
- **Impact**: Tests don't cover real-world scenarios
- **Mitigation**:
  - Create comprehensive test data sets
  - Use synthetic data generation
  - Sample from real corpus (anonymized)
  - Maintain test data repository

#### EC7.1.2: Mocking External Dependencies
**Scenario**: Difficulty mocking external APIs (embedding, LLM) for unit tests.
- **Impact**: Tests rely on external services, flaky tests
- **Mitigation**:
  - Implement comprehensive mocking
  - Use mock servers for external APIs
  - Create deterministic mock responses
  - Test both with and without mocks

#### EC7.1.3: Test Isolation Failures
**Scenario**: Tests interfere with each other (shared state, database).
- **Impact**: Flaky tests, false failures
- **Mitigation**:
  - Isolate test environments
  - Use test databases
  - Clean up after each test
  - Run tests in random order

#### EC7.1.4: Edge Case Coverage Gaps
**Scenario**: Unit tests miss edge cases (empty inputs, null values, boundary conditions).
- **Impact**: Bugs in production
- **Mitigation**:
  - Use test coverage tools
  - Perform edge case analysis
  - Implement property-based testing
  - Review coverage reports

#### EC7.1.5: Test Performance Issues
**Scenario**: Unit tests take too long to run, slowing development.
- **Impact**: Reduced developer productivity, tests skipped
- **Mitigation**:
  - Optimize slow tests
  - Use test parallelization
  - Separate unit from integration tests
  - Implement test caching

## 7.2 Integration Testing

### Edge Cases

#### EC7.2.1: Environment Configuration
**Scenario**: Integration test environment differs from production.
- **Impact**: Tests pass in test but fail in production
- **Mitigation**:
  - Mirror production environment
  - Use containerization (Docker)
  - Automate environment setup
  - Document configuration differences

#### EC7.2.2: Data Consistency
**Scenario**: Test data inconsistent across integration test runs.
- **Impact**: Flaky tests, unreliable results
- **Mitigation**:
  - Use deterministic test data
  - Reset database between runs
  - Use data seeding scripts
  - Implement test data versioning

#### EC7.2.3: External Service Dependencies
**Scenario**: Integration tests depend on external services (embedding API, LLM API).
- **Impact**: Tests flaky due to external factors
- **Mitigation**:
  - Use service virtualization
  - Implement retry logic for external calls
  - Have fallback test modes
  - Monitor external service health

#### EC7.2.4: Test Execution Time
**Scenario**: Integration tests take too long to complete.
- **Impact**: Slow feedback, tests not run frequently
- **Mitigation**:
  - Optimize test execution
  - Parallelize independent tests
  - Use test selection strategies
  - Run critical tests more frequently

## 7.3 Quality Assurance Testing

### Edge Cases

#### EC7.3.1: Ambiguous Requirements
**Scenario**: QA requirements unclear or open to interpretation.
- **Impact**: Inconsistent testing, missed bugs
- **Mitigation**:
  - Clarify requirements before testing
  - Create test cases from requirements
  - Document acceptance criteria
  - Regular requirement reviews

#### EC7.3.2: Test Case Completeness
**Scenario**: Test cases don't cover all user scenarios or edge cases.
- **Impact**: Bugs slip through to production
- **Mitigation**:
  - Perform risk-based testing
  - Use exploratory testing
  - Involve domain experts
  - Review test coverage

#### EC7.3.3: Regression Detection
**Scenario**: New features break existing functionality (regressions).
- **Impact**: Quality degradation over time
- **Mitigation**:
  - Implement regression test suite
  - Run full test suite before release
  - Use automated regression testing
  - Monitor for regressions

#### EC7.3.4: Performance Testing Gaps
**Scenario**: Performance not tested under realistic load.
- **Impact**: Performance issues in production
- **Mitigation**:
  - Implement load testing
  - Test with realistic data volumes
  - Monitor performance metrics
  - Establish performance baselines

#### EC7.3.5: Compliance Validation
**Scenario**: Compliance requirements (facts-only, source citation) not validated.
- **Impact**: Regulatory violations
- **Mitigation**:
  - Create compliance test cases
  - Automate compliance checks
  - Legal review of responses
  - Document compliance testing

## 7.4 User Acceptance Testing

### Edge Cases

#### EC7.4.1: User Recruitment Challenges
**Scenario**: Difficulty recruiting representative users for UAT.
- **Impact**: Limited feedback, biased results
- **Mitigation**:
  - Use user research platforms
  - Recruit from target user groups
  - Offer incentives
  - Plan recruitment early

#### EC7.4.2: User Feedback Quality
**Scenario**: User feedback vague, unhelpful, or biased.
- **Impact**: Difficult to act on feedback
- **Mitigation**:
  - Provide structured feedback forms
  - Conduct interviews
  - Use think-aloud protocols
  - Train users on providing feedback

#### EC7.4.3: Test Environment Differences
**Scenario**: UAT environment differs from production environment.
- **Impact**: Issues found in UAT don't occur in production (or vice versa)
- **Mitigation**:
  - Mirror production environment
  - Document environment differences
  - Test in production-like conditions
  - Monitor production for issues

#### EC7.4.4: Scope Creep
**Scenario**: UAT reveals many issues, scope expands to fix everything.
- **Impact**: Delays, budget overruns
- **Mitigation**:
  - Prioritize issues by severity
  - Set clear acceptance criteria
  - Plan for known limitations
  - Phase improvements

#### EC7.4.5: User Training Needs
**Scenario**: Users struggle to use system during UAT due to lack of training.
- **Impact**: Poor feedback, negative impression
- **Mitigation**:
  - Provide user guides
  - Conduct training sessions
  - Offer onboarding support
  - Improve UI intuitiveness

## Cross-Phase Edge Cases

#### EC7.CP1: Test Environment Drift
**Scenario**: Test environments drift from production over time.
- **Impact**: Tests become unreliable
- **Mitigation**:
  - Regularly sync environments
  - Use infrastructure as code
  - Monitor environment differences
  - Automate environment updates

#### EC7.CP2: Test Data Privacy
**Scenario**: Test data contains real user data or PII.
- **Impact**: Privacy violation, compliance issues
- **Mitigation**:
  - Anonymize test data
  - Use synthetic data
  - Implement data governance
  - Regular data audits

---

# Phase 8: Deployment & Monitoring

## 8.1 Deployment Strategy

### Edge Cases

#### EC8.1.1: Deployment Rollback Failure
**Scenario**: Deployment fails and rollback cannot be completed.
- **Impact**: Extended downtime, broken production
- **Mitigation**:
  - Test rollback procedures regularly
  - Implement blue-green deployment
  - Use canary releases
  - Have manual rollback procedures documented

#### EC8.1.2: Database Migration Failures
**Scenario**: Database schema migration fails during deployment.
- **Impact**: Application cannot start, data inconsistency
- **Mitigation**:
  - Test migrations in staging
  - Implement reversible migrations
  - Use transactional migrations
  - Have data backup before migration

#### EC8.1.3: Configuration Drift
**Scenario**: Production configuration differs from expected/staging configuration.
- **Impact**: Application behaves incorrectly, errors
- **Mitigation**:
  - Use infrastructure as code
  - Automate configuration management
  - Validate configuration on deployment
  - Document configuration differences

#### EC8.1.4: Dependency Version Conflicts
**Scenario**: Dependency versions differ between environments or break after deployment.
- **Impact**: Application crashes, unexpected behavior
- **Mitigation**:
  - Use dependency locking
  - Test with exact production versions
  - Implement dependency scanning
  - Document version requirements

#### EC8.1.5: Resource Exhaustion
**Scenario**: Deployment fails due to insufficient resources (CPU, memory, disk).
- **Impact**: Deployment incomplete, performance issues
- **Mitigation**:
  - Monitor resource usage
  - Right-size resources
  - Implement auto-scaling
  - Plan resource requirements

#### EC8.1.6: Deployment Timeout
**Scenario**: Deployment process times out before completion.
- **Impact**: Partial deployment, inconsistent state
- **Mitigation**:
  - Implement deployment checkpoints
  - Use idempotent deployment scripts
  - Increase timeout for large deployments
  - Implement deployment monitoring

#### EC8.1.7: Secret Management Failures
**Scenario**: API keys, database credentials not properly deployed or rotated.
- **Impact**: Authentication failures, security risk
- **Mitigation**:
  - Use secret management systems
  - Automate secret injection
  - Implement secret rotation
  - Never commit secrets to code

## 8.2 Monitoring & Logging

### Edge Cases

#### EC8.2.1: Monitoring System Outage
**Scenario**: Monitoring system itself goes down or becomes unresponsive.
- **Impact**: Blind spot in system health, no alerts
- **Mitigation**:
  - Monitor the monitoring system
  - Use multiple monitoring tools
  - Implement failover monitoring
  - Have manual health check procedures

#### EC8.2.2: Alert Fatigue
**Scenario**: Too many alerts generated, team ignores or misses critical alerts.
- **Impact**: Critical issues missed, slow response time
- **Mitigation**:
  - Tune alert thresholds
  - Implement alert grouping
  - Use severity-based alerting
  - Regularly review and prune alerts

#### EC8.2.3: Log Volume Overload
**Scenario**: Log volume exceeds storage capacity or processing capability.
- **Impact**: Logs lost, monitoring degraded
- **Mitigation**:
  - Implement log rotation
  - Use log sampling for high-volume logs
  - Compress archived logs
  - Monitor log storage usage

#### EC8.2.4: Sensitive Data in Logs
**Scenario**: Logs contain sensitive information (PII, API keys).
- **Impact**: Security violation, compliance issues
- **Mitigation**:
  - Implement log sanitization
  - Scan logs for sensitive data
  - Use log access controls
  - Regular log audits

#### EC8.2.5: Metric Collection Failures
**Scenario**: Metrics not collected or collected incorrectly.
- **Impact**: Incomplete monitoring, missed issues
- **Mitigation**:
  - Validate metric collection
  - Implement metric health checks
  - Test metric queries
  - Document metric definitions

#### EC8.2.6: Distributed Tracing Issues
**Scenario**: Distributed tracing fails or traces incomplete.
- **Impact**: Difficult to debug distributed issues
- **Mitigation**:
  - Implement sampling strategies
  - Ensure trace propagation
  - Monitor tracing system health
  - Have fallback debugging methods

## 8.3 Maintenance & Updates

### Edge Cases

#### EC8.3.1: Data Refresh Failures
**Scenario**: Scheduled data refresh fails, leaving stale data in system.
- **Impact**: Outdated information provided to users
- **Mitigation**:
  - Monitor refresh success
  - Implement retry logic
  - Alert on refresh failures
  - Have manual refresh procedures

#### EC8.3.2: Zero-Downtime Updates
**Scenario**: Updates require downtime, affecting users.
- **Impact**: Service interruption, user dissatisfaction
- **Mitigation**:
  - Implement blue-green deployment
  - Use rolling updates
  - Schedule updates during low-traffic periods
  - Communicate maintenance windows

#### EC8.3.3: Dependency Updates Breaking Changes
**Scenario**: Dependency updates introduce breaking changes.
- **Impact**: Application fails after update
- **Mitigation**:
  - Test updates in staging
  - Use semantic versioning
  - Implement compatibility checks
  - Pin critical dependencies

#### EC8.3.4: Backup Restoration Failures
**Scenario**: Backup cannot be restored when needed.
- **Impact**: Data loss, extended downtime
- **Mitigation**:
  - Regularly test restoration
  - Validate backup integrity
  - Document restoration procedures
  - Have multiple backup copies

#### EC8.3.5: Security Patch Delays
**Scenario**: Security patches not applied promptly.
- **Impact**: Security vulnerabilities exploited
- **Mitigation**:
  - Automate security patching
  - Monitor security advisories
  - Prioritize critical patches
  - Have emergency patching procedures

#### EC8.3.6: Performance Degradation Over Time
**Scenario**: System performance degrades gradually over time.
- **Impact**: Slow responses, poor user experience
- **Mitigation**:
  - Monitor performance trends
  - Implement performance baselines
  - Regular performance tuning
  - Plan capacity growth

## 8.4 Documentation

### Edge Cases

#### EC8.4.1: Documentation Outdated
**Scenario**: Documentation becomes outdated as system evolves.
- **Impact**: Confusion, incorrect usage
- **Mitigation**:
  - Review documentation regularly
  - Update docs with code changes
  - Use documentation as code
  - Implement doc versioning

#### EC8.4.2: Incomplete Documentation
**Scenario**: Critical information missing from documentation.
- **Impact**: Users cannot use system effectively
- **Mitigation**:
  - Create documentation checklist
  - Review with new users
  - Include troubleshooting sections
  - Maintain FAQ

#### EC8.4.3: Documentation Inaccessibility
**Scenario**: Documentation not accessible (broken links, paywalls, permissions).
- **Impact**: Users cannot access needed information
- **Mitigation**:
  - Host documentation publicly
  - Use multiple formats (web, PDF)
  - Implement search functionality
  - Regular link checking

#### EC8.4.4: Language Barriers
**Scenario**: Documentation only in English, non-English speakers cannot use.
- **Impact**: Limited user base
- **Mitigation**:
  - Translate key documentation
  - Use simple language
  - Include diagrams and examples
  - Consider localization

## Cross-Phase Edge Cases

#### EC8.CP1: Scaling Challenges
**Scenario**: System cannot handle increased load as user base grows.
- **Impact**: Performance degradation, outages
- **Mitigation**:
  - Implement auto-scaling
  - Load test regularly
  - Monitor capacity metrics
  - Plan scaling architecture

#### EC8.CP2: Cost Overruns
**Scenario**: Cloud or service costs exceed budget.
- **Impact**: Budget issues, service cuts
- **Mitigation**:
  - Monitor costs in real-time
  - Implement cost alerts
  - Optimize resource usage
  - Use reserved instances where applicable

#### EC8.CP3: Security Incidents
**Scenario**: Security breach or incident occurs in production.
- **Impact**: Data exposure, service disruption
- **Mitigation**:
  - Implement incident response plan
  - Regular security audits
  - Use security monitoring
  - Have communication procedures

#### EC8.CP4: Vendor Lock-in
**Scenario**: Dependent on specific cloud provider or service, difficult to migrate.
- **Impact**: Limited flexibility, pricing issues
- **Mitigation**:
  - Use multi-cloud strategy where possible
  - Avoid proprietary services
  - Implement abstraction layers
  - Document dependencies

---

# Summary

This comprehensive edge case document covers all 8 phases of the Mutual Fund FAQ Assistant project:

1. **Phase 1**: Data Collection & Corpus Preparation
2. **Phase 2**: Document Ingestion & Processing
3. **Phase 3**: Vector Database Setup
4. **Phase 4**: RAG Pipeline Development
5. **Phase 5**: Query Processing & Response Generation
6. **Phase 6**: User Interface Development
7. **Phase 7**: Testing & Validation
8. **Phase 8**: Deployment & Monitoring

Each phase includes specific edge cases, their impacts, and mitigation strategies. Cross-phase edge cases are also identified to address system-wide challenges. This document should be referenced throughout the development lifecycle to proactively address potential issues.
