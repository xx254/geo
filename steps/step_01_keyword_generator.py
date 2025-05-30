#!/usr/bin/env python3
"""
Step 1: Keyword Generator from URL using Apify
Created: Updated to match original keyword_generator_given_url.py with proper .env integration

INPUT: Website URL (string)
OUTPUT: List of keywords extracted from the website (List[str])

This step takes a website URL and uses Apify Actor to scrape and extract keywords from the website.
It tries multiple field names to extract keywords and returns a list of strings.
Uses the same Actor ID and logic as the original implementation: rEbWw5H3urseNjdNw
"""

import os
import sys
from typing import List
from apify_client import ApifyClient
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    logger.info(f"Starting keyword extraction for URL: {url}")
    
    # Get API token from environment variable
    api_token = os.getenv('APIFY_API_TOKEN')
    if not api_token:
        error_msg = "APIFY_API_TOKEN environment variable not set. Please check your .env file."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Initialize the ApifyClient with API token
    client = ApifyClient(api_token)
    
    # Prepare the Actor input (same as original)
    run_input = {
        "urls": [url],
        "proxyConfiguration": {},
    }
    
    logger.info(f"Running Apify Actor with URL: {url}")
    logger.info("Using Actor ID: rEbWw5H3urseNjdNw")
    
    try:
        # Run the Actor and wait for it to finish (same Actor ID as original)
        run = client.actor("rEbWw5H3urseNjdNw").call(run_input=run_input)
        
        logger.info(f"Actor completed! Run ID: {run['id']}")
        logger.info("Extracting keywords from results...")
        
        # Extract keywords from results (exact same logic as original)
        keywords_list = []
        
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            # Try to extract keyword from different possible fields
            keyword = None
            if isinstance(item, dict):
                # Possible keyword field names (same as original)
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
        
        logger.info(f"Extracted {len(keywords_list)} total keywords")
        
        # Remove duplicates while preserving order (improvement over original)
        seen = set()
        unique_keywords = []
        for keyword in keywords_list:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        logger.info(f"Returning {len(unique_keywords)} unique keywords")
        logger.debug(f"Keywords: {unique_keywords}")
        
        return unique_keywords
        
    except Exception as e:
        error_msg = f"Error extracting keywords: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg) from e

def main():
    """
    Main function for standalone execution - mirrors original behavior
    """
    print("🔍 Keyword Generator - Step 1")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Get API token from environment variable or user input (like original)
    api_token = os.getenv('APIFY_API_TOKEN')
    if not api_token:
        print("⚠️  APIFY_API_TOKEN not found in environment")
        print("Please set APIFY_API_TOKEN in your .env file or enter it directly")
        api_token = input("Enter your Apify API token: ").strip()
        if not api_token:
            print("❌ No API token provided, exiting")
            return []
    
    # Get URL from command line argument or user input
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter URL to analyze: ").strip()
        if not url:
            print("No URL provided, using default: rapidapi.com")
            url = "rapidapi.com"
    
    try:
        print(f"\n🚀 Processing URL: {url}")
        keywords = execute_step(url)
        
        print(f"\n✅ Success! Extracted {len(keywords)} keywords:")
        print("-" * 40)
        for i, keyword in enumerate(keywords, 1):
            print(f"{i:2d}. {keyword}")
        
        return keywords
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return []

if __name__ == "__main__":
    keywords = main()
    print(f"\nFinal result: {keywords}") 