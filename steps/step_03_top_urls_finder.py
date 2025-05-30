#!/usr/bin/env python3
"""
Step 3: Top URLs Finder using Browserbase + Bing Search
Created: Updated to use real Browserbase automation for Bing searches instead of mock implementation

INPUT: List of keywords (List[str])
OUTPUT: List of top URLs found for those keywords (List[str])

This step takes a list of keywords and searches Bing for each keyword using Browserbase automation.
It extracts the top URLs from search results and returns a combined list of unique URLs.
Uses Playwright through Browserbase for reliable web scraping.
"""

import os
import sys
import time
from typing import List
from playwright.sync_api import Playwright, sync_playwright
from browserbase import Browserbase
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def extract_urls_from_page(page, page_number=1, keyword=""):
    """Extract URLs from current Bing search results page"""
    logger.info(f"Extracting URLs from page {page_number} for keyword: '{keyword}'")
    
    results = []
    algo_count = 0
    
    # Try multiple strategies to find .b_algo containers
    try:
        # Strategy 1: Follow exact pattern
        b_content = page.query_selector('#b_content')
        algo_containers = []
        
        if b_content:
            search_results_main = b_content.query_selector('main[aria-label="Search Results"]')
            if search_results_main:
                b_results = search_results_main.query_selector('#b_results')
                if b_results:
                    algo_containers = b_results.query_selector_all('li.b_algo')
                    logger.debug(f"Strategy 1: Found {len(algo_containers)} .b_algo containers")
        
        # Strategy 2: Direct search for .b_algo
        if len(algo_containers) == 0:
            algo_containers = page.query_selector_all('.b_algo')
            logger.debug(f"Strategy 2: Found {len(algo_containers)} .b_algo containers")
        
        # Strategy 3: Look for any list items that might be results
        if len(algo_containers) == 0:
            algo_containers = page.query_selector_all('li[class*="algo"], li[data-id*="SERP"]')
            logger.debug(f"Strategy 3: Found {len(algo_containers)} alternative containers")
        
        algo_count = len(algo_containers)
        logger.info(f"Page {page_number}: Processing {algo_count} containers for '{keyword}'")
        
        # Extract URLs from each container
        for index, algo_container in enumerate(algo_containers):
            logger.debug(f"Processing container {index + 1}")
            
            # Look for the <a class="tilk"> link inside this container
            tilk_link = algo_container.query_selector('a.tilk')
            
            if tilk_link and tilk_link.get_attribute('href'):
                url = tilk_link.get_attribute('href')
                aria_label = tilk_link.get_attribute('aria-label') or ''
                title = aria_label or tilk_link.text_content().strip() or 'No title'
                
                logger.debug(f"Found tilk link: {url}")
                
                # Only add if it's not a Bing/Microsoft internal link
                if 'bing.com' not in url and 'microsoft.com' not in url:
                    results.append({
                        'url': url,
                        'title': title,
                        'keyword': keyword,
                        'container_index': index + 1,
                        'page_number': page_number
                    })
                    logger.debug(f"Added as result {len(results)}")
                else:
                    logger.debug("Skipped (internal link)")
            else:
                logger.debug(f"No .tilk link found in container {index + 1}")
                
                # Fallback: look for any external link in this container
                any_link = algo_container.query_selector('a[href^="http"]:not([href*="bing.com"]):not([href*="microsoft.com"])')
                if any_link:
                    url = any_link.get_attribute('href')
                    logger.debug(f"Found fallback link: {url}")
                    results.append({
                        'url': url,
                        'title': any_link.text_content().strip() or 'No title',
                        'keyword': keyword,
                        'container_index': index + 1,
                        'page_number': page_number,
                        'method': 'fallback'
                    })
        
    except Exception as e:
        logger.error(f"Error extracting URLs for '{keyword}': {e}")
    
    return {'results': results, 'algo_count': algo_count}

