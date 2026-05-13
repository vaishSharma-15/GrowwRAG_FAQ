"""
Schema Validator Module - Validates extracted data using Pydantic
Ensures data quality and compliance with format specification
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class SchemeInfo(BaseModel):
    """Scheme information validation schema"""
    scheme_name: str = Field(..., min_length=1, max_length=200)
    scheme_code: str = Field(..., pattern=r'^[A-Z0-9]{6,7}$')
    amc: str = Field(default="Axis Mutual Fund")
    category: str = Field(...)
    sub_category: str = Field(..., min_length=1, max_length=100)
    plan_type: str = Field(default="Direct Growth")


class FinancialDetails(BaseModel):
    """Financial details validation schema"""
    expense_ratio: Optional[float] = Field(None, ge=0.0, le=5.0)
    exit_load: Optional[str] = Field(None, max_length=500)
    minimum_investment: Optional[int] = Field(None, ge=100)
    sip_amount: Optional[int] = Field(None, ge=100)
    nav: Optional[float] = Field(None, gt=0)
    nav_date: Optional[str] = None  # Will be validated separately


class Returns(BaseModel):
    """Returns validation schema"""
    one_year: Optional[float] = Field(None, ge=-100, le=100)
    three_year: Optional[float] = Field(None, ge=-100, le=100)
    five_year: Optional[float] = Field(None, ge=-100, le=100)


class RiskAndReturns(BaseModel):
    """Risk and returns validation schema"""
    risk_level: str = Field(...)
    benchmark: str = Field(..., min_length=1, max_length=200)
    aum: Optional[float] = Field(None, gt=0)
    returns: Optional[Returns] = None


class FundManagement(BaseModel):
    """Fund management validation schema"""
    fund_manager: str = Field(..., min_length=1, max_length=200)
    fund_manager_experience: Optional[str] = Field(None, max_length=100)


class Portfolio(BaseModel):
    """Portfolio validation schema"""
    holdings: list = Field(default_factory=list)
    sector_allocation: Dict[str, float] = Field(default_factory=dict)
    asset_allocation: Dict[str, float] = Field(default_factory=dict)


class Metadata(BaseModel):
    """Metadata validation schema"""
    source_url: str = Field(...)
    extracted_at: str = Field(...)
    extraction_method: str = Field(default="headless_browser")
    extraction_version: str = Field(default="1.0.0")
    last_updated: str = Field(...)


class SchemeData(BaseModel):
    """Complete scheme data validation schema"""
    scheme_info: SchemeInfo
    financial_details: FinancialDetails
    risk_and_returns: RiskAndReturns
    fund_management: FundManagement
    portfolio: Portfolio = Field(default_factory=Portfolio)
    metadata: Metadata
    
    @validator('risk_level', pre=True)
    def validate_risk_level(cls, v):
        """Validate risk level is in allowed values"""
        allowed_levels = [
            "Low", "Low to Moderate", "Moderate",
            "Moderately High", "High", "Very High"
        ]
        if v not in allowed_levels:
            logger.warning(f"Risk level '{v}' not in allowed values")
        return v
    
    @validator('category', pre=True)
    def validate_category(cls, v):
        """Validate category is in allowed values"""
        allowed_categories = [
            "Equity", "Debt", "Hybrid", "Commodity",
            "Index", "Fund of Funds"
        ]
        if v not in allowed_categories:
            logger.warning(f"Category '{v}' not in allowed values")
        return v


class DataValidator:
    """Validates extracted data against schema"""
    
    def __init__(self):
        """Initialize the data validator"""
        self.required_fields = {
            "scheme_info": ["scheme_name", "category", "sub_category"],
            "financial_details": [],
            "risk_and_returns": ["risk_level", "benchmark"],
            "fund_management": ["fund_manager"],
            "portfolio": [],
            "metadata": ["source_url"]
        }
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, Optional[str], Optional[SchemeData]]:
        """
        Validate extracted data against schema
        
        Args:
            data: Extracted data dictionary
        
        Returns:
            Tuple of (is_valid, error_message, validated_data)
        """
        try:
            # Check required fields
            missing_fields = self._check_required_fields(data)
            if missing_fields:
                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                logger.error(error_msg)
                return False, error_msg, None
            
            # Validate against Pydantic schema
            validated_data = SchemeData(**data)
            
            logger.info("Data validation successful")
            return True, None, validated_data
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def _check_required_fields(self, data: Dict[str, Any]) -> list[str]:
        """
        Check if all required fields are present
        
        Args:
            data: Data dictionary to check
        
        Returns:
            List of missing required field names
        """
        missing_fields = []
        
        for section, fields in self.required_fields.items():
            if section not in data:
                missing_fields.extend([f"{section}.{field}" for field in fields])
                continue
            
            for field in fields:
                if field not in data[section] or data[section][field] is None:
                    missing_fields.append(f"{section}.{field}")
        
        return missing_fields
    
    def validate_date_format(self, date_str: str) -> bool:
        """
        Validate date string is in ISO 8601 format (YYYY-MM-DD)
        
        Args:
            date_str: Date string to validate
        
        Returns:
            True if valid, False otherwise
        """
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_url(self, url: str) -> bool:
        """
        Validate URL format
        
        Args:
            url: URL string to validate
        
        Returns:
            True if valid, False otherwise
        """
        from urllib.parse import urlparse
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
