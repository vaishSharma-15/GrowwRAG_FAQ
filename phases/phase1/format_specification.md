# Format Specification

## Overview
This document defines the data format standards for extracted mutual fund scheme information from the 5 selected Groww URLs.

## Data Schema

### Primary Data Structure

```json
{
  "scheme_info": {
    "scheme_name": "string",
    "scheme_code": "string",
    "amc": "string",
    "category": "string",
    "sub_category": "string",
    "plan_type": "string"
  },
  "financial_details": {
    "expense_ratio": "float",
    "exit_load": "string",
    "minimum_investment": "integer",
    "sip_amount": "integer",
    "nav": "float",
    "nav_date": "string (ISO 8601)"
  },
  "risk_and_returns": {
    "risk_level": "string",
    "benchmark": "string",
    "aum": "float",
    "returns": {
      "1_year": "float (optional)",
      "3_year": "float (optional)",
      "5_year": "float (optional)"
    }
  },
  "fund_management": {
    "fund_manager": "string",
    "fund_manager_experience": "string (optional)"
  },
  "portfolio": {
    "holdings": "array (optional)",
    "sector_allocation": "object (optional)",
    "asset_allocation": "object (optional)"
  },
  "metadata": {
    "source_url": "string",
    "extracted_at": "string (ISO 8601)",
    "extraction_method": "string",
    "extraction_version": "string",
    "last_updated": "string (ISO 8601)"
  }
}
```

## Field Specifications

### Scheme Information

| Field | Type | Required | Format | Validation |
|-------|------|----------|--------|------------|
| scheme_name | string | Yes | Plain text | Not empty, max 200 chars |
| scheme_code | string | Yes | Alphanumeric | Pattern: ^[A-Z0-9]{6,7}$ |
| amc | string | Yes | Plain text | Must be "Axis Mutual Fund" |
| category | string | Yes | Plain text | Enum: Equity, Debt, Hybrid, Commodity, Index, FoF |
| sub_category | string | Yes | Plain text | Not empty, max 100 chars |
| plan_type | string | Yes | Plain text | Must be "Direct Growth" |

### Financial Details

| Field | Type | Required | Format | Validation |
|-------|------|----------|--------|------------|
| expense_ratio | float | Yes | Decimal | Range: 0.0 - 5.0, 2 decimal places |
| exit_load | string | Yes | Plain text | Not empty, max 500 chars |
| minimum_investment | integer | Yes | Integer | >= 100 |
| sip_amount | integer | Yes | Integer | >= 100 |
| nav | float | Yes | Decimal | > 0, 4 decimal places |
| nav_date | string | Yes | ISO 8601 | Format: YYYY-MM-DD |

### Risk and Returns

| Field | Type | Required | Format | Validation |
|-------|------|----------|--------|------------|
| risk_level | string | Yes | Plain text | Enum: Low, Low to Moderate, Moderate, Moderately High, High, Very High |
| benchmark | string | Yes | Plain text | Not empty, max 200 chars |
| aum | float | Yes | Decimal | > 0, 2 decimal places |
| returns.1_year | float | No | Decimal | Percentage, 2 decimal places |
| returns.3_year | float | No | Decimal | Percentage, 2 decimal places |
| returns.5_year | float | No | Decimal | Percentage, 2 decimal places |

### Fund Management

| Field | Type | Required | Format | Validation |
|-------|------|----------|--------|------------|
| fund_manager | string | Yes | Plain text | Not empty, max 200 chars |
| fund_manager_experience | string | No | Plain text | Max 100 chars |

### Portfolio

| Field | Type | Required | Format | Validation |
|-------|------|----------|--------|------------|
| holdings | array | No | Array of objects | See Holdings Schema |
| sector_allocation | object | No | Key-value pairs | Keys: sector names, Values: percentages |
| asset_allocation | object | No | Key-value pairs | Keys: asset types, Values: percentages |

#### Holdings Schema
```json
{
  "name": "string",
  "percentage": "float",
  "type": "string (optional)"
}
```

### Metadata

| Field | Type | Required | Format | Validation |
|-------|------|----------|--------|------------|
| source_url | string | Yes | URL | Valid URL format |
| extracted_at | string | Yes | ISO 8601 | Format: YYYY-MM-DDTHH:mm:ssZ |
| extraction_method | string | Yes | Plain text | Must be "headless_browser" |
| extraction_version | string | Yes | Semantic version | Format: X.Y.Z |
| last_updated | string | Yes | ISO 8601 | Format: YYYY-MM-DD |

