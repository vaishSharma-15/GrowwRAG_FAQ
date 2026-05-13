"""
Robots.txt Compliance Checker Module
Checks if URLs are allowed to be scraped according to robots.txt
"""

import logging
import urllib.robotparser
from urllib.parse import urlparse
from typing import Optional

logger = logging.getLogger(__name__)


class RobotsTxtChecker:
    """Checks robots.txt compliance for scraping operations"""
    
    def __init__(self, user_agent: str = "MutualFundFAQBot"):
        """
        Initialize robots.txt checker
        
        Args:
            user_agent: User agent string to use for checking
        """
        self.user_agent = user_agent
        self.robot_parsers: dict[str, urllib.robotparser.RobotFileParser] = {}
    
    def can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt
        
        Args:
            url: URL to check
        
        Returns:
            True if allowed, False otherwise
        """
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Get or create robot parser for this domain
            if base_url not in self.robot_parsers:
                self.robot_parsers[base_url] = self._create_robot_parser(base_url)
            
            robot_parser = self.robot_parsers[base_url]
            
            # Check if URL can be fetched
            can_fetch = robot_parser.can_fetch(self.user_agent, url)
            
            if can_fetch:
                logger.info(f"URL allowed by robots.txt: {url}")
            else:
                logger.warning(f"URL disallowed by robots.txt: {url}")
            
            return can_fetch
            
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {e}")
            # If robots.txt check fails, allow the fetch (fail-safe)
            return True
    
    def _create_robot_parser(self, base_url: str) -> urllib.robotparser.RobotFileParser:
        """
        Create and configure robot parser for a domain
        
        Args:
            base_url: Base URL of the domain
        
        Returns:
            Configured RobotFileParser instance
        """
        robots_url = f"{base_url}/robots.txt"
        robot_parser = urllib.robotparser.RobotFileParser()
        robot_parser.set_url(robots_url)
        
        try:
            robot_parser.read()
            logger.info(f"Successfully read robots.txt from {robots_url}")
        except Exception as e:
            logger.warning(f"Failed to read robots.txt from {robots_url}: {e}")
            # If robots.txt is not accessible, assume all URLs are allowed
            logger.info("Assuming all URLs are allowed (robots.txt not accessible)")
        
        return robot_parser
    
    def refresh(self, url: str):
        """
        Refresh robots.txt for a domain
        
        Args:
            url: URL from the domain to refresh
        """
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            if base_url in self.robot_parsers:
                del self.robot_parsers[base_url]
                logger.info(f"Refreshed robots.txt for {base_url}")
            
        except Exception as e:
            logger.error(f"Error refreshing robots.txt: {e}")
    
    def get_crawl_delay(self, url: str) -> Optional[float]:
        """
        Get crawl delay specified in robots.txt
        
        Args:
            url: URL to check
        
        Returns:
            Crawl delay in seconds, or None if not specified
        """
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            if base_url not in self.robot_parsers:
                self.robot_parsers[base_url] = self._create_robot_parser(base_url)
            
            robot_parser = self.robot_parsers[base_url]
            crawl_delay = robot_parser.crawl_delay(self.user_agent)
            
            if crawl_delay:
                logger.info(f"Crawl delay for {base_url}: {crawl_delay} seconds")
            
            return crawl_delay
            
        except Exception as e:
            logger.error(f"Error getting crawl delay: {e}")
            return None
