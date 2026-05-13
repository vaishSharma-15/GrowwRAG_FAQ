"""
Refusal Detector Module - Detects advisory queries and determines when to refuse
Implements graceful refusal for non-factual and out-of-scope queries
"""

import logging
import re
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RefusalCheck:
    """Result of a refusal check"""
    should_refuse: bool
    reason: str
    refusal_message: str
    category: str


class RefusalDetector:
    """Detects queries that should be refused"""
    
    # Advisory keywords - indicates investment advice request
    ADVISORY_KEYWORDS = [
        "should i",
        "should we",
        "better to",
        "recommend",
        "advice",
        "advise",
        "suggest",
        "good idea",
        "bad idea",
        "worth investing",
        "worth buying",
        "worth it",
        "profitable",
        "will it go up",
        "will it increase",
        "will it decrease",
        "future performance",
        "future returns",
        "predict",
        "prediction",
        "forecast",
        "best fund",
        "worst fund",
        "top performing",
        "outperform",
        "beat the market",
        "double my money",
        "get rich",
        "make money",
        "buy now",
        "sell now",
        "hold or sell",
        "exit strategy",
        "entry point",
        "timing",
        "right time",
        "good time"
    ]
    
    # Personal information keywords
    PII_KEYWORDS = [
        "my portfolio",
        "my investment",
        "my account",
        "my money",
        "my salary",
        "my income",
        "my age",
        "i am",
        "i'm",
        "my name",
        "my email",
        "my phone",
        "my address",
        "my pan",
        "my aadhar",
        "ssn",
        "social security"
    ]
    
    # Out of scope topics
    OUT_OF_SCOPE_TOPICS = [
        "stocks",
        "shares",
        "equity trading",
        "intraday",
        "options",
        "futures",
        "derivatives",
        "crypto",
        "bitcoin",
        "ethereum",
        "nft",
        "forex",
        "currency trading",
        "commodities trading",
        "gold trading",
        "silver trading",
        "real estate",
        "property",
        "insurance",
        "life insurance",
        "health insurance",
        "car insurance",
        "fixed deposit",
        "fd",
        "recurring deposit",
        "rd",
        "ppf",
        "nps",
        "epf",
        "sukanya samriddhi",
        "post office",
        "bank account",
        "loan",
        "home loan",
        "personal loan",
        "car loan",
        "credit card",
        "debt consolidation"
    ]
    
    # Known schemes in our corpus
    KNOWN_SCHEMES = [
        "axis silver",
        "axis small cap",
        "axis flexi cap",
        "axis gold fund",
        "axis nifty india defence",
        "silver fof",
        "small cap",
        "flexi cap",
        "gold fund",
        "defence index"
    ]
    
    def __init__(self, min_similarity_threshold: float = 0.6):
        """
        Initialize refusal detector
        
        Args:
            min_similarity_threshold: Minimum similarity for considering answer valid
        """
        self.min_similarity_threshold = min_similarity_threshold
        self.advisory_pattern = re.compile(
            r'\b(' + '|'.join(map(re.escape, self.ADVISORY_KEYWORDS)) + r')\b',
            re.IGNORECASE
        )
        self.pii_pattern = re.compile(
            r'\b(' + '|'.join(map(re.escape, self.PII_KEYWORDS)) + r')\b',
            re.IGNORECASE
        )
    
    def check_query(self, query: str, has_context: bool = True) -> RefusalCheck:
        """
        Check if a query should be refused
        
        Args:
            query: User query
            has_context: Whether relevant context was found
        
        Returns:
            RefusalCheck result
        """
        query_lower = query.lower().strip()
        
        # Check 1: Advisory keywords
        advisory_match = self._check_advisory(query_lower)
        if advisory_match:
            return RefusalCheck(
                should_refuse=True,
                reason="advisory_request",
                refusal_message=self._get_advisory_refusal(),
                category="advisory"
            )
        
        # Check 2: Personal information
        pii_match = self._check_pii(query_lower)
        if pii_match:
            return RefusalCheck(
                should_refuse=True,
                reason="pii_request",
                refusal_message=self._get_pii_refusal(),
                category="pii"
            )
        
        # Check 3: Out of scope topics
        out_of_scope = self._check_out_of_scope(query_lower)
        if out_of_scope:
            return RefusalCheck(
                should_refuse=True,
                reason="out_of_scope",
                refusal_message=self._get_out_of_scope_refusal(),
                category="out_of_scope"
            )
        
        # Check 4: Unknown schemes (but factual query)
        unknown_scheme = self._check_unknown_scheme(query_lower)
        # Skip unknown scheme check for generic factual queries
        # if unknown_scheme and not self._is_generic_factual_query(query_lower):
        #     return RefusalCheck(
        #         should_refuse=True,
        #         reason="unknown_scheme",
        #         refusal_message=self._get_unknown_scheme_refusal(query),
        #         category="unknown_scheme"
        #     )
        
        # Check 5: No relevant context found
        if not has_context:
            return RefusalCheck(
                should_refuse=True,
                reason="no_relevant_context",
                refusal_message=self._get_no_context_refusal(query),
                category="no_context"
            )
        
        # Query is acceptable
        return RefusalCheck(
            should_refuse=False,
            reason="",
            refusal_message="",
            category="acceptable"
        )
    
    def _check_advisory(self, query: str) -> bool:
        """Check if query contains advisory keywords"""
        return bool(self.advisory_pattern.search(query))
    
    def _check_pii(self, query: str) -> bool:
        """Check if query contains personal information indicators"""
        return bool(self.pii_pattern.search(query))
    
    def _check_out_of_scope(self, query: str) -> bool:
        """Check if query is about out-of-scope topics"""
        for topic in self.OUT_OF_SCOPE_TOPICS:
            if topic in query:
                return True
        return False
    
    def _check_unknown_scheme(self, query: str) -> bool:
        """Check if query is about a scheme not in our corpus"""
        # Check if any known scheme is mentioned
        for scheme in self.KNOWN_SCHEMES:
            if scheme in query:
                return False  # Known scheme found
        
        # Check for mutual fund mentions (e.g., "HDFC", "ICICI", "SBI")
        other_amcs = ["hdfc", "icici", "sbi", "nippon", "kotak", "aditya", "birla", "uti", "dsp", "franklin", "tata", "lic", "canara", "idfc", "bandhan", "mahindra", "quant", "motilal", "nippon india"]
        for amc in other_amcs:
            if amc in query:
                return True  # Different AMC mentioned
        
        return False  # Assume known scheme or generic query
    
    def _is_generic_factual_query(self, query: str) -> bool:
        """Check if query is a generic factual question"""
        generic_patterns = [
            "what is",
            "how to",
            "explain",
            "define",
            "difference between",
            "types of",
            "meaning of"
        ]
        for pattern in generic_patterns:
            if pattern in query:
                return True
        return False
    
    def _get_advisory_refusal(self) -> str:
        """Get refusal message for advisory queries"""
        return (
            "I can provide factual information about Axis mutual funds, including: • Scheme details (NAV, expense ratio, exit load) • Risk levels • Fund manager details. For general mutual fund education, please visit the official website of Groww\n\n"
            "https://groww.in\n\n"
            "For personalized investment advice or recommendations, please consult a SEBI-registered investment advisor."
        )
    
    def _get_pii_refusal(self) -> str:
        """Get refusal message for PII queries"""
        return (
            "I can provide factual information about Axis mutual funds, including: • Scheme details (NAV, expense ratio, exit load) • Risk levels • Fund manager details. For general mutual fund education, please visit the official website of Groww\n\n"
            "https://groww.in\n\n"
            "For personalized investment advice or recommendations, please consult a SEBI-registered investment advisor."
        )
    
    def _get_out_of_scope_refusal(self) -> str:
        """Get refusal message for out-of-scope topics"""
        return (
            "I can provide factual information about Axis mutual funds, including: • Scheme details (NAV, expense ratio, exit load) • Risk levels • Fund manager details. For general mutual fund education, please visit the official website of Groww\n\n"
            "https://groww.in\n\n"
            "For personalized investment advice or recommendations, please consult a SEBI-registered investment advisor."
        )
    
    def _get_unknown_scheme_refusal(self, query: str) -> str:
        """Get refusal message for unknown schemes"""
        return (
            "I can provide factual information about Axis mutual funds, including: • Scheme details (NAV, expense ratio, exit load) • Risk levels • Fund manager details. For general mutual fund education, please visit the official website of Groww\n\n"
            "https://groww.in\n\n"
            "For personalized investment advice or recommendations, please consult a SEBI-registered investment advisor."
        )
    
    def _get_no_context_refusal(self, query: str) -> str:
        """Get refusal message when no relevant context found"""
        return (
            "I can provide factual information about Axis mutual funds, including: • Scheme details (NAV, expense ratio, exit load) • Risk levels • Fund manager details. For general mutual fund education, please visit the official website of Groww\n\n"
            "https://groww.in\n\n"
            "For personalized investment advice or recommendations, please consult a SEBI-registered investment advisor."
        )
    
    def classify_query(self, query: str) -> Dict[str, Any]:
        """
        Classify query type without refusing
        
        Args:
            query: User query
        
        Returns:
            Classification results
        """
        query_lower = query.lower()
        
        classification = {
            "is_advisory": self._check_advisory(query_lower),
            "contains_pii": self._check_pii(query_lower),
            "is_out_of_scope": self._check_out_of_scope(query_lower),
            "is_unknown_scheme": self._check_unknown_scheme(query_lower),
            "query_type": "unknown"
        }
        
        # Determine query type
        if classification["is_advisory"]:
            classification["query_type"] = "advisory"
        elif classification["is_out_of_scope"]:
            classification["query_type"] = "out_of_scope"
        elif classification["contains_pii"]:
            classification["query_type"] = "pii"
        elif classification["is_unknown_scheme"]:
            classification["query_type"] = "unknown_scheme"
        else:
            classification["query_type"] = "factual"
        
        return classification
