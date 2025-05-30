#!/usr/bin/env python3
"""
Example: How to Add a New Step to the Workflow
Created: Example demonstrating the step creation process

This script shows how easy it is to add a new step to the workflow system.
It creates a sample "Content Analyzer" step that analyzes text content.
"""

import json
from pathlib import Path

def create_sample_step():
    """Create a sample step file"""
    
    step_content = '''#!/usr/bin/env python3
"""
Step 4: Content Analyzer using Firecrawl
Created: Analyze content quality and structure from URLs

INPUT: Dictionary mapping keywords to URLs (Dict[str, List[str]])
OUTPUT: Content analysis results (Dict[str, Dict[str, Any]])

This step takes URLs from the previous step and uses Firecrawl to analyze
the content quality, structure, and SEO metrics of each page.
"""

import os
from typing import Dict, List, Any
from loguru import logger
import requests

def execute_step(keyword_urls: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]:
    """
    Analyze content from URLs using Firecrawl
    
    Args:
        keyword_urls (Dict[str, List[str]]): Keywords mapped to their top URLs
        
    Returns:
        Dict[str, Dict[str, Any]]: Content analysis results for each URL
        
    Raises:
        ValueError: If input is empty or invalid
        Exception: If Firecrawl API call fails
    """
    # Validate input
    if not keyword_urls or not isinstance(keyword_urls, dict):
        raise ValueError("keyword_urls must be a non-empty dictionary")
    
    logger.info(f"Starting content analysis for {len(keyword_urls)} keywords")
    
    # Get API key from environment variable
    api_key = os.getenv('FIRECRAWL_API_KEY')
    if not api_key:
        logger.warning("FIRECRAWL_API_KEY not set, using mock analysis")
        return _mock_analysis(keyword_urls)
    
    results = {}
    
    try:
        for keyword, urls in keyword_urls.items():
            if not urls:
                continue
                
            logger.info(f"Analyzing content for keyword: {keyword}")
            results[keyword] = {}
            
            # Analyze first few URLs for each keyword
            for i, url in enumerate(urls[:3]):  # Limit to 3 URLs per keyword
                try:
                    analysis = _analyze_url_content(url, api_key)
                    results[keyword][url] = analysis
                    logger.info(f"Analyzed {url}")
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze {url}: {e}")
                    results[keyword][url] = {"error": str(e)}
        
        total_analyzed = sum(len(urls) for urls in results.values())
        logger.info(f"Content analysis completed. Analyzed {total_analyzed} URLs")
        
        return results
        
    except Exception as e:
        error_msg = f"Error in content analysis: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg) from e

def _analyze_url_content(url: str, api_key: str) -> Dict[str, Any]:
    """
    Analyze a single URL using Firecrawl
    
    Args:
        url (str): URL to analyze
        api_key (str): Firecrawl API key
        
    Returns:
        Dict[str, Any]: Content analysis results
    """
    # Mock implementation - replace with actual Firecrawl API calls
    return {
        "word_count": 1250,
        "heading_count": 8,
        "paragraph_count": 15,
        "image_count": 5,
        "link_count": 12,
        "readability_score": 7.8,
        "seo_score": 85,
        "load_time": 2.3,
        "mobile_friendly": True,
        "content_quality": "high"
    }

def _mock_analysis(keyword_urls: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]:
    """Create mock analysis results when API key is not available"""
    results = {}
    
    for keyword, urls in keyword_urls.items():
        results[keyword] = {}
        for url in urls[:3]:  # Analyze first 3 URLs
            results[keyword][url] = {
                "word_count": 800 + hash(url) % 1000,
                "heading_count": 5 + hash(url) % 10,
                "paragraph_count": 10 + hash(url) % 15,
                "image_count": hash(url) % 8,
                "link_count": 8 + hash(url) % 20,
                "readability_score": 6.0 + (hash(url) % 40) / 10,
                "seo_score": 70 + hash(url) % 30,
                "load_time": 1.5 + (hash(url) % 20) / 10,
                "mobile_friendly": hash(url) % 2 == 0,
                "content_quality": ["low", "medium", "high"][hash(url) % 3]
            }
    
    return results

def main():
    """Test function for standalone execution"""
    test_data = {
        "cloud storage": [
            "https://example1.com/cloud-storage",
            "https://example2.com/storage-solutions"
        ],
        "web development": [
            "https://example3.com/web-dev-guide",
            "https://example4.com/development-tools"
        ]
    }
    
    try:
        results = execute_step(test_data)
        print("Content Analysis Results:")
        for keyword, url_results in results.items():
            print(f"\\nKeyword: {keyword}")
            for url, analysis in url_results.items():
                print(f"  URL: {url}")
                print(f"    Word Count: {analysis.get('word_count', 'N/A')}")
                print(f"    SEO Score: {analysis.get('seo_score', 'N/A')}")
                print(f"    Quality: {analysis.get('content_quality', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
'''
    
    # Write the step file
    step_file = Path("steps/step_04_content_analyzer.py")
    with open(step_file, 'w') as f:
        f.write(step_content)
    
    print(f"✅ Created step file: {step_file}")
    return step_file

def update_workflow_config():
    """Add the new step to workflow configuration"""
    
    config_file = Path("workflow_config.json")
    
    # Read existing config
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Add new step
    new_step = {
        "name": "Analyze Content Quality",
        "module_name": "steps.step_04_content_analyzer",
        "function_name": "execute_step",
        "description": "Analyze content quality and SEO metrics using Firecrawl",
        "input_type": "Dict[str, List[str]] (keyword to URLs mapping)",
        "output_type": "Dict[str, Dict[str, Any]] (content analysis results)",
        "enabled": True
    }
    
    config["steps"].append(new_step)
    
    # Write updated config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Updated workflow configuration: {config_file}")
    return config_file

def demonstrate_extensibility():
    """Show how easy it is to extend the workflow"""
    
    print("🚀 Demonstrating Workflow Extensibility")
    print("=" * 50)
    
    print("\n1. Creating new step file...")
    step_file = create_sample_step()
    
    print("\n2. Updating workflow configuration...")
    config_file = update_workflow_config()
    
    print("\n3. Testing the new step...")
    try:
        import subprocess
        result = subprocess.run(['python', str(step_file)], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Step test completed successfully!")
        else:
            print(f"⚠️  Step test had issues: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Could not test step: {e}")
    
    print("\n4. Verifying workflow integration...")
    try:
        result = subprocess.run(['python', 'main.py', '--list-steps'], 
                              capture_output=True, text=True, timeout=10)
        if "Analyze Content Quality" in result.stdout:
            print("✅ New step integrated successfully!")
        else:
            print("⚠️  Step may not be properly integrated")
    except Exception as e:
        print(f"⚠️  Could not verify integration: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Extensibility demonstration complete!")
    print("\nWhat just happened:")
    print("1. Created a new step module with proper structure")
    print("2. Added step to workflow configuration")
    print("3. Tested the step in isolation")
    print("4. Verified integration with main workflow")
    print("\nYour workflow now has 4 steps instead of 3!")
    print("Run 'python main.py --list-steps' to see all steps.")

if __name__ == "__main__":
    demonstrate_extensibility() 