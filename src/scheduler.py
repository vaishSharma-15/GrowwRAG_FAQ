"""
Scheduler to automatically update financial metrics from source URLs
Runs periodically to keep chunk data up to date
"""

import logging
import schedule
import time
from datetime import datetime
from typing import Dict, Any
import json
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FinancialMetricsUpdater:
    """Updates financial metrics from source URLs"""
    
    def __init__(self):
        self.scheme_urls = {
            "axis_flexi_cap_fund_direct_growth": "https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth",
            "axis_small_cap_fund_direct_growth": "https://groww.in/mutual-funds/axis-small-cap-fund-direct-growth",
            "axis_silver_fof_direct_growth": "https://groww.in/mutual-funds/axis-silver-fof-direct-growth",
            "axis_gold_fund_direct_growth": "https://groww.in/mutual-funds/axis-gold-fund-direct-growth",
            "axis_nifty_india_defence_index_fund_direct_growth": "https://groww.in/mutual-funds/axis-nifty-india-defence-index-fund-direct-growth"
        }
        self.chunk_dir = "data/processed/chunks"
        
    def fetch_financial_metrics(self, url: str) -> Dict[str, Any]:
        """
        Fetch financial metrics from groww.in URL
        Note: This is a placeholder - actual implementation depends on website structure
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML to extract financial metrics
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # This is a placeholder - actual selectors depend on website structure
            # You'll need to inspect the actual HTML to find the correct selectors
            metrics = {
                "expense_ratio": None,
                "exit_load": None,
                "aum": None,
                "nav": None,
                "nav_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            logger.info(f"Fetched metrics from {url}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to fetch metrics from {url}: {e}")
            return None
    
    def update_chunk_file(self, scheme_name: str, metrics: Dict[str, Any]):
        """Update the chunk file with new financial metrics"""
        try:
            chunk_file = f"{self.chunk_dir}/{scheme_name}_chunks.json"
            
            with open(chunk_file, 'r') as f:
                chunks = json.load(f)
            
            # Update chunk_2 (financial details)
            for chunk in chunks:
                if chunk['chunk_id'].endswith('_chunk_2'):
                    old_text = chunk['chunk_text']
                    
                    # Update metrics if available
                    if metrics.get('expense_ratio'):
                        old_text = self._update_field(old_text, "Expense Ratio:", f"{metrics['expense_ratio']}%")
                    if metrics.get('exit_load'):
                        old_text = self._update_field(old_text, "Exit Load:", metrics['exit_load'])
                    if metrics.get('nav'):
                        old_text = self._update_field(old_text, "NAV:", f"₹{metrics['nav']}")
                    if metrics.get('nav_date'):
                        old_text = self._update_field(old_text, "NAV Date:", metrics['nav_date'])
                    
                    chunk['chunk_text'] = old_text
                    chunk['metadata']['last_updated'] = metrics.get('nav_date', datetime.now().strftime("%Y-%m-%d"))
            
            # Write back to file
            with open(chunk_file, 'w') as f:
                json.dump(chunks, f, indent=2)
            
            logger.info(f"Updated chunk file: {chunk_file}")
            
        except Exception as e:
            logger.error(f"Failed to update chunk file {scheme_name}: {e}")
    
    def _update_field(self, text: str, field: str, value: str) -> str:
        """Update a specific field in the chunk text"""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if line.startswith(field):
                lines[i] = f"{field} {value}"
                break
        return '\n'.join(lines)
    
    def update_all_chunks(self):
        """Update all scheme chunks with latest financial metrics"""
        logger.info("=" * 60)
        logger.info("Starting financial metrics update")
        logger.info("=" * 60)
        
        for scheme_name, url in self.scheme_urls.items():
            logger.info(f"Processing {scheme_name}...")
            
            metrics = self.fetch_financial_metrics(url)
            if metrics:
                self.update_chunk_file(scheme_name, metrics)
            else:
                logger.warning(f"Skipping {scheme_name} due to fetch failure")
        
        logger.info("=" * 60)
        logger.info("Financial metrics update completed")
        logger.info("=" * 60)
    
    def reindex_database(self):
        """Re-index the vector database after updating chunks"""
        logger.info("Re-indexing vector database...")
        
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "-m", "src.indexing_pipeline"],
                cwd="/Users/vaish/Documents/CursorProjects/MutualFund_RAG_FAQ",
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Vector database re-indexed successfully")
            else:
                logger.error(f"Failed to re-index: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error during re-indexing: {e}")
    
    def run_update_cycle(self):
        """Run complete update cycle"""
        self.update_all_chunks()
        self.reindex_database()


def main():
    """Main scheduler function"""
    updater = FinancialMetricsUpdater()
    
    # Schedule update every 2 days at 9:00 AM IST
    schedule.every(2).days.at("09:00").do(updater.run_update_cycle)
    
    logger.info("Scheduler started. Updates scheduled every 2 days at 09:00 IST")
    logger.info("Press Ctrl+C to stop")
    
    # Run once immediately on startup
    updater.run_update_cycle()
    
    # Keep scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