def search_keyword_on_bing(playwright: Playwright, keyword: str, max_urls: int = 3) -> List[str]:
    """
    Search for a single keyword on Bing and return top URLs
    
    Args:
        playwright: Playwright instance
        keyword: Search keyword
        max_urls: Maximum number of URLs to return per keyword
        
    Returns:
        List[str]: List of URLs found for this keyword
    """
    logger.info(f"Starting Bing search for keyword: '{keyword}'")
    
    # Get Browserbase credentials
    api_key = os.getenv('BROWSERBASE_API_KEY')
    project_id = os.getenv('BROWSERBASE_PROJECT_ID')
    
    if not api_key or not project_id:
        raise ValueError("BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID must be set in .env file")
    
    bb = Browserbase(api_key=api_key)
    
    try:
        # Create a session on Browserbase
        session = bb.sessions.create(project_id=project_id)
        logger.info(f"Created Browserbase session: {session.id}")
        
        # Connect to the remote session
        chromium = playwright.chromium
        browser = chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]
        
        try:
            # Step 1: Navigate to Bing and wait for it to fully load
            logger.info('Navigating to Bing...')
            page.goto("https://www.bing.com", wait_until='networkidle', timeout=60000)
            
            # Wait for Bing homepage to be ready
            logger.info('Waiting for Bing homepage to load...')
            page.wait_for_selector('input[name="q"], #sb_form_q', timeout=30000)
            logger.info('Bing homepage loaded successfully')
            
            # Step 2: Search for the keyword
            logger.info(f'Searching Bing for: "{keyword}"')
            
            # Find search box and submit search
            search_input = page.wait_for_selector('input[name="q"], #sb_form_q', timeout=15000)
            page.fill('input[name="q"], #sb_form_q', keyword)
            page.press('input[name="q"], #sb_form_q', 'Enter')
            
            logger.info('Search submitted, waiting for search results page to load...')
            
            # Wait for search results page structure to appear
            try:
                page.wait_for_selector('#b_content', timeout=30000)
                logger.debug('Found #b_content')
            except Exception as e:
                logger.warning('Timeout waiting for #b_content, checking what loaded...')
                current_url = page.url
                page_title = page.title()
                logger.info(f'Current URL: {current_url}')
                logger.info(f'Page title: {page_title}')
                
                if 'search?q=' not in current_url and 'bing.com/search' not in current_url:
                    raise Exception('Failed to navigate to search results page')
            
            try:
                page.wait_for_selector('main[aria-label="Search Results"]', timeout=15000)
                logger.debug('Found main[aria-label="Search Results"]')
            except Exception as e:
                logger.debug('Could not find main[aria-label="Search Results"], trying alternative...')
            
            try:
                page.wait_for_selector('#b_results', timeout=15000)
                logger.debug('Found #b_results')
            except Exception as e:
                logger.debug('Could not find #b_results, checking for any results...')
                
                # Check if there are any search results at all
                algo_containers = page.query_selector_all('.b_algo, li[class*="algo"]')
                logger.info(f'Found {len(algo_containers)} algo containers')
                
                if len(algo_containers) == 0:
                    logger.warning('No search results found on page')
                    return []
            
            # Give extra time for all results to load
            time.sleep(3)
            logger.info('Search results page loaded, proceeding with extraction...')
            
            # Step 3: Extract URLs from first page
            page1_data = extract_urls_from_page(page, 1, keyword)
            all_results = page1_data['results']
            page1_algo_count = page1_data['algo_count']
            
            logger.info(f'Page 1 summary for "{keyword}":')
            logger.info(f'- Found {page1_algo_count} .b_algo containers')
            logger.info(f'- Extracted {len(all_results)} valid URLs')
            
            # Step 4: Go to page 2 if we need more URLs and there were results on page 1
            if len(all_results) < max_urls and page1_algo_count > 0:
                logger.info(f'Need more URLs for "{keyword}" (have {len(all_results)}, want {max_urls})')
                logger.info('Looking for "Next" button to go to page 2...')
                
                # Look for next page button
                next_button_selectors = [
                    'a[aria-label="Next page"]',
                    '.b_pag a:last-child',
                    '.sb_pagN',
                    'a[href*="first="]'
                ]
                
                next_button_found = False
                
                for selector in next_button_selectors:
                    try:
                        next_button = page.query_selector(selector)
                        if next_button:
                            logger.debug(f'Found next button: {selector}')
                            next_button.click()
                            next_button_found = True
                            break
                    except Exception as e:
                        logger.debug(f'Next button selector {selector} failed')
                
                if next_button_found:
                    logger.info('Clicked next button, waiting for page 2...')
                    
                    # Wait for page 2 to load
                    page.wait_for_selector('#b_results', timeout=30000)
                    time.sleep(3)
                    
                    # Extract URLs from page 2
                    page2_data = extract_urls_from_page(page, 2, keyword)
                    page2_results = page2_data['results']
                    page2_algo_count = page2_data['algo_count']
                    
                    logger.info(f'Page 2 summary for "{keyword}":')
                    logger.info(f'- Found {page2_algo_count} .b_algo containers')
                    logger.info(f'- Extracted {len(page2_results)} valid URLs')
                    
                    # Combine results from both pages
                    all_results = all_results + page2_results
                else:
                    logger.debug('Could not find next page button')
            
            # Remove duplicates and limit to max_urls
            unique_results = []
            seen_urls = set()
            
            for result in all_results:
                if result['url'] not in seen_urls and len(unique_results) < max_urls:
                    seen_urls.add(result['url'])
                    unique_results.append(result)
            
            # Extract just the URLs
            urls_only = [result['url'] for result in unique_results]
            
            logger.info(f'Final results for "{keyword}": {len(urls_only)} URLs')
            if urls_only:
                logger.info(f'URLs found for "{keyword}":')
                for i, url in enumerate(urls_only, 1):
                    logger.info(f'  {i}. {url}')
            
            return urls_only
            
        except Exception as e:
            logger.error(f"Error during Bing search for '{keyword}': {e}")
            return []
            
        finally:
            try:
                page.close()
                browser.close()
                logger.info(f"Browserbase session replay: https://browserbase.com/sessions/{session.id}")
            except Exception as e:
                logger.debug(f"Error closing browser: {e}")
                
    except Exception as e:
        logger.error(f"Error creating Browserbase session for '{keyword}': {e}")
        return []

