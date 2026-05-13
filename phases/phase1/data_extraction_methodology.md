# Data Extraction Methodology

## Overview
This document outlines the methodology for extracting content from the 5 selected Groww URLs for the Mutual Fund FAQ Assistant project.

## Extraction Approach

### Primary Method: Web Scraping with Headless Browser

**Rationale**:
- All 5 URLs require JavaScript rendering for complete content
- Dynamic content loads after initial page load
- Headless browser ensures complete content capture
- Allows waiting for specific elements to load

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Headless Browser | Playwright | Latest | JavaScript rendering |
| HTML Parser | BeautifulSoup | 4.x | HTML parsing |
| HTTP Library | requests | 2.x | Fallback HTTP requests |
| Data Validation | pydantic | 2.x | Schema validation |
| Error Handling | tenacity | Latest | Retry logic |

## Extraction Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    URL Queue                                 │
│  - 5 Groww URLs                                             │
│  - Priority: FIFO                                          │
│  - Retry queue for failed URLs                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Headless Browser (Playwright)                  │
│  - Launch browser instance                                  │
│  - Navigate to URL                                          │
│  - Wait for content load                                    │
│  - Extract HTML                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              HTML Parser (BeautifulSoup)                     │
│  - Parse HTML content                                       │
│  - Apply CSS selectors                                      │
│  - Extract data fields                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Normalizer                                 │
│  - Clean text formatting                                    │
│  - Remove headers/footers                                  │
│  - Normalize numerical data                                 │
│  - Handle special characters                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Schema Validator                                │
│  - Validate extracted data                                  │
│  - Check required fields                                    │
│  - Type checking                                            │
│  - Range validation                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Storage                                    │
│  - Store extracted data                                    │
│  - Attach metadata (timestamp, source)                     │
│  - Save to JSON/Database                                    │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Extraction Process

### Step 1: URL Queue Management
```python
# Pseudocode
url_queue = [
    "https://groww.in/mutual-funds/axis-silver-fof-direct-growth",
    "https://groww.in/mutual-funds/axis-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/axis-gold-fund-direct-growth",
    "https://groww.in/mutual-funds/axis-nifty-india-defence-index-fund-direct-growth"
]

retry_queue = []
processed_urls = []
```

### Step 2: Headless Browser Setup
```python
# Playwright configuration
browser = await playwright.chromium.launch(headless=True)
page = await browser.new_page()

# Set user agent
await page.set_extra_http_headers({
    "User-Agent": "MutualFundFAQBot/1.0 (educational-research)"
})
```

### Step 3: Page Navigation and Content Loading
```python
async def extract_url(url):
    await page.goto(url, wait_until="networkidle")
    
    # Wait for specific elements to load
    await page.wait_for_selector(".scheme-details")
    await page.wait_for_selector(".expense-ratio")
    
    # Extract HTML
    html_content = await page.content()
    return html_content
```

### Step 4: HTML Parsing with BeautifulSoup
```python
from bs4 import BeautifulSoup

def parse_html(html_content, url):
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Extract data using CSS selectors
    scheme_name = soup.select_one(".scheme-name").text.strip()
    category = soup.select_one(".category").text.strip()
    expense_ratio = soup.select_one(".expense-ratio").text.strip()
    
    return {
        "scheme_name": scheme_name,
        "category": category,
        "expense_ratio": expense_ratio,
        "source_url": url
    }
```

### Step 5: Data Normalization
```python
def normalize_data(extracted_data):
    # Normalize expense ratio
    if "expense_ratio" in extracted_data:
        extracted_data["expense_ratio"] = normalize_percentage(
            extracted_data["expense_ratio"]
        )
    
    # Clean special characters
    for key, value in extracted_data.items():
        if isinstance(value, str):
            extracted_data[key] = clean_text(value)
    
    return extracted_data
```

### Step 6: Schema Validation
```python
from pydantic import BaseModel, validator

class SchemeData(BaseModel):
    scheme_name: str
    category: str
    expense_ratio: float
    exit_load: str
    minimum_investment: int
    source_url: str
    extracted_at: datetime
    
    @validator('expense_ratio')
    def validate_expense_ratio(cls, v):
        if v < 0 or v > 5:
            raise ValueError('Expense ratio must be between 0 and 5')
        return v
```

## Data Fields to Extract

### Common Fields (All Schemes)
| Field | Data Type | CSS Selector | Validation |
|-------|-----------|--------------|------------|
| Scheme Name | string | .scheme-name | Not empty |
| Scheme Code | string | .scheme-code | Format: XXXXXXX |
| Category | string | .category | Enum: Equity, Debt, etc. |
| Sub-Category | string | .sub-category | Not empty |
| Expense Ratio | float | .expense-ratio | Range: 0-5% |
| Exit Load | string | .exit-load | Not empty |
| Minimum Investment | integer | .minimum-investment | >= 100 |
| SIP Amount | integer | .sip-amount | >= 100 |
| NAV | float | .nav-value | > 0 |
| NAV Date | date | .nav-date | Valid date |
| Risk Level | string | .riskometer | Enum: Low to Very High |
| Benchmark | string | .benchmark | Not empty |
| Fund Manager | string | .fund-manager | Not empty |
| AUM | float | .aum | > 0 |

### Scheme-Specific Fields

#### Axis Silver FoF
| Field | Data Type | CSS Selector |
|-------|-----------|--------------|
| ETF Holdings | list | .etf-holdings |
| Silver Price Correlation | float | .correlation |

#### Axis Small Cap Fund
| Field | Data Type | CSS Selector |
|-------|-----------|--------------|
| Market Cap Distribution | dict | .market-cap-dist |
| Sector Allocation | dict | .sector-allocation |

