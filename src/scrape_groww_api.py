"""
Scraper using requests + regex for Groww
Tries multiple extraction methods for robustness
"""

import requests
import re
import json
from datetime import datetime
from pathlib import Path

SCHEMES = [
    {
        "code": "120496",
        "name": "Axis Flexi Cap Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth",
        "category": "Equity",
        "sub_category": "Flexi-cap"
    },
    {
        "code": "120503", 
        "name": "Axis Small Cap Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/axis-small-cap-fund-direct-growth",
        "category": "Equity",
        "sub_category": "Small-cap"
    },
    {
        "code": "120555",
        "name": "Axis Silver FoF Direct Growth", 
        "url": "https://groww.in/mutual-funds/axis-silver-fof-direct-growth",
        "category": "Fund of Funds",
        "sub_category": "Commodities"
    },
    {
        "code": "120551",
        "name": "Axis Gold Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/axis-gold-fund-direct-growth",
        "category": "Commodity",
        "sub_category": "Gold"
    },
    {
        "code": "120595",
        "name": "Axis Nifty India Defence Index Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/axis-nifty-india-defence-index-fund-direct-growth",
        "category": "Index",
        "sub_category": "Thematic Index - Defence"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def extract_nav(html: str) -> float:
    """Extract NAV from HTML - try multiple patterns"""
    # Pattern 1: Look for script data
    nav_match = re.search(r'\"nav\":\s*([\d.]+)', html)
    if nav_match:
        return float(nav_match.group(1))
    
    # Pattern 2: Look for NAV in text
    nav_match = re.search(r'NAV.*?₹\s*([\d.]+)', html, re.I)
    if nav_match:
        nav = float(nav_match.group(1))
        if 10 < nav < 1000:
            return nav
    
    # Pattern 3: Look for any rupee value in first 1000 chars
    first_part = html[:10000]
    rupee_matches = re.findall(r'₹\s*([\d]{2,3}\.\d{2})', first_part)
    for match in rupee_matches:
        nav = float(match)
        if 10 < nav < 1000:
            return nav
    
    return None


def extract_expense_ratio(html: str) -> float:
    """Extract expense ratio from HTML"""
    # Pattern 1: JSON data
    exp_match = re.search(r'\"expenseRatio\":\s*([\d.]+)', html)
    if exp_match:
        return float(exp_match.group(1))
    
    # Pattern 2: Text search
    exp_match = re.search(r'Expense\s*Ratio.*?([\d.]+)\s*%', html, re.I)
    if exp_match:
        expense = float(exp_match.group(1))
        if 0.1 <= expense <= 3.0:
            return expense
    
    # Pattern 3: Look for percentage after expense
    exp_match = re.search(r'(?:expense|Expense).*?([\d.]+)%', html)
    if exp_match:
        expense = float(exp_match.group(1))
        if 0.1 <= expense <= 3.0:
            return expense
    
    return None


def extract_aum(html: str) -> float:
    """Extract AUM from HTML"""
    # Pattern 1: JSON data
    aum_match = re.search(r'\"aum\":\s*([\d,]+\.?\d*)', html)
    if aum_match:
        return float(aum_match.group(1).replace(',', ''))
    
    # Pattern 2: Text with Cr/Crore
    aum_match = re.search(r'AUM.*?₹?\s*([\d,\.]+)\s*(?:Cr|Crore)', html, re.I)
    if aum_match:
        return float(aum_match.group(1).replace(',', ''))
    
    return None


def scrape_scheme(scheme: dict) -> dict:
    """Scrape single scheme"""
    print(f"\n🔍 {scheme['name']}")
    
    result = {
        "name": scheme["name"],
        "code": scheme["code"],
        "category": scheme["category"],
        "sub_category": scheme["sub_category"],
        "url": scheme["url"],
        "nav": None,
        "nav_date": datetime.now().strftime("%Y-%m-%d"),
        "expense_ratio": None,
        "exit_load": None,
        "minimum_investment": 100,
        "sip_amount": 100,
        "risk_level": "Very High",
        "riskometer": "Very High",
        "benchmark": None,
        "aum": None,
        "fund_manager": None,
        "scraped_at": datetime.now().isoformat()
    }
    
    try:
        response = requests.get(scheme["url"], headers=HEADERS, timeout=30)
        response.raise_for_status()
        html = response.text
        
        # Extract data
        result["nav"] = extract_nav(html)
        result["expense_ratio"] = extract_expense_ratio(html)
        result["aum"] = extract_aum(html)
        
        # Try to get benchmark from text
        if "NIFTY" in html.upper():
            benchmark_match = re.search(r'(NIFTY[^<\"\']{5,50})', html, re.I)
            if benchmark_match:
                result["benchmark"] = benchmark_match.group(1).strip()[:50]
        
        # Default values if extraction failed
        if not result["benchmark"]:
            benchmarks = {
                "120496": "NIFTY 500 Total Return Index",
                "120503": "NIFTY Smallcap 250 Total Return Index",
                "120555": "Domestic Price of Silver",
                "120551": "Domestic Price of Gold",
                "120595": "Nifty India Defence Index"
            }
            result["benchmark"] = benchmarks.get(scheme["code"])
        
        # Fund manager defaults
        fund_managers = {
            "120496": "Krishnaa N, Sachin Relekar, Hitesh Das",
            "120503": "Tejas Sheth, Mayank Hyanki, Krishnaa N",
            "120555": "Aditya Pagaria, Pratik Tibrewal",
            "120551": "Aditya Pagaria, Pratik Tibrewal",
            "120595": "Nandik Mallik, Rohit Gautam"
        }
        result["fund_manager"] = fund_managers.get(scheme["code"])
        
        # Exit load defaults
        exit_loads = {
            "120496": "1% for redemption within 365 days, Nil after 365 days",
            "120503": "1% for redemption within 365 days, Nil after 365 days",
            "120555": "0.50% for redemption within 90 days, Nil after 90 days",
            "120551": "Nil",
            "120595": "0.50% for redemption within 90 days, Nil after 90 days"
        }
        result["exit_load"] = exit_loads.get(scheme["code"])
        
        print(f"  NAV: ₹{result['nav']}")
        print(f"  Expense: {result['expense_ratio']}%")
        print(f"  AUM: ₹{result['aum']} Cr")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    return result


def main():
    """Scrape all schemes"""
    print("=" * 70)
    print("🔄 Scraping Current Data from Groww")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    for scheme in SCHEMES:
        data = scrape_scheme(scheme)
        results.append(data)
        import time
        time.sleep(1)  # Be nice to server
    
    # Save results
    output_dir = Path("data/extracted")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "groww_current_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print(f"✅ Scraping Complete!")
    print(f"Saved to: {output_file}")
    print("=" * 70)
    
    # Summary
    print("\n📊 Summary:")
    for r in results:
        status = "✓" if r["nav"] and r["expense_ratio"] else "⚠"
        print(f"  {status} {r['name'][:40]:40} NAV: ₹{r['nav']:>6} Exp: {r['expense_ratio']}%")
    
    return results


if __name__ == "__main__":
    main()
