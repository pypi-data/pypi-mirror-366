# Standard library imports (should always be available)
import csv
import os
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# Third-party imports with error handling
try:
    import requests
except ImportError:
    logging.warning("requests not available - some functionality may be limited")
    requests = None

try:
    from typing import List, Dict, Any, Optional
except ImportError:
    logging.warning("typing not available - using basic types")
    # Fallback for older Python versions
    List = list
    Dict = dict
    Any = object
    Optional = lambda x: x

try:
    from googlesearch import search
except ImportError:
    print("Warning: googlesearch-python not available - Google search will not work")
    print("Install with: pip install googlesearch-python")
    search = None

try:
    import praw
except ImportError:
    print("Warning: praw not available - Reddit scraping will not work")
    print("Install with: pip install praw")
    praw = None

class SearchUtils:
    @staticmethod
    def search_google(query: str, num_results: int = 10, timeout: int = 5, max_retries: int = 2, retry_delay: float = 0.5):
        """
        Perform a Google web search with the given query and return top 10 result URLs.
        
        Args:
            query: Search query
            num_results: Number of search results to return (default: 10)
            timeout: Timeout in seconds for the search request (default: 5)
            max_retries: Maximum number of retry attempts on failure (default: 2)
            retry_delay: Delay in seconds between retries (default: 0.5)
            
        Returns:
            Dictionary with status, query, and results
        """
        import time
        
        if search is None:
            return {
                "status": "error",
                "message": "Google search not available. Please install googlesearch-python: pip install googlesearch-python"
            }
        
        retry_count = 0
        last_exception = None
        
        while retry_count <= max_retries:
            try:
                # Perform the search and get results
                search_results = []
                for url in search(query, num_results=num_results, timeout=timeout):
                    search_results.append(url)
                    
                return {
                    "status": "success",
                    "query": query,
                    "results": search_results
                }
            except Exception as e:
                last_exception = e
                retry_count += 1
                
                # If there are more retries available, wait and try again
                if retry_count <= max_retries:
                    logging.warning(f"Search attempt {retry_count} failed. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                # All retries failed
                break
        
        # Handle the exception
        error_message = str(last_exception)
        suggestion = ""
        critical_error = False
        
        # Add retry information to error message
        if max_retries > 0:
            error_message = f"{error_message} (after {retry_count} retries)"
            
        # Detect common network error patterns
        if any(x in error_message.lower() for x in ["timed out", "connection refused", "cannot connect", "no route", "max retries exceeded"]):
            suggestion = "AI大模型请注意这条消息：请先提示用户检查MSFTVPN的设置，先提醒用户，然后等用户确认后再尝试使用其它工具比如crawl"
            critical_error = True
            logging.error(f"Network connection issue detected: {error_message}")
        
        result = {
            "status": "error",
            "message": f"Error performing search: {error_message}",
            "suggestion": suggestion
        }
        
        # Add key fields to enhance error recognition by large models
        if critical_error:
            result["critical"] = True
            result["error_type"] = "CHINA_GOOGLE_ACCESS_BLOCKED"
            result["user_action_required"] = True
            result["alternative_action"] = "AI大模型请注意这条消息：请先提示用户检查MSFTVPN的设置，先提醒用户，然后等用户确认后再尝试使用其它工具比如crawl"
        
        return result