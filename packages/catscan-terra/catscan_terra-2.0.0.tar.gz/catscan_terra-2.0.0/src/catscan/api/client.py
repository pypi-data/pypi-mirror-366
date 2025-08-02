"""HTTP client with connection pooling and retry logic."""

import time
import random
from typing import Dict, Optional

import requests
from rich.console import Console

from catscan.config import API_TIMEOUT, CONNECTION_POOL_SIZE, MAX_RETRIES, RATE_LIMIT_CALLS
from catscan.exceptions import APIError, RateLimitError
from catscan.api.rate_limiter import rate_limiter
from catscan.utils import get_logger

logger = get_logger('catscan.api.client')
console = Console()

# Global session for connection pooling
_session: Optional[requests.Session] = None


def get_session() -> requests.Session:
    """Get or create a requests session with connection pooling.
    
    Returns:
        Configured requests session with connection pooling
    """
    global _session
    if _session is None:
        _session = requests.Session()
        # Configure connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=CONNECTION_POOL_SIZE,
            pool_maxsize=CONNECTION_POOL_SIZE,
            max_retries=0  # We handle retries ourselves
        )
        _session.mount('http://', adapter)
        _session.mount('https://', adapter)
        
        # Set default headers for the session
        _session.headers.update({
            "Content-Type": "application/vnd.api+json"
        })
    return _session


def close_session():
    """Close the global session and cleanup connections."""
    global _session
    if _session is not None:
        _session.close()
        _session = None


def make_api_request(
    url: str, 
    headers: Dict[str, str], 
    retry_count: int = MAX_RETRIES,
    use_session: bool = True,
    timeout: int = API_TIMEOUT
) -> Optional[requests.Response]:
    """Make API request with retry logic, exponential backoff, and connection pooling.
    
    Args:
        url: The URL to request
        headers: Request headers (must include Authorization)
        retry_count: Number of retries to attempt
        use_session: Whether to use connection pooling
        timeout: Request timeout in seconds
        
    Returns:
        Response object if successful, None if all retries failed
        
    Raises:
        APIError: For non-retryable errors (4xx except 429)
        RateLimitError: If rate limited after all retries
    """
    # Log the request
    logger.debug(f"API Request: GET {url}")
    logger.debug(f"Using session: {use_session}, Timeout: {timeout}s, Max retries: {retry_count}")
    
    # Use rate limiter
    with rate_limiter:
        logger.debug(f"Rate limiter acquired for request to {url}")
        
        for attempt in range(retry_count):
            try:
                # Use session for connection pooling if available
                if use_session:
                    sess = get_session()
                    # Update authorization header for this request
                    response = sess.get(
                        url, 
                        headers={"Authorization": headers.get("Authorization", "")},
                        timeout=timeout
                    )
                else:
                    # Direct request without session
                    response = requests.get(
                        url,
                        headers={
                            "Authorization": headers.get("Authorization", ""),
                            "Content-Type": "application/vnd.api+json"
                        },
                        timeout=timeout
                    )
                
                # Handle different status codes
                if response.status_code == 429:
                    # Rate limited - check for retry-after header
                    retry_after = response.headers.get('Retry-After', 2 ** attempt)
                    logger.warning(f"Rate limited (429) on {url}. Retry-After: {retry_after}s")
                    
                    if attempt < retry_count - 1:
                        console.print(f"[yellow]Rate limited. Waiting {retry_after} seconds...[/yellow]")
                        logger.info(f"Retry attempt {attempt + 1}/{retry_count} after {retry_after}s wait")
                        time.sleep(float(retry_after))
                        continue
                    else:
                        logger.error(f"Rate limited after {retry_count} attempts on {url}")
                        raise RateLimitError(f"Rate limited after {retry_count} attempts")
                
                elif 400 <= response.status_code < 500:
                    # Client error (4xx) - don't retry except for 429
                    error_msg = f"Client error {response.status_code} for {url}: {response.text[:200]}"
                    logger.error(error_msg)
                    raise APIError(error_msg)
                
                # For all other errors, raise_for_status will handle them
                response.raise_for_status()
                logger.debug(f"API Response: {response.status_code} from {url} (attempt {attempt + 1})")
                return response
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout on {url} (attempt {attempt + 1}/{retry_count})")
                if attempt < retry_count - 1:
                    # Exponential backoff with jitter
                    base_wait = 2 ** attempt
                    jitter = random.uniform(0, base_wait * 0.1)  # Add up to 10% jitter
                    wait_time = base_wait + jitter
                    
                    console.print(f"[yellow]Request timeout. Retrying in {wait_time:.1f} seconds...[/yellow]")
                    logger.info(f"Retrying after timeout. Wait: {wait_time:.1f}s (with jitter)")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Request timeout after all retries on {url}")
                    console.print("[red]Request timeout after all retries[/red]")
                    return None
                    
            except requests.exceptions.RequestException as e:
                # Don't retry for APIError (4xx errors)
                if isinstance(e, APIError):
                    raise
                
                logger.warning(f"Request error on {url}: {type(e).__name__}: {str(e)}")
                if attempt < retry_count - 1:
                    # Exponential backoff with jitter
                    base_wait = 2 ** attempt
                    jitter = random.uniform(0, base_wait * 0.1)  # Add up to 10% jitter
                    wait_time = base_wait + jitter
                    
                    console.print(f"[yellow]Request error: {e}. Retrying in {wait_time:.1f} seconds...[/yellow]")
                    logger.info(f"Retrying after error. Wait: {wait_time:.1f}s (with jitter)")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Request failed after all retries on {url}: {str(e)}", exc_info=True)
                    console.print(f"[red]Request failed after all retries: {e}[/red]")
                    return None
        
        logger.error(f"Request failed - exited retry loop without success for {url}")
        return None