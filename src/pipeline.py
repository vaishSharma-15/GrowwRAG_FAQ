"""
Main Extraction Pipeline Script
Orchestrates the data extraction process for Phase 1
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from scraper import WebScraper
from parser import HTMLParser
from normalizer import DataNormalizer
from validator import DataValidator, SchemeData
from retry import RetryHandler
from robots_checker import RobotsTxtChecker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ExtractionPipeline:
    """Main pipeline for extracting mutual fund scheme data"""
    
    # URLs to extract data from
    URLS = [
        "https://groww.in/mutual-funds/axis-silver-fof-direct-growth",
        "https://groww.in/mutual-funds/axis-small-cap-fund-direct-growth",
        "https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth",
        "https://groww.in/mutual-funds/axis-gold-fund-direct-growth",
        "https://groww.in/mutual-funds/axis-nifty-india-defence-index-fund-direct-growth"
    ]
    
    def __init__(self, output_dir: str = "data/extracted"):
        """
        Initialize the extraction pipeline
        
        Args:
            output_dir: Directory to save extracted data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.scraper = WebScraper(headless=True, timeout=30000)
        self.parser = HTMLParser()
        self.normalizer = DataNormalizer()
        self.validator = DataValidator()
        self.retry_handler = RetryHandler(max_attempts=3)
        self.robots_checker = RobotsTxtChecker(user_agent="MutualFundFAQBot/1.0")
    
    async def run(self):
        """Run the extraction pipeline"""
        logger.info("Starting extraction pipeline")
        logger.info(f"URLs to process: {len(self.URLS)}")
        
        try:
            # Start browser
            await self.scraper.start()
            
            # Process each URL
            results = []
            for url in self.URLS:
                try:
                    logger.info(f"Processing URL: {url}")
                    result = await self.process_url(url)
                    if result:
                        results.append(result)
                        # Save result
                        await self.save_result(result)
                except Exception as e:
                    logger.error(f"Failed to process URL {url}: {e}")
            
            # Generate summary
            await self.generate_summary(results)
            
            logger.info(f"Extraction pipeline completed. Successfully extracted: {len(results)}/{len(self.URLS)}")
            
        finally:
            # Stop browser
            await self.scraper.stop()
    
    async def process_url(self, url: str) -> Dict[str, Any]:
        """
        Process a single URL through the extraction pipeline
        
        Args:
            url: URL to process
        
        Returns:
            Extracted and validated data dictionary
        """
        # Check robots.txt compliance
        if not self.robots_checker.can_fetch(url):
            logger.warning(f"URL disallowed by robots.txt: {url}")
            return None
        
        # Extract HTML with retry logic
        async def extract_html():
            return await self.scraper.extract_html(url, wait_for_selector=".scheme-details")
        
        html = await self.retry_handler.execute_with_retry(
            extract_html,
            exceptions=(Exception,)
        )
        
        if not html:
            logger.error(f"Failed to extract HTML from {url}")
            return None
        
        # Parse HTML
        try:
            parsed_data = self.parser.parse(html, url)
        except Exception as e:
            logger.error(f"Failed to parse HTML from {url}: {e}")
            return None
        
        # Normalize data
        try:
            normalized_data = self.normalizer.normalize(parsed_data)
        except Exception as e:
            logger.error(f"Failed to normalize data from {url}: {e}")
            return None
        
        # Validate data
        is_valid, error_msg, validated_data = self.validator.validate(normalized_data)
        
        if not is_valid:
            logger.error(f"Validation failed for {url}: {error_msg}")
            return None
        
        # Convert to dict for JSON serialization
        result = validated_data.dict()
        
        return result
    
    async def save_result(self, data: Dict[str, Any]):
        """
        Save extracted data to JSON file
        
        Args:
            data: Extracted data dictionary
        """
        try:
            # Generate filename from scheme name
            scheme_name = data.get("scheme_info", {}).get("scheme_name", "unknown")
            scheme_slug = scheme_name.lower().replace(" ", "_").replace("-", "_")
            filename = f"{scheme_slug}.json"
            filepath = self.output_dir / filename
            
            # Save to JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved data to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
    
    async def generate_summary(self, results: List[Dict[str, Any]]):
        """
        Generate extraction summary report
        
        Args:
            results: List of extracted data dictionaries
        """
        summary = {
            "extraction_date": datetime.utcnow().isoformat(),
            "total_urls": len(self.URLS),
            "successful_extractions": len(results),
            "failed_extractions": len(self.URLS) - len(results),
            "schemes_extracted": [
                result.get("scheme_info", {}).get("scheme_name") for result in results
            ]
        }
        
        summary_path = self.output_dir / "extraction_summary.json"
        
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved extraction summary to {summary_path}")
            
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")


async def main():
    """Main entry point"""
    pipeline = ExtractionPipeline()
    await pipeline.run()


if __name__ == "__main__":
    asyncio.run(main())
