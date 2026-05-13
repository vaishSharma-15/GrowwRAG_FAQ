# Curated URL List with Metadata

## Overview
This document contains the curated list of source URLs for the Mutual Fund FAQ Assistant project. These URLs are the **ONLY** sources that will be used for this project.

## Important Note
**These 5 URLs are the EXCLUSIVE data sources for this project. No additional URLs from AMC, AMFI, or SEBI will be used.**

## Source URLs

### URL 1
| Field | Value |
|-------|-------|
| **URL** | https://groww.in/mutual-funds/axis-silver-fof-direct-growth |
| **Scheme Name** | Axis Silver FoF Direct Growth |
| **Category** | Fund of Funds - Commodities |
| **Sub-Category** | Silver FoF |
| **Plan Type** | Direct Growth |
| **AMC** | Axis Mutual Fund |
| **Document Type** | Scheme Information Page |
| **Source Platform** | Groww |
| **Last Validated** | 2024-05-08 |
| **Status** | Active |

### URL 2
| Field | Value |
|-------|-------|
| **URL** | https://groww.in/mutual-funds/axis-small-cap-fund-direct-growth |
| **Scheme Name** | Axis Small Cap Fund Direct Growth |
| **Category** | Equity |
| **Sub-Category** | Small-cap |
| **Plan Type** | Direct Growth |
| **AMC** | Axis Mutual Fund |
| **Document Type** | Scheme Information Page |
| **Source Platform** | Groww |
| **Last Validated** | 2024-05-08 |
| **Status** | Active |

### URL 3
| Field | Value |
|-------|-------|
| **URL** | https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth |
| **Scheme Name** | Axis Flexi Cap Fund Direct Growth |
| **Category** | Equity |
| **Sub-Category** | Flexi-cap |
| **Plan Type** | Direct Growth |
| **AMC** | Axis Mutual Fund |
| **Document Type** | Scheme Information Page |
| **Source Platform** | Groww |
| **Last Validated** | 2024-05-08 |
| **Status** | Active |

### URL 4
| Field | Value |
|-------|-------|
| **URL** | https://groww.in/mutual-funds/axis-gold-fund-direct-growth |
| **Scheme Name** | Axis Gold Fund Direct Growth |
| **Category** | Commodity |
| **Sub-Category** | Gold |
| **Plan Type** | Direct Growth |
| **AMC** | Axis Mutual Fund |
| **Document Type** | Scheme Information Page |
| **Source Platform** | Groww |
| **Last Validated** | 2024-05-08 |
| **Status** | Active |

### URL 5
| Field | Value |
|-------|-------|
| **URL** | https://groww.in/mutual-funds/axis-nifty-india-defence-index-fund-direct-growth |
| **Scheme Name** | Axis Nifty India Defence Index Fund Direct Growth |
| **Category** | Index |
| **Sub-Category** | Thematic Index - Defence |
| **Plan Type** | Direct Growth |
| **AMC** | Axis Mutual Fund |
| **Document Type** | Scheme Information Page |
| **Source Platform** | Groww |
| **Last Validated** | 2024-05-08 |
| **Status** | Active |

## Metadata Summary

### Category Distribution
| Category | Count | URLs |
|----------|-------|------|
| Fund of Funds | 1 | Axis Silver FoF |
| Equity | 2 | Axis Small Cap, Axis Flexi Cap |
| Commodity | 1 | Axis Gold Fund |
| Index | 1 | Axis Nifty India Defence Index |

### Risk Level Distribution
| Risk Level | Count | Schemes |
|------------|-------|---------|
| Very High | 4 | Axis Silver FoF, Axis Small Cap, Axis Flexi Cap, Axis Nifty India Defence Index |
| High | 1 | Axis Gold Fund |

### Expected Data Points per URL
Each URL is expected to contain the following information:
- Scheme name and code
- Category and sub-category
- Expense ratio
- Exit load structure
- Minimum investment amount
- SIP details
- NAV history
- Riskometer level
- Benchmark index
- Fund manager information
- Portfolio holdings
- Performance metrics

## Source Platform Information

### Groww Platform Details
- **Platform**: Groww (https://groww.in)
- **Type**: Mutual Fund Aggregator Platform
- **Access Method**: Web scraping (respecting robots.txt)
- **Content Type**: HTML pages with dynamic content
- **Authentication**: Not required for public scheme pages
- **Rate Limiting**: To be implemented in scraper
- **Terms of Use**: Must be reviewed and complied with

## Extraction Considerations

### Dynamic Content Handling
- Some content may load dynamically via JavaScript
- May require headless browser (Selenium/Playwright)
- API endpoints may be available for data extraction

### HTML Structure
- Each URL may have different HTML structure
- Need flexible CSS selectors for data extraction
- Schema validation required for extracted data

### Data Freshness
- NAV values update daily
- Scheme details may change periodically
- Need timestamp tracking for extracted data
- Implement regular data refresh schedule

## Compliance Notes

### robots.txt Compliance
- Must check and respect Groww's robots.txt
- Implement appropriate delays between requests
- User agent identification

### Terms of Service
- Review Groww's Terms of Service
- Ensure compliance with data usage policies
- No unauthorized scraping of user data

### Fair Use
- Extract only publicly available information
- Do not overload servers with excessive requests
- Implement caching to minimize repeated requests

## URL Maintenance

### Validation Schedule
- Weekly URL accessibility check
- Monthly content structure validation
- Quarterly terms of service review

### Change Management
- Monitor for URL structure changes
- Alert on 404 or access errors
- Document any changes in URL patterns

### Backup Strategy
- Store extracted data locally
- Maintain version history of extracted content
- Implement fallback procedures if URLs become unavailable

## References
- Groww Terms of Service: https://groww.in/terms
- Groww Privacy Policy: https://groww.in/privacy
- robots.txt: https://groww.in/robots.txt

---
**Document Version**: 1.0
**Last Updated**: 2024-05-08
**Status**: Approved
**Total URLs**: 5
