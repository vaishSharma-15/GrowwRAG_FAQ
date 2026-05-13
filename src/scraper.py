"""
Web Scraper Module - Uses Playwright for headless browser scraping
Handles JavaScript rendering and dynamic content loading
"""

import asyncio
import logging
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page

logger = logging.getLogger(__name__)


class WebScraper:
    """Headless browser scraper for extracting HTML content from URLs"""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Initialize the web scraper
        
        Args:
            headless: Run browser in headless mode
            timeout: Page load timeout in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    async def start(self):
        """Start the browser instance"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless
            )
            logger.info("Browser started successfully")
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    async def stop(self):
        """Stop the browser instance"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser stopped successfully")
        except Exception as e:
            logger.error(f"Failed to stop browser: {e}")
    
    async def extract_html(self, url: str, wait_for_selector: str = None) -> str:
        """
        Extract HTML content from a URL
        
        Args:
            url: URL to scrape
            wait_for_selector: CSS selector to wait for before extraction
        
        Returns:
            HTML content as string
        
        Raises:
            Exception: If extraction fails
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Call start() first.")
        
        try:
            page = await self.browser.new_page()
            
            # Set user agent
            await page.set_extra_http_headers({
                "User-Agent": "MutualFundFAQBot/1.0 (educational-research; contact: none)"
            })
            
            # Navigate to URL
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until="networkidle", timeout=self.timeout)
            
            # Wait for specific selector if provided
            if wait_for_selector:
                logger.info(f"Waiting for selector: {wait_for_selector}")
                await page.wait_for_selector(wait_for_selector, timeout=self.timeout)
            
            # Extract HTML content
            html_content = await page.content()
            
            # Close page
            await page.close()
            
            logger.info(f"Successfully extracted HTML from {url}")
            return html_content
            
        except Exception as e:
            logger.error(f"Failed to extract HTML from {url}: {e}")
            raise
    
    async def extract_multiple(self, urls: list[str], wait_for_selector: str = None) -> dict[str, str]:
        """
        Extract HTML content from multiple URLs
        
        Args:
            urls: List of URLs to scrape
            wait_for_selector: CSS selector to wait for before extraction
        
        Returns:
            Dictionary mapping URLs to HTML content
        """
        results = {}
        
        for url in urls:
            try:
                html = await self.extract_html(url, wait_for_selector)
                results[url] = html
                # Add delay between requests to respect rate limiting
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"Failed to extract {url}: {e}")
                results[url] = None
        
        return results
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()