## Enumerated Values

### Category Enum
- Equity
- Debt
- Hybrid
- Commodity
- Index
- Fund of Funds (FoF)

### Sub-Category Enum
- Large-cap
- Mid-cap
- Small-cap
- Flexi-cap
- ELSS
- Gold
- Silver
- Thematic Index
- Sectoral
- Balanced
- Debt Fund
- Liquid Fund
- Money Market

### Risk Level Enum
- Low
- Low to Moderate
- Moderate
- Moderately High
- High
- Very High

## Data Normalization Rules

### Numerical Data
- **Expense Ratio**: Convert percentage to decimal (e.g., "1.05%" → 1.05)
- **NAV**: Keep as decimal with 4 places (e.g., 45.6789)
- **AUM**: Convert to crores if in lakhs, keep as decimal
- **Returns**: Convert percentage to decimal (e.g., "15.5%" → 15.5)

### Text Data
- **Trim whitespace**: Remove leading/trailing whitespace
- **Normalize case**: Use title case for scheme names, sentence case for descriptions
- **Remove special characters**: Remove unnecessary special characters except where meaningful
- **Unicode normalization**: Use NFC normalization

### Date Data
- **Format**: All dates in ISO 8601 format (YYYY-MM-DD)
- **Timezone**: Use UTC for timestamps
- **Invalid dates**: Set to null if date cannot be parsed

### Percentage Data
- **Format**: Store as decimal number (not string with %)
- **Range**: 0-100 for returns, 0-5 for expense ratio
- **Negative values**: Allowed for returns (negative returns)

## Example Data

### Complete Example: Axis Flexi Cap Fund Direct Growth

```json
{
  "scheme_info": {
    "scheme_name": "Axis Flexi Cap Fund Direct Growth",
    "scheme_code": "120503",
    "amc": "Axis Mutual Fund",
    "category": "Equity",
    "sub_category": "Flexi-cap",
    "plan_type": "Direct Growth"
  },
  "financial_details": {
    "expense_ratio": 1.05,
    "exit_load": "1% if redeemed within 30 days, Nil after 30 days",
    "minimum_investment": 100,
    "sip_amount": 100,
    "nav": 45.6789,
    "nav_date": "2024-05-08"
  },
  "risk_and_returns": {
    "risk_level": "Very High",
    "benchmark": "NIFTY 50 - TRI",
    "aum": 45678.90,
    "returns": {
      "1_year": 18.45,
      "3_year": 14.23,
      "5_year": 12.87
    }
  },
  "fund_management": {
    "fund_manager": "Shreyash Deore",
    "fund_manager_experience": "10+ years"
  },
  "portfolio": {
    "holdings": [
      {
        "name": "Reliance Industries Ltd",
        "percentage": 8.5,
        "type": "Equity"
      },
      {
        "name": "HDFC Bank Ltd",
        "percentage": 7.2,
        "type": "Equity"
      }
    ],
    "sector_allocation": {
      "Financials": 28.5,
      "Technology": 15.3,
      "Consumer Goods": 12.8
    },
    "asset_allocation": {
      "Equity": 95.5,
      "Debt": 4.5
    }
  },
  "metadata": {
    "source_url": "https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth",
    "extracted_at": "2024-05-08T10:30:00Z",
    "extraction_method": "headless_browser",
    "extraction_version": "1.0.0",
    "last_updated": "2024-05-08"
  }
}
```

### Minimal Example (Missing Optional Fields)

```json
{
  "scheme_info": {
    "scheme_name": "Axis Silver FoF Direct Growth",
    "scheme_code": "120555",
    "amc": "Axis Mutual Fund",
    "category": "Fund of Funds",
    "sub_category": "Commodities",
    "plan_type": "Direct Growth"
  },
  "financial_details": {
    "expense_ratio": 0.50,
    "exit_load": "Nil",
    "minimum_investment": 100,
    "sip_amount": 100,
    "nav": 22.3456,
    "nav_date": "2024-05-08"
  },
  "risk_and_returns": {
    "risk_level": "Very High",
    "benchmark": "Silver Price",
    "aum": 1234.56
  },
  "fund_management": {
    "fund_manager": "Hiral Mehta"
  },
  "portfolio": {},
  "metadata": {
    "source_url": "https://groww.in/mutual-funds/axis-silver-fof-direct-growth",
    "extracted_at": "2024-05-08T10:35:00Z",
    "extraction_method": "headless_browser",
    "extraction_version": "1.0.0",
    "last_updated": "2024-05-08"
  }
}
```

