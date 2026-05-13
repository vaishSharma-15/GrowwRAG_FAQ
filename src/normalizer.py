"""
Data Normalizer Module - Normalizes and cleans extracted data
Handles text formatting, numerical data normalization, and special characters
"""

import logging
import re
import unicodedata
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DataNormalizer:
    """Normalizes and cleans extracted mutual fund scheme data"""
    
    def __init__(self):
        """Initialize the data normalizer"""
        self.category_mapping = {
            "equity": "Equity",
            "debt": "Debt",
            "hybrid": "Hybrid",
            "commodity": "Commodity",
            "index": "Index",
            "fund of funds": "Fund of Funds",
            "fof": "Fund of Funds"
        }
        
        self.risk_level_mapping = {
            "low": "Low",
            "low to moderate": "Low to Moderate",
            "moderate": "Moderate",
            "moderately high": "Moderately High",
            "high": "High",
            "very high": "Very High"
        }
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize extracted data
        
        Args:
            data: Raw extracted data dictionary
        
        Returns:
            Normalized data dictionary
        """
        try:
            normalized_data = data.copy()
            
            # Normalize scheme information
            if "scheme_info" in normalized_data:
                normalized_data["scheme_info"] = self._normalize_scheme_info(
                    normalized_data["scheme_info"]
                )
            
            # Normalize financial details
            if "financial_details" in normalized_data:
                normalized_data["financial_details"] = self._normalize_financial_details(
                    normalized_data["financial_details"]
                )
            
            # Normalize risk and returns
            if "risk_and_returns" in normalized_data:
                normalized_data["risk_and_returns"] = self._normalize_risk_and_returns(
                    normalized_data["risk_and_returns"]
                )
            
            # Normalize fund management
            if "fund_management" in normalized_data:
                normalized_data["fund_management"] = self._normalize_fund_management(
                    normalized_data["fund_management"]
                )
            
            # Add timestamps
            if "metadata" in normalized_data:
                normalized_data["metadata"]["extracted_at"] = datetime.utcnow().isoformat()
                normalized_data["metadata"]["last_updated"] = datetime.utcnow().strftime("%Y-%m-%d")
            
            logger.info("Data normalization completed successfully")
            return normalized_data
            
        except Exception as e:
            logger.error(f"Failed to normalize data: {e}")
            raise
    
    def _normalize_scheme_info(self, scheme_info: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize scheme information"""
        normalized = scheme_info.copy()
        
        # Normalize scheme name
        if "scheme_name" in normalized and normalized["scheme_name"]:
            normalized["scheme_name"] = self._clean_text(normalized["scheme_name"])
            normalized["scheme_name"] = self._to_title_case(normalized["scheme_name"])
        
        # Normalize scheme code
        if "scheme_code" in normalized and normalized["scheme_code"]:
            normalized["scheme_code"] = self._clean_text(normalized["scheme_code"]).upper()
        
        # Normalize category
        if "category" in normalized and normalized["category"]:
            normalized["category"] = self._normalize_category(normalized["category"])
        
        # Normalize sub-category
        if "sub_category" in normalized and normalized["sub_category"]:
            normalized["sub_category"] = self._clean_text(normalized["sub_category"])
            normalized["sub_category"] = self._to_title_case(normalized["sub_category"])
        
        # Normalize AMC
        if "amc" in normalized and normalized["amc"]:
            normalized["amc"] = self._clean_text(normalized["amc"])
            normalized["amc"] = self._to_title_case(normalized["amc"])
        
        # Normalize plan type
        if "plan_type" in normalized and normalized["plan_type"]:
            normalized["plan_type"] = self._clean_text(normalized["plan_type"])
            normalized["plan_type"] = self._to_title_case(normalized["plan_type"])
        
        return normalized
    
    def _normalize_financial_details(self, financial_details: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize financial details"""
        normalized = financial_details.copy()
        
        # Normalize expense ratio
        if "expense_ratio" in normalized and normalized["expense_ratio"] is not None:
            normalized["expense_ratio"] = self._normalize_expense_ratio(
                normalized["expense_ratio"]
            )
        
        # Normalize exit load
        if "exit_load" in normalized and normalized["exit_load"]:
            normalized["exit_load"] = self._clean_text(normalized["exit_load"])
        
        # Normalize minimum investment
        if "minimum_investment" in normalized and normalized["minimum_investment"] is not None:
            normalized["minimum_investment"] = self._normalize_integer(
                normalized["minimum_investment"]
            )
        
        # Normalize SIP amount
        if "sip_amount" in normalized and normalized["sip_amount"] is not None:
            normalized["sip_amount"] = self._normalize_integer(normalized["sip_amount"])
        
        # Normalize NAV
        if "nav" in normalized and normalized["nav"] is not None:
            normalized["nav"] = self._normalize_float(normalized["nav"])
        
        # Normalize NAV date
        if "nav_date" in normalized and normalized["nav_date"]:
            normalized["nav_date"] = self._normalize_date(normalized["nav_date"])
        
        return normalized
    
    def _normalize_risk_and_returns(self, risk_and_returns: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize risk and returns information"""
        normalized = risk_and_returns.copy()
        
        # Normalize risk level
        if "risk_level" in normalized and normalized["risk_level"]:
            normalized["risk_level"] = self._normalize_risk_level(normalized["risk_level"])
        
        # Normalize benchmark
        if "benchmark" in normalized and normalized["benchmark"]:
            normalized["benchmark"] = self._clean_text(normalized["benchmark"])
            normalized["benchmark"] = self._to_title_case(normalized["benchmark"])
        
        # Normalize AUM
        if "aum" in normalized and normalized["aum"] is not None:
            normalized["aum"] = self._normalize_float(normalized["aum"])
        
        # Normalize returns
        if "returns" in normalized and isinstance(normalized["returns"], dict):
            normalized["returns"] = self._normalize_returns(normalized["returns"])
        
        return normalized
    
    def _normalize_fund_management(self, fund_management: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize fund management information"""
        normalized = fund_management.copy()
        
        # Normalize fund manager
        if "fund_manager" in normalized and normalized["fund_manager"]:
            normalized["fund_manager"] = self._clean_text(normalized["fund_manager"])
            normalized["fund_manager"] = self._to_title_case(normalized["fund_manager"])
        
        # Normalize fund manager experience
        if "fund_manager_experience" in normalized and normalized["fund_manager_experience"]:
            normalized["fund_manager_experience"] = self._clean_text(
                normalized["fund_manager_experience"]
            )
        
        return normalized
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and special characters
        
        Args:
            text: Input text string
        
        Returns:
            Cleaned text string
        """
        if not isinstance(text, str):
            return str(text)
        
        # Unicode normalization
        text = unicodedata.normalize('NFC', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _to_title_case(self, text: str) -> str:
        """
        Convert text to title case
        
        Args:
            text: Input text string
        
        Returns:
            Title case text string
        """
        if not isinstance(text, str):
            return str(text)
        
        # Capitalize first letter of each word
        return ' '.join(word.capitalize() for word in text.split())
    
    def _normalize_category(self, category: str) -> str:
        """
        Normalize category to standard format
        
        Args:
            category: Category string
        
        Returns:
            Normalized category string
        """
        if not isinstance(category, str):
            return str(category)
        
        category_lower = category.lower().strip()
        
        # Use mapping if available
        if category_lower in self.category_mapping:
            return self.category_mapping[category_lower]
        
        # Default to title case
        return self._to_title_case(category)
    
    def _normalize_risk_level(self, risk_level: str) -> str:
        """
        Normalize risk level to standard format
        
        Args:
            risk_level: Risk level string
        
        Returns:
            Normalized risk level string
        """
        if not isinstance(risk_level, str):
            return str(risk_level)
        
        risk_lower = risk_level.lower().strip()
        
        # Use mapping if available
        if risk_lower in self.risk_level_mapping:
            return self.risk_level_mapping[risk_lower]
        
        # Default to title case
        return self._to_title_case(risk_level)
    
    def _normalize_expense_ratio(self, value: Any) -> Optional[float]:
        """
        Normalize expense ratio to float
        
        Args:
            value: Expense ratio value (string or float)
        
        Returns:
            Normalized expense ratio as float or None
        """
        if value is None:
            return None
        
        try:
            if isinstance(value, (int, float)):
                return float(value)
            
            if isinstance(value, str):
                # Remove % sign and convert
                cleaned = re.sub(r'[^\d.]', '', value)
                if cleaned:
                    return float(cleaned)
            
            return None
        except (ValueError, TypeError):
            logger.warning(f"Failed to normalize expense ratio: {value}")
            return None
    
    def _normalize_float(self, value: Any) -> Optional[float]:
        """
        Normalize value to float
        
        Args:
            value: Value to normalize (string or float)
        
        Returns:
            Normalized value as float or None
        """
        if value is None:
            return None
        
        try:
            if isinstance(value, (int, float)):
                return float(value)
            
            if isinstance(value, str):
                # Remove commas and convert
                cleaned = re.sub(r'[^\d.]', '', value)
                if cleaned:
                    return float(cleaned)
            
            return None
        except (ValueError, TypeError):
            logger.warning(f"Failed to normalize float: {value}")
            return None
    
    def _normalize_integer(self, value: Any) -> Optional[int]:
        """
        Normalize value to integer
        
        Args:
            value: Value to normalize (string or int)
        
        Returns:
            Normalized value as integer or None
        """
        if value is None:
            return None
        
        try:
            if isinstance(value, int):
                return value
            
            if isinstance(value, float):
                return int(value)
            
            if isinstance(value, str):
                # Remove commas and convert
                cleaned = re.sub(r'[^\d]', '', value)
                if cleaned:
                    return int(cleaned)
            
            return None
        except (ValueError, TypeError):
            logger.warning(f"Failed to normalize integer: {value}")
            return None
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """
        Normalize date string to ISO 8601 format (YYYY-MM-DD)
        
        Args:
            date_str: Date string in various formats
        
        Returns:
            Normalized date string in ISO 8601 format or None
        """
        if not isinstance(date_str, str):
            return None
        
        date_formats = [
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%b %d, %Y",
            "%B %d, %Y",
            "%d-%b-%Y",
            "%d-%B-%Y"
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        logger.warning(f"Failed to normalize date: {date_str}")
        return None
    
    def _normalize_returns(self, returns: Dict[str, Any]) -> Dict[str, Optional[float]]:
        """
        Normalize returns dictionary
        
        Args:
            returns: Returns dictionary with percentage strings or floats
        
        Returns:
            Normalized returns dictionary with float values
        """
        normalized = {}
        
        for period, value in returns.items():
            if value is not None:
                normalized[period] = self._normalize_float(value)
            else:
                normalized[period] = None
        
        return normalized
