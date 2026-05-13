"""
HTML Parser Module - Parses extracted HTML using BeautifulSoup
Extracts scheme data using CSS selectors
"""

import logging
from typing import Dict, Optional, Any
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class HTMLParser:
    """Parses HTML content to extract mutual fund scheme data"""
    
    def __init__(self):
        """Initialize the HTML parser"""
        self.selectors = self._get_default_selectors()
    
    def _get_default_selectors(self) -> Dict[str, str]:
        """
        Get default CSS selectors for common scheme data fields
        
        Returns:
            Dictionary mapping field names to CSS selectors
        """
        return {
            "scheme_name": [".scheme-name", "h1.schemeTitle", ".fund-name"],
            "scheme_code": [".scheme-code", ".fund-code"],
            "category": [".category", ".fund-category"],
            "sub_category": [".sub-category", ".fund-subcategory"],
            "expense_ratio": [".expense-ratio", ".expenseRatio"],
            "exit_load": [".exit-load", ".exitLoad"],
            "minimum_investment": [".minimum-investment", ".minInvestment"],
            "sip_amount": [".sip-amount", ".sipAmount"],
            "nav": [".nav-value", ".nav", ".current-nav"],
            "nav_date": [".nav-date", ".navDate"],
            "risk_level": [".riskometer", ".risk-level", ".riskLabel"],
            "benchmark": [".benchmark", ".benchmarkIndex"],
            "fund_manager": [".fund-manager", ".fundManager"],
            "aum": [".aum", ".fund-aum"],
        }
    
    def parse(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Parse HTML content and extract scheme data
        
        Args:
            html_content: HTML content as string
            url: Source URL for metadata
        
        Returns:
            Dictionary containing extracted scheme data
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            extracted_data = {
                "source_url": url,
                "scheme_info": {},
                "financial_details": {},
                "risk_and_returns": {},
                "fund_management": {},
                "portfolio": {},
                "metadata": {}
            }
            
            # Extract scheme information
            extracted_data["scheme_info"] = self._extract_scheme_info(soup)
            
            # Extract financial details
            extracted_data["financial_details"] = self._extract_financial_details(soup)
            
            # Extract risk and returns
            extracted_data["risk_and_returns"] = self._extract_risk_and_returns(soup)
            
            # Extract fund management
            extracted_data["fund_management"] = self._extract_fund_management(soup)
            
            # Extract portfolio (optional)
            extracted_data["portfolio"] = self._extract_portfolio(soup)
            
            # Add metadata
            extracted_data["metadata"] = {
                "source_url": url,
                "extraction_method": "headless_browser",
                "extraction_version": "1.0.0"
            }
            
            logger.info(f"Successfully parsed HTML from {url}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Failed to parse HTML from {url}: {e}")
            raise
    
    def _extract_scheme_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract scheme information"""
        scheme_info = {}
        
        scheme_info["scheme_name"] = self._extract_with_fallback(
            soup, self.selectors["scheme_name"]
        )
        scheme_info["scheme_code"] = self._extract_with_fallback(
            soup, self.selectors["scheme_code"]
        )
        scheme_info["amc"] = "Axis Mutual Fund"  # Fixed for this project
        scheme_info["category"] = self._extract_with_fallback(
            soup, self.selectors["category"]
        )
        scheme_info["sub_category"] = self._extract_with_fallback(
            soup, self.selectors["sub_category"]
        )
        scheme_info["plan_type"] = "Direct Growth"  # Fixed for this project
        
        return scheme_info
    
    def _extract_financial_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract financial details"""
        financial_details = {}
        
        expense_ratio_str = self._extract_with_fallback(
            soup, self.selectors["expense_ratio"]
        )
        financial_details["expense_ratio"] = self._parse_percentage(expense_ratio_str)
        
        financial_details["exit_load"] = self._extract_with_fallback(
            soup, self.selectors["exit_load"]
        )
        
        min_investment_str = self._extract_with_fallback(
            soup, self.selectors["minimum_investment"]
        )
        financial_details["minimum_investment"] = self._parse_integer(min_investment_str)
        
        sip_amount_str = self._extract_with_fallback(
            soup, self.selectors["sip_amount"]
        )
        financial_details["sip_amount"] = self._parse_integer(sip_amount_str)
        
        nav_str = self._extract_with_fallback(soup, self.selectors["nav"])
        financial_details["nav"] = self._parse_float(nav_str)
        
        financial_details["nav_date"] = self._extract_with_fallback(
            soup, self.selectors["nav_date"]
        )
        
        return financial_details
    
    def _extract_risk_and_returns(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract risk and returns information"""
        risk_and_returns = {}
        
        risk_and_returns["risk_level"] = self._extract_with_fallback(
            soup, self.selectors["risk_level"]
        )
        
        risk_and_returns["benchmark"] = self._extract_with_fallback(
            soup, self.selectors["benchmark"]
        )
        
        aum_str = self._extract_with_fallback(soup, self.selectors["aum"])
        risk_and_returns["aum"] = self._parse_float(aum_str)
        
        # Returns are optional and may not be present
        risk_and_returns["returns"] = {}
        
        return risk_and_returns
    
    def _extract_fund_management(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract fund management information"""
        fund_management = {}
        
        fund_management["fund_manager"] = self._extract_with_fallback(
            soup, self.selectors["fund_manager"]
        )
        
        return fund_management
    
    def _extract_portfolio(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract portfolio information (optional)"""
        # This is a placeholder - actual implementation depends on HTML structure
        return {
            "holdings": [],
            "sector_allocation": {},
            "asset_allocation": {}
        }
    
    def _extract_with_fallback(self, soup: BeautifulSoup, selectors: list[str]) -> Optional[str]:
        """
        Extract text using multiple selector options with fallback
        
        Args:
            soup: BeautifulSoup object
            selectors: List of CSS selectors to try
        
        Returns:
            Extracted text or None if not found
        """
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text:
                    return text
        return None
    
    def _parse_percentage(self, value: Optional[str]) -> Optional[float]:
        """Parse percentage string to float"""
        if not value:
            return None
        try:
            # Remove % sign and convert to float
            cleaned = re.sub(r'[^\d.]', '', value)
            return float(cleaned) if cleaned else None
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse percentage: {value}")
            return None
    
    def _parse_float(self, value: Optional[str]) -> Optional[float]:
        """Parse string to float"""
        if not value:
            return None
        try:
            # Remove commas and convert to float
            cleaned = re.sub(r'[^\d.]', '', value)
            return float(cleaned) if cleaned else None
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse float: {value}")
            return None
    
    def _parse_integer(self, value: Optional[str]) -> Optional[int]:
        """Parse string to integer"""
        if not value:
            return None
        try:
            # Remove commas and convert to integer
            cleaned = re.sub(r'[^\d]', '', value)
            return int(cleaned) if cleaned else None
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse integer: {value}")
            return None
