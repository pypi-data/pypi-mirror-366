"""Rate limiting functionality for API calls."""

import time
from threading import Lock, Semaphore
from typing import Optional

from catscan.config import RATE_LIMIT_CALLS


class RateLimiter:
    """Thread-safe rate limiter for API calls."""
    
    def __init__(self, calls_per_second: int = RATE_LIMIT_CALLS):
        """Initialize rate limiter.
        
        Args:
            calls_per_second: Maximum number of API calls allowed per second
        """
        self.calls_per_second = calls_per_second
        self.semaphore = Semaphore(calls_per_second)
        self.lock = Lock()
        self.last_reset_time = time.time()
    
    def reset_if_needed(self):
        """Reset rate limiter if a second has passed."""
        current_time = time.time()
        if current_time - self.last_reset_time >= 1.0:
            with self.lock:
                # Double-check inside lock
                if current_time - self.last_reset_time >= 1.0:
                    # Reset the semaphore
                    self.semaphore = Semaphore(self.calls_per_second)
                    self.last_reset_time = current_time
    
    def acquire(self, timeout: Optional[float] = None) -> bool:
        """Acquire a rate limit permit.
        
        Args:
            timeout: Maximum time to wait for permit (None = blocking)
            
        Returns:
            True if permit acquired, False if timeout
        """
        self.reset_if_needed()
        return self.semaphore.acquire(timeout=timeout)
    
    def release(self):
        """Release a rate limit permit."""
        self.semaphore.release()
    
    def __enter__(self):
        """Context manager entry."""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
        return False


# Global rate limiter instance
rate_limiter = RateLimiter()