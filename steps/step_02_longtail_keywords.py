#!/usr/bin/env python3
"""
Step 2: Long-tail Keyword Generator using OpenAI
Created: Generate long-tail keyword variations using OpenAI GPT

INPUT: List of base keywords (List[str])
OUTPUT: Expanded list of long-tail keywords (List[str])

This step takes a list of base keywords and uses OpenAI to generate long-tail keyword variations
that are more specific and targeted for better SEO and content strategy.
"""

import os
from typing import List
from openai import OpenAI
from loguru import logger

def execute_step(base_keywords: List[str]) -> List[str]:
    """
    Generate long-tail keywords from base keywords using OpenAI
    
    Args:
        base_keywords (List[str]): List of base keywords to expand
        
    Returns:
        List[str]: Expanded list of long-tail keywords
        
    Raises:
        ValueError: If input is empty or invalid
        Exception: If OpenAI API call fails
    """
    # Validate input
    if not base_keywords or not isinstance(base_keywords, list):
        raise ValueError("base_keywords must be a non-empty list")
    
    if not all(isinstance(keyword, str) for keyword in base_keywords):
        raise ValueError("All keywords must be strings")
    
    # Filter out empty keywords
    valid_keywords = [kw.strip() for kw in base_keywords if kw.strip()]
    
    if not valid_keywords:
        raise ValueError("No valid keywords provided")
    
    logger.info(f"Generating long-tail keywords for {len(valid_keywords)} base keywords")
    
    # Get API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Prepare keywords string for prompt
    keywords_text = ", ".join(valid_keywords[:10])  # Limit to first 10 to avoid token limits
    
    prompt = f"""
    Generate long-tail keyword variations for the following base keywords: {keywords_text}

    Instructions:
    1. Create 3-5 long-tail variations for each base keyword
    2. Long-tail keywords should be 3-7 words long
    3. Make them specific and searchable
    4. Focus on commercial intent and informational queries
    5. Include question-based keywords (how, what, why, where, when)
    6. Return only the keywords, one per line, no numbering or bullets

    Example:
    If base keyword is "cloud storage", generate:
    - best cloud storage for small business
    - how to choose cloud storage service
    - secure cloud storage solutions
    - cloud storage pricing comparison
    - what is cloud storage used for
    """
    
    try:
        logger.info("Calling OpenAI API for long-tail keyword generation")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert SEO keyword researcher who generates high-quality long-tail keywords."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Extract and process the response
        generated_text = response.choices[0].message.content.strip()
        
        # Split into individual keywords and clean them
        longtail_keywords = []
        for line in generated_text.split('\n'):
            keyword = line.strip()
            # Remove common prefixes/bullets
            keyword = keyword.lstrip('- • * 1234567890. ')
            if keyword and len(keyword.split()) >= 3:  # Ensure it's actually long-tail
                longtail_keywords.append(keyword)
        
        # Combine original keywords with long-tail variants
        all_keywords = valid_keywords + longtail_keywords
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in all_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower not in seen:
                seen.add(keyword_lower)
                unique_keywords.append(keyword)
        
        logger.info(f"Generated {len(longtail_keywords)} long-tail keywords, total: {len(unique_keywords)}")
        logger.debug(f"Sample long-tail keywords: {longtail_keywords[:5]}")
        
        return unique_keywords
        
    except Exception as e:
        error_msg = f"Error generating long-tail keywords: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg) from e

# Standalone testing function
def main():
    """Test function for standalone execution"""
    test_keywords = ["cloud storage", "web development", "digital marketing"]
    
    try:
        expanded_keywords = execute_step(test_keywords)
        print(f"Input keywords: {test_keywords}")
        print(f"Expanded to {len(expanded_keywords)} total keywords:")
        for i, keyword in enumerate(expanded_keywords, 1):
            print(f"{i}. {keyword}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 