#### Axis Flexi Cap Fund
| Field | Data Type | CSS Selector |
|-------|-----------|--------------|
| Asset Allocation | dict | .asset-allocation |
| Sector-wise Exposure | dict | .sector-exposure |

#### Axis Gold Fund
| Field | Data Type | CSS Selector |
|-------|-----------|--------------|
| Gold Price Tracking | float | .gold-tracking |
| ETF Holdings | list | .etf-holdings |

#### Axis Nifty India Defence Index Fund
| Field | Data Type | CSS Selector |
|-------|-----------|--------------|
| Index Constituents | list | .index-constituents |
| Tracking Error | float | .tracking-error |

## Rate Limiting Strategy

### Request Throttling
```python
import asyncio
import time

async def extract_with_delay(url):
    # Minimum delay between requests
    await asyncio.sleep(3)  # 3 seconds delay
    
    result = await extract_url(url)
    return result
```

### Exponential Backoff
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def extract_with_retry(url):
    try:
        return await extract_url(url)
    except Exception as e:
        logger.error(f"Failed to extract {url}: {e}")
        raise
```

### Concurrent Request Limit
- Maximum concurrent requests: 1
- Sequential processing to avoid rate limiting
- Monitor for 429 (Too Many Requests) responses

## robots.txt Compliance

### Compliance Check
```python
import urllib.robotparser

rp = urllib.robotparser.RobotFileParser()
rp.set_url("https://groww.in/robots.txt")
rp.read()

def can_fetch(url):
    return rp.can_fetch("MutualFundFAQBot", url)
```

### Implementation
- Check robots.txt before each request
- Respect crawl-delay if specified
- Identify user agent appropriately
- Do not override disallow rules

## Error Handling

### Error Categories
1. **Network Errors**: Connection timeout, DNS failure
2. **HTTP Errors**: 404, 403, 429, 500
3. **Parsing Errors**: Invalid HTML, missing elements
4. **Validation Errors**: Invalid data format, out of range
5. **Dynamic Content Errors**: Content not loading

### Error Handling Strategy
```python
async def extract_with_error_handling(url):
    try:
        # Check robots.txt
        if not can_fetch(url):
            logger.warning(f"URL disallowed by robots.txt: {url}")
            return None
        
        # Extract with retry
        result = await extract_with_retry(url)
        
        # Validate result
        validated = validate_data(result)
        
        return validated
        
    except NetworkError as e:
        logger.error(f"Network error for {url}: {e}")
        return await handle_network_error(url)
        
    except ValidationError as e:
        logger.error(f"Validation error for {url}: {e}")
        return await handle_validation_error(url)
        
    except Exception as e:
        logger.error(f"Unexpected error for {url}: {e}")
        return None
```

## Data Freshness Strategy

### Timestamp Tracking
```python
from datetime import datetime

extracted_data = {
    "scheme_name": "Axis Flexi Cap Fund",
    "expense_ratio": 1.05,
    "extracted_at": datetime.utcnow().isoformat(),
    "source_url": "https://groww.in/..."
}
```

### Refresh Schedule
- NAV data: Daily refresh
- Scheme details: Weekly refresh
- Portfolio holdings: Monthly refresh
- Full extraction: Quarterly

### Incremental Updates
- Only update changed fields
- Compare with previous extraction
- Store version history

## Output Format

### JSON Structure
```json
{
  "scheme_name": "Axis Flexi Cap Fund Direct Growth",
  "scheme_code": "120503",
  "category": "Equity",
  "sub_category": "Flexi-cap",
  "expense_ratio": 1.05,
  "exit_load": "1% if redeemed within 30 days",
  "minimum_investment": 100,
  "sip_amount": 100,
  "nav": 45.67,
  "nav_date": "2024-05-08",
  "risk_level": "Very High",
  "benchmark": "NIFTY 50 - TRI",
  "fund_manager": "Shreyash Deore",
  "aum": 45678.90,
  "source_url": "https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth",
  "extracted_at": "2024-05-08T10:30:00Z",
  "metadata": {
    "extraction_method": "headless_browser",
    "extraction_version": "1.0"
  }
}
```

## Monitoring and Logging

### Logging Strategy
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extraction.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics to Track
- Extraction success rate per URL
- Average extraction time per URL
- Data validation failure rate
- Retry attempts
- Rate limiting occurrences

### Alerts
- On extraction failure
- On validation errors
- On significant structure changes
- On robots.txt changes

## Testing Strategy

### Unit Tests
- Test individual extraction functions
- Test data normalization
- Test schema validation
- Test error handling

### Integration Tests
- Test end-to-end extraction pipeline
- Test with actual URLs (staging environment)
- Test retry logic
- Test rate limiting

### Validation Tests
- Test with known good data
- Test with malformed data
- Test with missing fields
- Test with out-of-range values

## Security Considerations

### User Agent Identification
- Clearly identify the bot
- Provide contact information
- Explain purpose (educational research)

### Data Privacy
- No PII collection
- Anonymize any user data
- Secure storage of extracted data

### Terms of Service Compliance
- Review Groww's Terms of Service
- Ensure compliance with data usage policies
- No unauthorized access

## References
- Playwright Documentation: https://playwright.dev
- BeautifulSoup Documentation: https://www.crummy.com/software/BeautifulSoup/
- robots.txt Specification: https://www.robotstxt.org
- Groww Terms of Service: https://groww.in/terms

---
**Document Version**: 1.0
**Last Updated**: 2024-05-08
**Status**: Approved