def execute_step(keywords: List[str]) -> List[str]:
    """
    Find top URLs for a list of keywords using Bing search via Browserbase
    
    Args:
        keywords (List[str]): List of keywords to search for
        
    Returns:
        List[str]: List of top URLs found across all keywords
        
    Raises:
        ValueError: If keywords list is empty
        Exception: If Browserbase search fails
    """
    # Validate input
    if not keywords or not isinstance(keywords, list):
        raise ValueError("Keywords must be a non-empty list")
    
    if len(keywords) == 0:
        raise ValueError("Keywords list cannot be empty")
    
    # Limit to reasonable number of keywords to avoid long execution times
    max_keywords = 10
    if len(keywords) > max_keywords:
        logger.warning(f"Too many keywords ({len(keywords)}), limiting to first {max_keywords}")
        keywords = keywords[:max_keywords]
    
    logger.info(f"Starting URL search for {len(keywords)} keywords")
    logger.info(f"Keywords: {keywords}")
    
    # Check environment variables
    api_key = os.getenv('BROWSERBASE_API_KEY')
    project_id = os.getenv('BROWSERBASE_PROJECT_ID')
    
    if not api_key or not project_id:
        error_msg = "BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID must be set in .env file"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    all_urls = []
    urls_per_keyword = 3  # Get top 3 URLs per keyword
    
    try:
        with sync_playwright() as playwright:
            for i, keyword in enumerate(keywords, 1):
                logger.info(f"Processing keyword {i}/{len(keywords)}: '{keyword}'")
                
                try:
                    # Search for this keyword
                    keyword_urls = search_keyword_on_bing(playwright, keyword, urls_per_keyword)
                    
                    if keyword_urls:
                        logger.info(f"Found {len(keyword_urls)} URLs for '{keyword}'")
                        logger.info(f"URLs for '{keyword}':")
                        for j, url in enumerate(keyword_urls, 1):
                            logger.info(f"  {j}. {url}")
                        all_urls.extend(keyword_urls)
                    else:
                        logger.warning(f"No URLs found for '{keyword}'")
                    
                    # Add small delay between searches to be respectful
                    if i < len(keywords):
                        time.sleep(2)
                        
                except Exception as e:
                    logger.error(f"Error searching for keyword '{keyword}': {e}")
                    continue
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in all_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        logger.info(f"Search completed! Found {len(unique_urls)} unique URLs from {len(keywords)} keywords")
        if unique_urls:
            logger.info("All unique URLs found:")
            for i, url in enumerate(unique_urls, 1):
                logger.info(f"  {i:2d}. {url}")
        
        return unique_urls
        
    except Exception as e:
        error_msg = f"Error during URL search: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg) from e

def main():
    """
    Main function for standalone execution
    """
    print("🔗 Top URLs Finder - Step 3")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check Browserbase credentials
    api_key = os.getenv('BROWSERBASE_API_KEY')
    project_id = os.getenv('BROWSERBASE_PROJECT_ID')
    
    if not api_key or not project_id:
        print("⚠️  BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID not found in environment")
        print("Please set them in your .env file")
        print("BROWSERBASE_API_KEY=bb_live_vgUkX6cZiwAT2VANjCxD5J9jM44")
        print("BROWSERBASE_PROJECT_ID=a9fffef8-fc15-4230-a90e-491af78c7418")
        return []
    
    # Get keywords from command line arguments or user input
    if len(sys.argv) > 1:
        # Keywords provided as command line arguments
        keywords = sys.argv[1].split(',') if ',' in sys.argv[1] else [sys.argv[1]]
        keywords = [k.strip() for k in keywords]
    else:
        # Interactive input
        keywords_input = input("Enter keywords (comma-separated): ").strip()
        if not keywords_input:
            print("No keywords provided, using default test keywords")
            keywords = ["digital marketing", "seo tools"]
        else:
            keywords = [k.strip() for k in keywords_input.split(',')]
    
    try:
        print(f"\n🚀 Searching for URLs for {len(keywords)} keywords:")
        for i, keyword in enumerate(keywords, 1):
            print(f"{i:2d}. {keyword}")
        
        urls = execute_step(keywords)
        
        print(f"\n✅ Success! Found {len(urls)} unique URLs:")
        print("-" * 60)
        for i, url in enumerate(urls, 1):
            print(f"{i:2d}. {url}")
        
        return urls
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return []

if __name__ == "__main__":
    urls = main()
    print(f"\nFinal result: {urls}") 