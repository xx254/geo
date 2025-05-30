#!/usr/bin/env python3
"""
Step 1: Keyword Generator from URL using Apify
Created: Refactored from keyword_generator_given_url.py into workflow step structure

INPUT: Website URL (string)
OUTPUT: List of keywords extracted from the website (List[str])

This step takes a website URL and uses Apify Actor to scrape and extract keywords from the website.
It tries multiple field names to extract keywords and returns a list of strings.
"""

import os
from typing import List
from apify_client import ApifyClient
from loguru import logger

def execute_step(url: str) -> List[str]:
    """
    Extract keywords from a website URL using Apify Actor
    
    Args:
        url (str): Website URL to analyze for keywords
        
    Returns:
        List[str]: List of extracted keywords from the website
        
    Raises:
        ValueError: If URL is empty or invalid
        Exception: If Apify API call fails
    """
    # Validate input
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    url = url.strip()
    if not url:
        raise ValueError("URL cannot be empty")
    
    logger.info(f"Starting keyword extraction for URL: {url}")
    
    # Get API token from environment variable
    api_token = os.getenv('APIFY_API_TOKEN')
    if not api_token:
        raise ValueError("APIFY_API_TOKEN environment variable not set")
    
    # Initialize the ApifyClient with API token
    client = ApifyClient(api_token)
    
    # Prepare the Actor input
    run_input = {
        "urls": [url],
        "proxyConfiguration": {},
    }
    
    logger.info(f"Running Apify Actor with URL: {url}")
    
    try:
        # Run the Actor and wait for it to finish
        run = client.actor("rEbWw5H3urseNjdNw").call(run_input=run_input)
        
        logger.info(f"Actor completed! Run ID: {run['id']}")
        logger.info("Extracting keywords from results...")
        
        # Extract keywords from results
        keywords_list = []
        
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            # Try to extract keyword from different possible fields
            keyword = None
            if isinstance(item, dict):
                # Possible keyword field names
                possible_keyword_fields = ['keyword', 'keywords', 'term', 'query', 'text', 'title', 'name']
                
                for field in possible_keyword_fields:
                    if field in item and item[field]:
                        if isinstance(item[field], str):
                            keyword = item[field].strip()
                            break
                        elif isinstance(item[field], list) and len(item[field]) > 0:
                            keyword = str(item[field][0]).strip()
                            break
                
                # If no standard keyword field found, use first string value
                if not keyword:
                    for key, value in item.items():
                        if isinstance(value, str) and len(value.strip()) > 0:
                            keyword = value.strip()
                            break
            
            # If still no keyword found, use string representation of item
            if not keyword:
                keyword = str(item).strip()
            
            if keyword:
                keywords_list.append(keyword)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords_list:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        logger.info(f"Extracted {len(unique_keywords)} unique keywords")
        logger.debug(f"Keywords: {unique_keywords}")
        
        return unique_keywords
        
    except Exception as e:
        error_msg = f"Error extracting keywords: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg) from e

# Legacy support - can be removed once fully migrated to workflow system
def main():
    """Legacy main function for backward compatibility"""
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter URL to analyze: ").strip()
        if not url:
            print("No URL provided, using default: rapidapi.com")
            url = "rapidapi.com"
    
    try:
        keywords = execute_step(url)
        print(f"Extracted keywords: {keywords}")
        return keywords
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    main() 