"""
Quality Control Module - Implements data quality checks and monitoring
Checks for broken links, outdated information, and data consistency
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
import requests

logger = logging.getLogger(__name__)


class QualityControl:
    """Performs quality control checks on extracted data"""
    
    def __init__(self, timeout: int = 10):
        """
        Initialize quality control checker
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
    
    def check_broken_links(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check for broken links in documents
        
        Args:
            documents: List of document dictionaries
        
        Returns:
            Broken links report
        """
        report = {
            "total_urls": 0,
            "broken_urls": [],
            "valid_urls": [],
            "unreachable_urls": []
        }
        
        for doc in documents:
            metadata = doc.get("metadata", {})
            source_url = metadata.get("source_url")
            
            if source_url:
                report["total_urls"] += 1
                
                try:
                    response = requests.head(
                        source_url,
                        timeout=self.timeout,
                        allow_redirects=True
                    )
                    
                    if response.status_code == 200:
                        report["valid_urls"].append({
                            "url": source_url,
                            "scheme": doc.get("scheme_info", {}).get("scheme_name", "Unknown")
                        })
                    elif response.status_code == 404:
                        report["broken_urls"].append({
                            "url": source_url,
                            "scheme": doc.get("scheme_info", {}).get("scheme_name", "Unknown"),
                            "status_code": response.status_code
                        })
                    else:
                        report["unreachable_urls"].append({
                            "url": source_url,
                            "scheme": doc.get("scheme_info", {}).get("scheme_name", "Unknown"),
                            "status_code": response.status_code
                        })
                
                except requests.RequestException as e:
                    report["unreachable_urls"].append({
                        "url": source_url,
                        "scheme": doc.get("scheme_info", {}).get("scheme_name", "Unknown"),
                        "error": str(e)
                    })
        
        return report
    
    def check_data_consistency(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check data consistency across documents
        
        Args:
            documents: List of document dictionaries
        
        Returns:
            Consistency report
        """
        report = {
            "inconsistencies": [],
            "warnings": [],
            "statistics": {}
        }
        
        # Check AMC consistency
        amcs = set()
        for doc in documents:
            scheme_info = doc.get("scheme_info", {})
            amc = scheme_info.get("amc")
            if amc:
                amcs.add(amc)
        
        if len(amcs) > 1:
            report["inconsistencies"].append(
                f"Multiple AMCs found: {amcs}"
            )
        
        # Check plan type consistency
        plan_types = set()
        for doc in documents:
            scheme_info = doc.get("scheme_info", {})
            plan_type = scheme_info.get("plan_type")
            if plan_type:
                plan_types.add(plan_type)
        
        if len(plan_types) > 1:
            report["inconsistencies"].append(
                f"Multiple plan types found: {plan_types}"
            )
        
        # Check for duplicate scheme codes
        scheme_codes = []
        for doc in documents:
            scheme_info = doc.get("scheme_info", {})
            scheme_code = scheme_info.get("scheme_code")
            if scheme_code:
                scheme_codes.append(scheme_code)
        
        duplicates = [code for code in set(scheme_codes) if scheme_codes.count(code) > 1]
        if duplicates:
            report["inconsistencies"].append(
                f"Duplicate scheme codes found: {duplicates}"
            )
        
        # Check for duplicate scheme names
        scheme_names = []
        for doc in documents:
            scheme_info = doc.get("scheme_info", {})
            scheme_name = scheme_info.get("scheme_name")
            if scheme_name:
                scheme_names.append(scheme_name)
        
        duplicates = [name for name in set(scheme_names) if scheme_names.count(name) > 1]
        if duplicates:
            report["inconsistencies"].append(
                f"Duplicate scheme names found: {duplicates}"
            )
        
        # Statistics
        report["statistics"] = {
            "total_documents": len(documents),
            "unique_amcs": len(amcs),
            "unique_plan_types": len(plan_types),
            "unique_scheme_codes": len(set(scheme_codes))
        }
        
        return report
    
    def check_outdated_information(
        self,
        documents: List[Dict[str, Any]],
        max_nav_age_days: int = 7
    ) -> Dict[str, Any]:
        """
        Check for outdated information in documents
        
        Args:
            documents: List of document dictionaries
            max_nav_age_days: Maximum acceptable NAV age in days
        
        Returns:
            Outdated information report
        """
        report = {
            "outdated_schemes": [],
            "fresh_schemes": [],
            "missing_nav_dates": []
        }
        
        for doc in documents:
            financial = doc.get("financial_details", {})
            nav_date = financial.get("nav_date")
            scheme_info = doc.get("scheme_info", {})
            scheme_name = scheme_info.get("scheme_name", "Unknown")
            
            if not nav_date:
                report["missing_nav_dates"].append(scheme_name)
                continue
            
            try:
                nav_datetime = datetime.strptime(nav_date, "%Y-%m-%d")
                days_old = (datetime.utcnow() - nav_datetime).days
                
                if days_old > max_nav_age_days:
                    report["outdated_schemes"].append({
                        "scheme": scheme_name,
                        "nav_date": nav_date,
                        "days_old": days_old
                    })
                else:
                    report["fresh_schemes"].append(scheme_name)
            
            except ValueError:
                report["missing_nav_dates"].append(scheme_name)
        
        return report
    
    def check_data_completeness(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check data completeness across documents
        
        Args:
            documents: List of document dictionaries
        
        Returns:
            Completeness report
        """
        report = {
            "total_fields": 0,
            "filled_fields": 0,
            "missing_fields": [],
            "completeness_percentage": 0.0,
            "scheme_completeness": {}
        }
        
        required_fields = {
            "scheme_info": ["scheme_name", "scheme_code", "category", "sub_category"],
            "financial_details": ["expense_ratio", "nav", "minimum_investment", "sip_amount"],
            "risk_and_returns": ["risk_level", "benchmark"],
            "fund_management": ["fund_manager"],
            "metadata": ["source_url"]
        }
        
        for doc in documents:
            scheme_name = doc.get("scheme_info", {}).get("scheme_name", "Unknown")
            scheme_report = {
                "total": 0,
                "filled": 0,
                "missing": []
            }
            
            for section, fields in required_fields.items():
                section_data = doc.get(section, {})
                for field in fields:
                    scheme_report["total"] += 1
                    report["total_fields"] += 1
                    
                    if field in section_data and section_data[field] is not None:
                        scheme_report["filled"] += 1
                        report["filled_fields"] += 1
                    else:
                        scheme_report["missing"].append(f"{section}.{field}")
                        report["missing_fields"].append({
                            "scheme": scheme_name,
                            "field": f"{section}.{field}"
                        })
            
            completeness = (scheme_report["filled"] / scheme_report["total"] * 100) if scheme_report["total"] > 0 else 0
            scheme_report["completeness_percentage"] = round(completeness, 2)
            report["scheme_completeness"][scheme_name] = scheme_report
        
        report["completeness_percentage"] = (
            report["filled_fields"] / report["total_fields"] * 100
        ) if report["total_fields"] > 0 else 0
        report["completeness_percentage"] = round(report["completeness_percentage"], 2)
        
        return report
    
    def check_numerical_anomalies(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check for numerical anomalies in financial data
        
        Args:
            documents: List of document dictionaries
        
        Returns:
            Anomalies report
        """
        report = {
            "anomalies": [],
            "warnings": []
        }
        
        expense_ratios = []
        navs = []
        aums = []
        
        for doc in documents:
            financial = doc.get("financial_details", {})
            risk_returns = doc.get("risk_and_returns", {})
            scheme_name = doc.get("scheme_info", {}).get("scheme_name", "Unknown")
            
            # Collect expense ratios
            if financial.get("expense_ratio") is not None:
                expense_ratios.append({
                    "scheme": scheme_name,
                    "value": financial["expense_ratio"]
                })
            
            # Collect NAVs
            if financial.get("nav") is not None:
                navs.append({
                    "scheme": scheme_name,
                    "value": financial["nav"]
                })
            
            # Collect AUMs
            if risk_returns.get("aum") is not None:
                aums.append({
                    "scheme": scheme_name,
                    "value": risk_returns["aum"]
                })
        
        # Check expense ratio anomalies
        if expense_ratios:
            avg_expense_ratio = sum(item["value"] for item in expense_ratios) / len(expense_ratios)
            for item in expense_ratios:
                if abs(item["value"] - avg_expense_ratio) > 2.0:  # More than 2% deviation
                    report["anomalies"].append({
                        "scheme": item["scheme"],
                        "field": "expense_ratio",
                        "value": item["value"],
                        "average": avg_expense_ratio,
                        "deviation": abs(item["value"] - avg_expense_ratio)
                    })
        
        # Check NAV anomalies
        if navs:
            avg_nav = sum(item["value"] for item in navs) / len(navs)
            for item in navs:
                if item["value"] < avg_nav * 0.1 or item["value"] > avg_nav * 10:  # More than 10x deviation
                    report["anomalies"].append({
                        "scheme": item["scheme"],
                        "field": "nav",
                        "value": item["value"],
                        "average": avg_nav,
                        "deviation_ratio": item["value"] / avg_nav if avg_nav > 0 else 0
                    })
        
        return report
    
    def generate_quality_report(
        self,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive quality report
        
        Args:
            documents: List of document dictionaries
        
        Returns:
            Comprehensive quality report
        """
        logger.info("Generating quality report")
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_documents": len(documents),
            "summary": {},
            "link_check": {},
            "consistency_check": {},
            "freshness_check": {},
            "completeness_check": {},
            "anomaly_check": {}
        }
        
        # Run all checks
        report["link_check"] = self.check_broken_links(documents)
        report["consistency_check"] = self.check_data_consistency(documents)
        report["freshness_check"] = self.check_outdated_information(documents)
        report["completeness_check"] = self.check_data_completeness(documents)
        report["anomaly_check"] = self.check_numerical_anomalies(documents)
        
        # Generate summary
        report["summary"] = {
            "has_broken_links": len(report["link_check"]["broken_urls"]) > 0,
            "has_inconsistencies": len(report["consistency_check"]["inconsistencies"]) > 0,
            "has_outdated_data": len(report["freshness_check"]["outdated_schemes"]) > 0,
            "has_missing_data": len(report["completeness_check"]["missing_fields"]) > 0,
            "has_anomalies": len(report["anomaly_check"]["anomalies"]) > 0,
            "overall_quality_score": self._calculate_quality_score(report)
        }
        
        logger.info("Quality report generated successfully")
        return report
    
    def _calculate_quality_score(self, report: Dict[str, Any]) -> float:
        """
        Calculate overall quality score (0-100)
        
        Args:
            report: Quality report
        
        Returns:
            Quality score
        """
        score = 100.0
        
        # Deduct for broken links
        broken_links = len(report["link_check"]["broken_urls"])
        score -= broken_links * 10
        
        # Deduct for inconsistencies
        inconsistencies = len(report["consistency_check"]["inconsistencies"])
        score -= inconsistencies * 5
        
        # Deduct for outdated data
        outdated = len(report["freshness_check"]["outdated_schemes"])
        score -= outdated * 5
        
        # Deduct for missing data
        completeness = report["completeness_check"]["completeness_percentage"]
        score -= (100 - completeness) * 0.3
        
        # Deduct for anomalies
        anomalies = len(report["anomaly_check"]["anomalies"])
        score -= anomalies * 2
        
        return max(0.0, min(100.0, score))
