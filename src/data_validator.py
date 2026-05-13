"""
Data Validation Module - Validates extracted data accuracy and completeness
Implements numerical data validation, cross-referencing, and freshness tracking
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates extracted mutual fund scheme data"""
    
    def __init__(self):
        """Initialize the data validator"""
        self.validation_rules = self._get_validation_rules()
    
    def _get_validation_rules(self) -> Dict[str, Dict]:
        """
        Get validation rules for different data fields
        
        Returns:
            Dictionary of validation rules
        """
        return {
            "expense_ratio": {
                "min": 0.0,
                "max": 5.0,
                "type": float,
                "required": True
            },
            "nav": {
                "min": 0.0,
                "type": float,
                "required": True
            },
            "minimum_investment": {
                "min": 100,
                "type": int,
                "required": True
            },
            "sip_amount": {
                "min": 100,
                "type": int,
                "required": True
            },
            "aum": {
                "min": 0.0,
                "type": float,
                "required": False
            },
            "returns": {
                "min": -100,
                "max": 100,
                "type": float,
                "required": False
            }
        }
    
    def validate_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a complete document
        
        Args:
            document: Document dictionary to validate
        
        Returns:
            Validation report dictionary
        """
        validation_report = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "field_validations": {}
        }
        
        # Validate scheme information
        scheme_validation = self._validate_scheme_info(
            document.get("scheme_info", {})
        )
        validation_report["field_validations"]["scheme_info"] = scheme_validation
        validation_report["errors"].extend(scheme_validation["errors"])
        validation_report["warnings"].extend(scheme_validation["warnings"])
        
        # Validate financial details
        financial_validation = self._validate_financial_details(
            document.get("financial_details", {})
        )
        validation_report["field_validations"]["financial_details"] = financial_validation
        validation_report["errors"].extend(financial_validation["errors"])
        validation_report["warnings"].extend(financial_validation["warnings"])
        
        # Validate risk and returns
        risk_validation = self._validate_risk_and_returns(
            document.get("risk_and_returns", {})
        )
        validation_report["field_validations"]["risk_and_returns"] = risk_validation
        validation_report["errors"].extend(risk_validation["errors"])
        validation_report["warnings"].extend(risk_validation["warnings"])
        
        # Validate fund management
        fund_mgmt_validation = self._validate_fund_management(
            document.get("fund_management", {})
        )
        validation_report["field_validations"]["fund_management"] = fund_mgmt_validation
        validation_report["errors"].extend(fund_mgmt_validation["errors"])
        validation_report["warnings"].extend(fund_mgmt_validation["warnings"])
        
        # Validate metadata
        metadata_validation = self._validate_metadata(
            document.get("metadata", {})
        )
        validation_report["field_validations"]["metadata"] = metadata_validation
        validation_report["errors"].extend(metadata_validation["errors"])
        validation_report["warnings"].extend(metadata_validation["warnings"])
        
        # Set overall validity
        validation_report["is_valid"] = len(validation_report["errors"]) == 0
        
        return validation_report
    
    def _validate_scheme_info(self, scheme_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate scheme information"""
        validation = {"errors": [], "warnings": []}
        
        # Check required fields
        required_fields = ["scheme_name", "scheme_code", "category", "sub_category"]
        for field in required_fields:
            if field not in scheme_info or not scheme_info[field]:
                validation["errors"].append(f"Missing required field: scheme_info.{field}")
        
        # Validate scheme code format
        if "scheme_code" in scheme_info and scheme_info["scheme_code"]:
            scheme_code = scheme_info["scheme_code"]
            if not re.match(r'^[A-Z0-9]{6,7}$', scheme_code):
                validation["errors"].append(
                    f"Invalid scheme code format: {scheme_code}"
                )
        
        # Validate category
        if "category" in scheme_info and scheme_info["category"]:
            valid_categories = [
                "Equity", "Debt", "Hybrid", "Commodity", "Index", "Fund of Funds"
            ]
            if scheme_info["category"] not in valid_categories:
                validation["warnings"].append(
                    f"Unusual category: {scheme_info['category']}"
                )
        
        return validation
    
    def _validate_financial_details(self, financial: Dict[str, Any]) -> Dict[str, Any]:
        """Validate financial details"""
        validation = {"errors": [], "warnings": []}
        
        # Validate expense ratio
        if "expense_ratio" in financial:
            expense_ratio = financial["expense_ratio"]
            if expense_ratio is not None:
                if not isinstance(expense_ratio, (int, float)):
                    validation["errors"].append(
                        f"Expense ratio must be numeric: {expense_ratio}"
                    )
                elif expense_ratio < 0 or expense_ratio > 5:
                    validation["errors"].append(
                        f"Expense ratio out of range (0-5): {expense_ratio}"
                    )
            else:
                validation["errors"].append("Expense ratio is required")
        
        # Validate NAV
        if "nav" in financial:
            nav = financial["nav"]
            if nav is not None:
                if not isinstance(nav, (int, float)):
                    validation["errors"].append(f"NAV must be numeric: {nav}")
                elif nav <= 0:
                    validation["errors"].append(f"NAV must be positive: {nav}")
            else:
                validation["errors"].append("NAV is required")
        
        # Validate minimum investment
        if "minimum_investment" in financial:
            min_inv = financial["minimum_investment"]
            if min_inv is not None:
                if not isinstance(min_inv, (int, float)):
                    validation["errors"].append(
                        f"Minimum investment must be numeric: {min_inv}"
                    )
                elif min_inv < 100:
                    validation["warnings"].append(
                        f"Minimum investment unusually low: {min_inv}"
                    )
            else:
                validation["errors"].append("Minimum investment is required")
        
        # Validate SIP amount
        if "sip_amount" in financial:
            sip = financial["sip_amount"]
            if sip is not None:
                if not isinstance(sip, (int, float)):
                    validation["errors"].append(f"SIP amount must be numeric: {sip}")
                elif sip < 100:
                    validation["warnings"].append(f"SIP amount unusually low: {sip}")
            else:
                validation["errors"].append("SIP amount is required")
        
        # Validate NAV date
        if "nav_date" in financial and financial["nav_date"]:
            nav_date = financial["nav_date"]
            if not self._is_valid_date(nav_date):
                validation["errors"].append(f"Invalid NAV date format: {nav_date}")
            elif not self._is_recent_date(nav_date, days=7):
                validation["warnings"].append(f"NAV date may be outdated: {nav_date}")
        
        return validation
    
    def _validate_risk_and_returns(self, risk_returns: Dict[str, Any]) -> Dict[str, Any]:
        """Validate risk and returns information"""
        validation = {"errors": [], "warnings": []}
        
        # Validate risk level
        if "risk_level" in risk_returns and risk_returns["risk_level"]:
            valid_risk_levels = [
                "Low", "Low to Moderate", "Moderate",
                "Moderately High", "High", "Very High"
            ]
            if risk_returns["risk_level"] not in valid_risk_levels:
                validation["warnings"].append(
                    f"Unusual risk level: {risk_returns['risk_level']}"
                )
        else:
            validation["errors"].append("Risk level is required")
        
        # Validate benchmark
        if "benchmark" in risk_returns and risk_returns["benchmark"]:
            if len(risk_returns["benchmark"]) == 0:
                validation["errors"].append("Benchmark is required")
        else:
            validation["errors"].append("Benchmark is required")
        
        # Validate AUM
        if "aum" in risk_returns:
            aum = risk_returns["aum"]
            if aum is not None:
                if not isinstance(aum, (int, float)):
                    validation["errors"].append(f"AUM must be numeric: {aum}")
                elif aum <= 0:
                    validation["errors"].append(f"AUM must be positive: {aum}")
        
        # Validate returns
        if "returns" in risk_returns and isinstance(risk_returns["returns"], dict):
            for period, value in risk_returns["returns"].items():
                if value is not None:
                    if not isinstance(value, (int, float)):
                        validation["errors"].append(
                            f"Returns must be numeric: {period}={value}"
                        )
                    elif value < -100 or value > 100:
                        validation["errors"].append(
                            f"Returns out of range (-100 to 100): {period}={value}"
                        )
        
        return validation
    
    def _validate_fund_management(self, fund_mgmt: Dict[str, Any]) -> Dict[str, Any]:
        """Validate fund management information"""
        validation = {"errors": [], "warnings": []}
        
        # Validate fund manager
        if "fund_manager" in fund_mgmt and fund_mgmt["fund_manager"]:
            if len(fund_mgmt["fund_manager"]) == 0:
                validation["errors"].append("Fund manager name is required")
        else:
            validation["errors"].append("Fund manager is required")
        
        return validation
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata"""
        validation = {"errors": [], "warnings": []}
        
        # Validate source URL
        if "source_url" in metadata and metadata["source_url"]:
            url = metadata["source_url"]
            if not self._is_valid_url(url):
                validation["errors"].append(f"Invalid source URL: {url}")
        else:
            validation["errors"].append("Source URL is required")
        
        # Validate extracted_at timestamp
        if "extracted_at" in metadata and metadata["extracted_at"]:
            timestamp = metadata["extracted_at"]
            if not self._is_valid_iso_timestamp(timestamp):
                validation["errors"].append(
                    f"Invalid extracted_at format: {timestamp}"
                )
        
        return validation
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Check if date string is valid (YYYY-MM-DD format)"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def _is_recent_date(self, date_str: str, days: int = 7) -> bool:
        """Check if date is recent (within specified days)"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            days_diff = (datetime.utcnow() - date).days
            return days_diff <= days
        except ValueError:
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        from urllib.parse import urlparse
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _is_valid_iso_timestamp(self, timestamp: str) -> bool:
        """Check if timestamp is valid ISO 8601 format"""
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    def cross_reference_facts(
        self,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Cross-reference facts across multiple documents
        
        Args:
            documents: List of document dictionaries
        
        Returns:
            Cross-reference report
        """
        report = {
            "inconsistencies": [],
            "similarities": [],
            "summary": {}
        }
        
        if len(documents) < 2:
            return report
        
        # Extract AMC from all documents
        amcs = set()
        for doc in documents:
            scheme_info = doc.get("scheme_info", {})
            amc = scheme_info.get("amc")
            if amc:
                amcs.add(amc)
        
        # Check if all documents have the same AMC
        if len(amcs) > 1:
            report["inconsistencies"].append(
                f"Multiple AMCs found: {amcs}"
            )
        
        report["summary"]["total_documents"] = len(documents)
        report["summary"]["unique_amcs"] = len(amcs)
        report["summary"]["unique_categories"] = len(
            set(doc.get("scheme_info", {}).get("category") for doc in documents)
        )
        
        return report
    
    def check_data_freshness(
        self,
        documents: List[Dict[str, Any]],
        max_days_old: int = 7
    ) -> Dict[str, Any]:
        """
        Check data freshness across documents
        
        Args:
            documents: List of document dictionaries
            max_days_old: Maximum acceptable age in days
        
        Returns:
            Freshness report
        """
        report = {
            "fresh_documents": [],
            "stale_documents": [],
            "missing_dates": []
        }
        
        for doc in documents:
            financial = doc.get("financial_details", {})
            nav_date = financial.get("nav_date")
            scheme_name = doc.get("scheme_info", {}).get("scheme_name", "Unknown")
            
            if not nav_date:
                report["missing_dates"].append(scheme_name)
            elif self._is_recent_date(nav_date, days=max_days_old):
                report["fresh_documents"].append(scheme_name)
            else:
                report["stale_documents"].append({
                    "scheme": scheme_name,
                    "nav_date": nav_date,
                    "days_old": (datetime.utcnow() - datetime.strptime(nav_date, "%Y-%m-%d")).days
                })
        
        return report
