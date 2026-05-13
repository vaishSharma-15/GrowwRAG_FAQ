"""
Retry Logic Module - Implements rate limiting and retry logic using tenacity
Handles exponential backoff and request throttling
"""

import asyncio
import logging
import time
from typing import Callable, Any
from functools import wraps
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for controlling request frequency"""
    
    def __init__(self, min_delay: float = 3.0):
        """
        Initialize rate limiter
        
        Args:
            min_delay: Minimum delay between requests in seconds
        """
        self.min_delay = min_delay
        self.last_request_time = 0.0
    
    async def acquire(self):
        """Acquire permission to make a request"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_delay:
            delay_needed = self.min_delay - time_since_last_request
            logger.info(f"Rate limiting: waiting {delay_needed:.2f} seconds")
            await asyncio.sleep(delay_needed)
        
        self.last_request_time = time.time()
    
    def reset(self):
        """Reset the rate limiter"""
        self.last_request_time = 0.0


def retry_on_failure(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying failed operations with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries in seconds
        max_wait: Maximum wait time between retries in seconds
        exceptions: Tuple of exception types to retry on
    """
    def decorator(func: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            retry=retry_if_exception_type(exceptions),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True
        )
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            return func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class RetryHandler:
    """Handles retry logic for extraction operations"""
    
    def __init__(self, max_attempts: int = 3):
        """
        Initialize retry handler
        
        Args:
            max_attempts: Maximum number of retry attempts
        """
        self.max_attempts = max_attempts
        self.rate_limiter = RateLimiter(min_delay=3.0)
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        exceptions: tuple = (Exception,),
        **kwargs
    ) -> Any:
        """
        Execute function with retry logic and rate limiting
        
        Args:
            func: Function to execute
            *args: Function arguments
            exceptions: Tuple of exception types to retry on
            **kwargs: Function keyword arguments
        
        Returns:
            Function result
        
        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                # Acquire rate limiter
                await self.rate_limiter.acquire()
                
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                logger.info(f"Operation succeeded on attempt {attempt}/{self.max_attempts}")
                return result
                
            except exceptions as e:
                last_exception = e
                logger.warning(
                    f"Attempt {attempt}/{self.max_attempts} failed: {str(e)}"
                )
                
                if attempt < self.max_attempts:
                    # Exponential backoff
                    wait_time = min(2 ** attempt, 10)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
        
        # All attempts failed
        logger.error(
            f"Operation failed after {self.max_attempts} attempts: {str(last_exception)}"
        )
        raise last_exception
    
    def reset(self):
        """Reset the retry handler"""
        self.rate_limiter.reset()
