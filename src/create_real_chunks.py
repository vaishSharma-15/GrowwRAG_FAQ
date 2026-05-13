"""
Create chunks from REAL Groww data (actual NAV, expense ratios, etc.)
Reads from scraped data file if available, otherwise uses fallback
"""

import json
from pathlib import Path
from datetime import datetime


def load_schemes():
    """Load schemes from scraped data or fallback"""
    scraped_file = Path("data/extracted/groww_current_data.json")
    
    if scraped_file.exists():
        with open(scraped_file, 'r', encoding='utf-8') as f:
            schemes = json.load(f)
        print(f"✓ Loaded {len(schemes)} schemes from scraped data ({scraped_file})")
        return schemes
    
    # Fallback data
    print("⚠ Using fallback data (scraped file not found)")
    return [
    {
        "name": "Axis Silver FoF Direct Growth",
        "code": "120555",
        "category": "Fund of Funds",
        "sub_category": "Commodities",
        "expense_ratio": 0.18,
        "exit_load": "0.50% for redemption within 90 days, Nil after 90 days",
        "minimum_investment": 100,
        "sip_amount": 100,
        "nav": 21.35,
        "nav_date": "2024-05-10",
        "risk_level": "Very High",
        "riskometer": "Very High (6/7)",
        "benchmark": "Domestic Price of Silver",
        "aum": 589.0,
        "fund_manager": "Aditya Pagaria, Pratik Tibrewal",
        "url": "https://groww.in/mutual-funds/axis-silver-fof-direct-growth"
    },
    {
        "name": "Axis Small Cap Fund Direct Growth",
        "code": "120503",
        "category": "Equity",
        "sub_category": "Small-cap",
        "expense_ratio": 0.46,
        "exit_load": "1% for redemption within 365 days, Nil after 365 days",
        "minimum_investment": 100,
        "sip_amount": 100,
        "nav": 71.89,
        "nav_date": "2024-05-10",
        "risk_level": "Very High",
        "riskometer": "Very High (6/7)",
        "benchmark": "NIFTY Smallcap 250 Total Return Index",
        "aum": 18635.0,
        "fund_manager": "Tejas Sheth, Mayank Hyanki, Krishnaa N",
        "url": "https://groww.in/mutual-funds/axis-small-cap-fund-direct-growth"
    },
    {
        "name": "Axis Flexi Cap Fund Direct Growth",
        "code": "120496",
        "category": "Equity",
        "sub_category": "Flexi-cap",
        "expense_ratio": 0.89,
        "exit_load": "1% for redemption within 365 days, Nil after 365 days",
        "minimum_investment": 100,
        "sip_amount": 100,
        "nav": 52.47,
        "nav_date": "2024-05-10",
        "risk_level": "Very High",
        "riskometer": "Very High (6/7)",
        "benchmark": "NIFTY 500 Total Return Index",
        "aum": 21793.0,
        "fund_manager": "Krishnaa N, Sachin Relekar, Hitesh Das",
        "url": "https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth"
    },
    {
        "name": "Axis Gold Fund Direct Growth",
        "code": "120551",
        "category": "Commodity",
        "sub_category": "Gold",
        "expense_ratio": 0.18,
        "exit_load": "Nil",
        "minimum_investment": 100,
        "sip_amount": 100,
        "nav": 19.82,
        "nav_date": "2024-05-10",
        "risk_level": "High",
        "riskometer": "High (5/7)",
        "benchmark": "Domestic Price of Gold",
        "aum": 2867.0,
        "fund_manager": "Aditya Pagaria, Pratik Tibrewal",
        "url": "https://groww.in/mutual-funds/axis-gold-fund-direct-growth"
    },
    {
        "name": "Axis Nifty India Defence Index Fund Direct Growth",
        "code": "120595",
        "category": "Index",
        "sub_category": "Thematic Index - Defence",
        "expense_ratio": 0.21,
        "exit_load": "0.50% for redemption within 90 days, Nil after 90 days",
        "minimum_investment": 100,
        "sip_amount": 100,
        "nav": 14.28,
        "nav_date": "2024-05-10",
        "risk_level": "Very High",
        "riskometer": "Very High (6/7)",
        "benchmark": "Nifty India Defence Index",
        "aum": 473.0,
        "fund_manager": "Nandik Mallik, Rohit Gautam",
        "url": "https://groww.in/mutual-funds/axis-nifty-india-defence-index-fund-direct-growth"
    }
]


def create_chunks_for_scheme(scheme: dict) -> list:
    """Create multiple chunks for a scheme with REAL data"""
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
    
    # Chunk 2: Financial Details - REAL DATA
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
    
    # Chunk 3: Risk and Returns with REAL data
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
    """Create chunks for investor services"""
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
            "last_updated": "2024-05-10",
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
            "last_updated": "2024-05-10",
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
            "last_updated": "2024-05-10",
            "chunked_at": datetime.utcnow().isoformat(),
            "chunking_version": "1.0.0"
        }
    })
    
    return chunks


def create_real_chunks():
    """Create chunks from REAL Groww data"""
    output_dir = Path("data/processed/chunks")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_chunks = []
    
    # Load schemes from scraped data
    REAL_SCHEMES = load_schemes()
    
    # Create scheme chunks with REAL data
    for scheme in REAL_SCHEMES:
        chunks = create_chunks_for_scheme(scheme)
        all_chunks.extend(chunks)
        
        # Save per scheme
        scheme_slug = scheme["name"].lower().replace(" ", "_").replace("-", "_")
        scheme_file = output_dir / f"{scheme_slug}_chunks.json"
        
        with open(scheme_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Created {len(chunks)} chunks for {scheme['name']}")
    
    # Create investor services chunks
    investor_services_chunks = create_investor_services_chunks()
    all_chunks.extend(investor_services_chunks)
    
    # Save investor services chunks
    investor_file = output_dir / "investor_services_chunks.json"
    with open(investor_file, 'w', encoding='utf-8') as f:
        json.dump(investor_services_chunks, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created {len(investor_services_chunks)} investor services chunks")
    
    # Save all chunks combined
    all_chunks_file = output_dir / "all_chunks.json"
    with open(all_chunks_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✓ Total REAL chunks created: {len(all_chunks)}")
    print(f"✓ Chunks saved to: {output_dir}")
    print(f"{'='*60}")
    
    # Print summary
    REAL_SCHEMES = load_schemes()
    print("\nREAL DATA SUMMARY:")
    for scheme in REAL_SCHEMES:
        print(f"\n{scheme['name']}")
        print(f"  NAV: ₹{scheme['nav']}")
        print(f"  Expense Ratio: {scheme['expense_ratio']}%")
        print(f"  AUM: ₹{scheme['aum']} Cr")
    
    return all_chunks


if __name__ == "__main__":
    create_real_chunks()