## Validation Rules

### Required Fields
All fields marked as "Required" must be present in the extracted data. Missing required fields should trigger a validation error and the extraction should be retried or flagged for manual review.

### Type Validation
- String fields: Must be valid UTF-8 strings
- Integer fields: Must be whole numbers
- Float fields: Must be decimal numbers
- Date fields: Must be valid ISO 8601 dates
- URL fields: Must be valid URL format

### Range Validation
- expense_ratio: 0.0 - 5.0
- minimum_investment: >= 100
- sip_amount: >= 100
- nav: > 0
- aum: > 0
- returns: -100 to 100 (can be negative)

### Format Validation
- scheme_code: Must match pattern ^[A-Z0-9]{6,7}$
- nav_date: Must match YYYY-MM-DD format
- extracted_at: Must match YYYY-MM-DDTHH:mm:ssZ format
- source_url: Must be valid URL from groww.in domain

## Error Handling

### Missing Required Field
```json
{
  "error": "missing_required_field",
  "field": "expense_ratio",
  "message": "Required field 'expense_ratio' is missing"
}
```

### Type Mismatch
```json
{
  "error": "type_mismatch",
  "field": "expense_ratio",
  "expected": "float",
  "received": "string",
  "message": "Field 'expense_ratio' expected float but received string"
}
```

### Range Violation
```json
{
  "error": "range_violation",
  "field": "expense_ratio",
  "value": 6.5,
  "min": 0.0,
  "max": 5.0,
  "message": "Field 'expense_ratio' value 6.5 is outside allowed range [0.0, 5.0]"
}
```

### Invalid Format
```json
{
  "error": "invalid_format",
  "field": "nav_date",
  "value": "08-05-2024",
  "expected_format": "YYYY-MM-DD",
  "message": "Field 'nav_date' has invalid format, expected YYYY-MM-DD"
}
```

## Versioning

### Format Version
- Current version: 1.0.0
- Versioning follows Semantic Versioning (SemVer)
- Major version: Breaking changes
- Minor version: Non-breaking additions
- Patch version: Bug fixes

### Backward Compatibility
- Changes that break backward compatibility require major version increment
- Additions of optional fields require minor version increment
- Bug fixes require patch version increment

### Migration Strategy
- Maintain format version in metadata
- Implement format version detection
- Provide migration scripts for format changes
- Document all format changes in changelog

## Storage Format

### File Format
- Primary format: JSON
- Encoding: UTF-8
- File extension: .json
- Compression: Optional (gzip)

### Directory Structure
```
data/
├── extracted/
│   ├── axis_silver_fof.json
│   ├── axis_small_cap.json
│   ├── axis_flexi_cap.json
│   ├── axis_gold_fund.json
│   └── axis_defence_index.json
├── processed/
│   └── chunks/
└── metadata/
    └── extraction_log.json
```

### File Naming Convention
- Pattern: `{scheme_slug}.json`
- Example: `axis_flexi_cap.json`
- Slug generation: lowercase, hyphens for spaces

## Quality Checks

### Completeness Check
- All required fields present
- Optional fields populated where available
- No null values in required fields

### Consistency Check
- Scheme name matches across all sources
- Category and sub-category are consistent
- Financial data is internally consistent

### Accuracy Check
- Expense ratio within reasonable range
- NAV values are realistic
- AUM values are realistic
- Returns are within plausible ranges

### Freshness Check
- NAV date is recent (within 1 day)
- Last updated timestamp is recent
- Data is not stale

## References
- JSON Schema Specification: https://json-schema.org
- ISO 8601 Date Format: https://en.wikipedia.org/wiki/ISO_8601
- Semantic Versioning: https://semver.org
- Pydantic Validation: https://docs.pydantic.dev

---
**Document Version**: 1.0
**Last Updated**: 2024-05-08
**Status**: Approved
