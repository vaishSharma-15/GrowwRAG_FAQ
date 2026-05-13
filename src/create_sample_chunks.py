"""
Create Sample Chunks - Generates sample chunks for Phase 3 testing
Based on the 5 Axis Mutual Fund schemes
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scheme data based on Phase 1 documentation
SCHEMES = [
    {
        "name": "Axis Silver FoF Direct Growth",
        "code": "120555",
        "category": "Fund of Funds",
        "sub_category": "Commodities",
        "expense_ratio": 0.50,
        "exit_load": "Nil",
        "minimum_investment": 100,
        "sip_amount": 100,
        "nav": 22.3456,
        "nav_date": "2024-05-08",
        "risk_level": "Very High",
        "riskometer": "Very High (6/7)",
        "benchmark": "Silver Price",
        "aum": 1234.56,
        "fund_manager": "Hiral Mehta",
        "url": "https://groww.in/mutual-funds/axis-silver-fof-direct-growth"
    },
    {
        "name": "Axis Small Cap Fund Direct Growth",
        "code": "120503",
        "category": "Equity",
        "sub_category": "Small-cap",
        "expense_ratio": 0.85,
        "exit_load": "1% if redeemed within 15 days",
        "minimum_investment": 100,
        "sip_amount": 100,
        "nav": 78.9012,
        "nav_date": "2024-05-08",
        "risk_level": "Very High",
        "riskometer": "Very High (6/7)",
        "benchmark": "NIFTY Smallcap 250 - TRI",
        "aum": 8923.45,
        "fund_manager": "Anupam Tiwari",
        "url": "https://groww.in/mutual-funds/axis-small-cap-fund-direct-growth"
    },
    {
        "name": "Axis Flexi Cap Fund Direct Growth",
        "code": "120496",
        "category": "Equity",
        "sub_category": "Flexi-cap",
        "expense_ratio": 1.05,
        "exit_load": "1% if redeemed within 30 days, Nil after 30 days",
        "minimum_investment": 100,
        "sip_amount": 100,
        "nav": 45.6789,
        "nav_date": "2024-05-08",
        "risk_level": "Very High",
        "riskometer": "Very High (6/7)",
        "benchmark": "NIFTY 500 - TRI",
        "aum": 45678.90,
        "fund_manager": "Shreyash Deore",
        "url": "https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth"
    },
    {
        "name": "Axis Gold Fund Direct Growth",
        "code": "120551",
        "category": "Commodity",
        "sub_category": "Gold",
        "expense_ratio": 0.45,
        "exit_load": "Nil",
        "minimum_investment": 100,
        "sip_amount": 100,
        "nav": 18.7654,
        "nav_date": "2024-05-08",
        "risk_level": "High",
        "riskometer": "High (5/7)",
        "benchmark": "Gold Price",
        "aum": 3456.78,
        "fund_manager": "Hiral Mehta",
        "url": "https://groww.in/mutual-funds/axis-gold-fund-direct-growth"
    },
    {
        "name": "Axis Nifty India Defence Index Fund Direct Growth",
        "code": "120595",
        "category": "Index",
        "sub_category": "Thematic Index - Defence",
        "expense_ratio": 0.20,
        "exit_load": "Nil",
        "minimum_investment": 100,
        "sip_amount": 100,
        "nav": 15.4321,
        "nav_date": "2024-05-08",
        "risk_level": "Very High",
        "riskometer": "Very High (6/7)",
        "benchmark": "Nifty India Defence Index",
        "aum": 2345.67,
        "fund_manager": "Ashish Naik",
        "url": "https://groww.in/mutual-funds/axis-nifty-india-defence-index-fund-direct-growth"
    }
]


def create_chunks_for_scheme(scheme: dict) -> list:
    """Create multiple chunks for a scheme"""
    chunks = []
    base_id = scheme["code"]
    
    # Chunk 1: Basic Information
    chunks.append({
        "chunk_id": f"{base_id}_chunk_1",
        "chunk_text": f"Scheme Name: {scheme['name']}\nScheme Code: {scheme['code']}\nCategory: {scheme['category']}\nSub-Category: {scheme['sub_category']}\nFund Manager: {scheme['fund_manager']}",
        "chunk_index": 0,
        "chunk_type": "general",
        "metadata": {
            "source_url": scheme["url"],
            "scheme_name": scheme["name"],
            "scheme_code": scheme["code"],
            "category": scheme["category"],
            "sub_category": scheme["sub_category"],
            "document_type": "scheme_details",
            "last_updated": scheme["nav_date"],
            "chunked_at": datetime.utcnow().isoformat(),
            "chunking_version": "1.0.0"
        }
    })
    
    # Chunk 2: Financial Details
    chunks.append({
        "chunk_id": f"{base_id}_chunk_2",
        "chunk_text": f"Financial Details for {scheme['name']}:\nExpense Ratio: {scheme['expense_ratio']}%\nExit Load: {scheme['exit_load']}\nMinimum Investment: ₹{scheme['minimum_investment']}\nSIP Amount: ₹{scheme['sip_amount']}\nNAV: ₹{scheme['nav']}\nNAV Date: {scheme['nav_date']}",
        "chunk_index": 1,
        "chunk_type": "financial",
        "metadata": {
            "source_url": scheme["url"],
            "scheme_name": scheme["name"],
            "scheme_code": scheme["code"],
            "category": scheme["category"],
            "sub_category": scheme["sub_category"],
            "document_type": "scheme_details",
            "last_updated": scheme["nav_date"],
            "chunked_at": datetime.utcnow().isoformat(),
            "chunking_version": "1.0.0"
        }
    })
    
    # Chunk 3: Risk and Returns with Riskometer
    chunks.append({
        "chunk_id": f"{base_id}_chunk_3",
        "chunk_text": f"Risk and Returns for {scheme['name']}:\nRisk Level: {scheme['risk_level']}\nRiskometer: {scheme.get('riskometer', scheme['risk_level'])}\nBenchmark: {scheme['benchmark']}\nAUM: ₹{scheme['aum']} Crores",
        "chunk_index": 2,
        "chunk_type": "risk",
        "metadata": {
            "source_url": scheme["url"],
            "scheme_name": scheme["name"],
            "scheme_code": scheme["code"],
            "category": scheme["category"],
            "sub_category": scheme["sub_category"],
            "document_type": "scheme_details",
            "last_updated": scheme["nav_date"],
            "chunked_at": datetime.utcnow().isoformat(),
            "chunking_version": "1.0.0"
        }
    })
    
    return chunks


def create_investor_services_chunks() -> list:
    """Create chunks for investor services and general information"""
    chunks = []
    
    # ELSS Information
    chunks.append({
        "chunk_id": "elss_info_1",
        "chunk_text": "ELSS (Equity Linked Savings Scheme) Lock-in Period:\nELSS mutual funds have a mandatory lock-in period of 3 years from the date of investment.\nThis means you cannot redeem or switch your ELSS units before 3 years.\nELSS investments qualify for tax deduction under Section 80C of the Income Tax Act up to ₹1.5 lakhs per financial year.",
        "chunk_index": 0,
        "chunk_type": "faq",
        "metadata": {
            "source_url": "https://groww.in/mutual-funds",
            "scheme_name": "General ELSS Information",
            "scheme_code": "N/A",
            "category": "Tax Saver",
            "sub_category": "ELSS",
            "document_type": "investor_education",
            "last_updated": "2024-05-08",
            "chunked_at": datetime.utcnow().isoformat(),
            "chunking_version": "1.0.0"
        }
    })
    
    # Statement Download Process
    chunks.append({
        "chunk_id": "investor_services_1",
        "chunk_text": "To download statements or capital gains reports of any Axis Mutual Fund, visit axismf.com, login to your account, and navigate to \"Capital Gains Statement\" or \"Account Statement\". Select the financial year and your folio number(s) to download the report in PDF format.",
        "chunk_index": 1,
        "chunk_type": "faq",
        "metadata": {
            "source_url": "https://axismf.com",
            "scheme_name": "Investor Services",
            "scheme_code": "N/A",
            "category": "Service",
            "sub_category": "Statement Download",
            "document_type": "process_guide",
            "last_updated": "2024-05-08",
            "chunked_at": datetime.utcnow().isoformat(),
            "chunking_version": "1.0.0"
        }
    })
    
    # Capital Gains Report
    chunks.append({
        "chunk_id": "investor_services_2",
        "chunk_text": "To download statements or capital gains reports of any Axis Mutual Fund, visit axismf.com, login to your account, and navigate to \"Capital Gains Statement\" or \"Account Statement\". Select the financial year and your folio number(s) to download the report in PDF format.",
        "chunk_index": 2,
        "chunk_type": "faq",
        "metadata": {
            "source_url": "https://axismf.com",
            "scheme_name": "Investor Services",
            "scheme_code": "N/A",
            "category": "Service",
            "sub_category": "Capital Gains Report",
            "document_type": "process_guide",
            "last_updated": "2024-05-08",
            "chunked_at": datetime.utcnow().isoformat(),
            "chunking_version": "1.0.0"
        }
    })
    
    return chunks


def create_sample_chunks():
    """Create sample chunks for all schemes plus investor services"""
    output_dir = Path("data/processed/chunks")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_chunks = []
    
    # Create scheme chunks
    for scheme in SCHEMES:
        chunks = create_chunks_for_scheme(scheme)
        all_chunks.extend(chunks)
        
        # Save per scheme
        scheme_slug = scheme["name"].lower().replace(" ", "_").replace("-", "_")
        scheme_file = output_dir / f"{scheme_slug}_chunks.json"
        
        with open(scheme_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created {len(chunks)} chunks for {scheme['name']}")
    
    # Create investor services chunks
    investor_services_chunks = create_investor_services_chunks()
    all_chunks.extend(investor_services_chunks)
    
    # Save investor services chunks
    investor_file = output_dir / "investor_services_chunks.json"
    with open(investor_file, 'w', encoding='utf-8') as f:
        json.dump(investor_services_chunks, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Created {len(investor_services_chunks)} investor services chunks")
    
    # Save all chunks combined
    all_chunks_file = output_dir / "all_chunks.json"
    with open(all_chunks_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Total chunks created: {len(all_chunks)}")
    logger.info(f"Chunks saved to: {output_dir}")
    
    return all_chunks


if __name__ == "__main__":
    create_sample_chunks()
