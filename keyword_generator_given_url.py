#!/usr/bin/env python3
"""
Simple Apify Actor Runner
Run Apify Actor and extract keywords from results
"""

import os
from apify_client import ApifyClient

def main():
    """Run the specified Apify Actor and return list of keywords"""
    
    # Get API token from environment variable or user input
    api_token = os.getenv('APIFY_API_TOKEN')
    if not api_token:
        print("Please set APIFY_API_TOKEN environment variable or enter it directly")
        api_token = input("Enter your Apify API token: ").strip()
        if not api_token:
            print("No API token provided, exiting")
            return []
    
    # Get URL from user input
    url = input("Enter URL to analyze: ").strip()
    if not url:
        print("No URL provided, using default: rapidapi.com")
        url = "rapidapi.com"
    
    # Initialize the ApifyClient with your API token
    client = ApifyClient(api_token)
    
    # Prepare the Actor input
    run_input = {
        "urls": [url],
        "proxyConfiguration": {},
    }
    
    print(f"Running Actor with URL: {url}")
    
    try:
        # Run the Actor and wait for it to finish
        run = client.actor("rEbWw5H3urseNjdNw").call(run_input=run_input)
        
        print(f"Actor completed! Run ID: {run['id']}")
        print("Extracting keywords...")
        
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
        
        print(f"Extracted {len(keywords_list)} keywords")
        return keywords_list
        
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    keywords = main()
    print(keywords) 