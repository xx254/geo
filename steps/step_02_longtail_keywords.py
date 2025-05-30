#!/usr/bin/env python3
"""
Step 2: Long-tail Keywords Generator using OpenAI Structured Outputs with gpt-4o
Created: Updated to use OpenAI structured outputs with gpt-4o for reliable, schema-compliant JSON responses

INPUT: List of short keywords from website analysis (List[str])
OUTPUT: List of 10-20 long-tail keywords/queries (List[str])

This step takes thousands of short keywords from step 1 and uses OpenAI gpt-4o with structured outputs
to identify the most valuable long-tail keywords that users would actually search for.
Uses Pydantic schema to ensure consistent, reliable JSON responses.
"""

import os
import sys
import json
from typing import List
from openai import OpenAI
from pydantic import BaseModel, Field
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LongTailKeywordsResponse(BaseModel):
    """Structured response for long-tail keywords generation"""
    long_tail_keywords: List[str] = Field(
        description="List of 10-20 high-quality long-tail search queries that users would actually type",
        min_items=10,
        max_items=20
    )
    reasoning: str = Field(
        description="Brief explanation of the keyword selection strategy and rationale"
    )

def create_longtail_system_prompt() -> str:
    """
    Create the system prompt for OpenAI to act as an answer engine expert
    """
    return """You are an expert in search engines, user behavior, and answer engines like ChatGPT. Your task is to analyze short keywords and identify the most valuable long-tail search queries that users would actually type when looking for information about these topics.

You understand:
- How users think and search when they need specific information
- The difference between short keywords and actual search queries
- What people type into Google, ChatGPT, Bing, or other search engines
- SEO and content marketing strategies
- User intent and search behavior patterns

Your goal is to transform a large list of short keywords into 10-20 high-quality long-tail search queries that:
1. Real users would actually type into search engines or AI assistants
2. Have clear commercial or informational intent
3. Are specific enough to drive targeted traffic
4. Represent the most valuable search opportunities from the input keywords
5. Sound natural and conversational (like how people actually talk to AI assistants)
6. Include question-based queries (how to, what is, best ways to, etc.)
7. Include problem-solving queries that users face

IMPORTANT: Focus on queries that sound like natural questions or searches people would make, not just longer versions of keywords.

Example transformations:
- "api" → "how to integrate REST API with my website step by step"
- "seo tools" → "best free seo tools for small business websites 2024"
- "digital marketing" → "what are the most effective digital marketing strategies for startups"

Return exactly 10-20 long-tail keywords that represent real user search intent."""

def create_user_prompt(keywords: List[str]) -> str:
    """
    Create the user prompt with the actual keywords to process
    """
    # Limit keywords to avoid token limits
    max_keywords = 150
    if len(keywords) > max_keywords:
        keywords = keywords[:max_keywords]
        logger.info(f"Limited keywords to first {max_keywords} to stay within token limits")
    
    keywords_text = ", ".join(keywords)
    
    return f"""Analyze these {len(keywords)} keywords from a website and identify the 10-20 most valuable long-tail search queries that users would actually search for.

Keywords: {keywords_text}

Transform these short keywords into natural, conversational long-tail search queries that:
1. Users would naturally type into search engines or ask AI assistants
2. Have clear commercial or informational value  
3. Represent the best search opportunities from these keywords
4. Sound conversational and natural
5. Include question-based formats when appropriate
6. Cover the main themes and topics present in the keyword list
7. Focus on user problems and solutions

Provide exactly 10-20 long-tail keywords that real users would search for."""

def execute_step(keywords: List[str]) -> List[str]:
    """
    Generate long-tail keywords from short keywords using OpenAI Structured Outputs
    
    Args:
        keywords (List[str]): List of short keywords from website analysis
        
    Returns:
        List[str]: List of 10-20 long-tail keywords/search queries
        
    Raises:
        ValueError: If keywords list is empty or invalid
        Exception: If OpenAI API call fails
    """
    # Validate input
    if not keywords or not isinstance(keywords, list):
        raise ValueError("Keywords must be a non-empty list")
    
    if len(keywords) == 0:
        raise ValueError("Keywords list cannot be empty")
    
    # Filter out very short or low-quality keywords
    filtered_keywords = []
    for keyword in keywords:
        if isinstance(keyword, str) and len(keyword.strip()) > 2:
            filtered_keywords.append(keyword.strip())
    
    if len(filtered_keywords) == 0:
        raise ValueError("No valid keywords found after filtering")
    
    logger.info(f"Generating long-tail keywords from {len(filtered_keywords)} short keywords using gpt-4o structured outputs")
    logger.info(f"Sample keywords: {filtered_keywords[:10]}")
    
    # Get API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        error_msg = "OPENAI_API_KEY environment variable not set. Please check your .env file."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    try:
        # Create prompts
        system_prompt = create_longtail_system_prompt()
        user_prompt = create_user_prompt(filtered_keywords)
        
        logger.info("Calling OpenAI gpt-4o API with structured outputs for long-tail keyword generation")
        logger.debug(f"System prompt length: {len(system_prompt)} characters")
        logger.debug(f"User prompt length: {len(user_prompt)} characters")
        
        # Call OpenAI API with structured outputs
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=LongTailKeywordsResponse,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract structured response
        response_data = completion.choices[0].message.parsed
        
        if not response_data:
            raise ValueError("No structured data returned from OpenAI")
        
        long_tail_keywords = response_data.long_tail_keywords
        reasoning = response_data.reasoning
        
        logger.info(f"OpenAI reasoning: {reasoning}")
        
        if not long_tail_keywords or not isinstance(long_tail_keywords, list):
            raise ValueError("Invalid response format: missing or invalid long_tail_keywords")
        
        # Validate and clean the keywords
        valid_keywords = []
        for keyword in long_tail_keywords:
            if isinstance(keyword, str) and len(keyword.strip()) > 5:
                valid_keywords.append(keyword.strip())
        
        if len(valid_keywords) == 0:
            raise ValueError("No valid long-tail keywords in OpenAI response")
        
        logger.info(f"Generated {len(valid_keywords)} long-tail keywords using structured outputs")
        logger.info("Long-tail keywords:")
        for i, keyword in enumerate(valid_keywords, 1):
            logger.info(f"  {i:2d}. {keyword}")
        
        return valid_keywords
        
    except Exception as e:
        error_msg = f"Error generating long-tail keywords with structured outputs: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg) from e

def main():
    """
    Main function for standalone execution
    """
    print("🎯 Long-tail Keywords Generator with Structured Outputs - Step 2")
    print("=" * 70)
    
    # Load environment variables
    load_dotenv()
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OPENAI_API_KEY not found in environment")
        print("Please set OPENAI_API_KEY in your .env file")
        return []
    
    # Get keywords from command line arguments or user input
    if len(sys.argv) > 1:
        # Keywords provided as command line arguments
        if sys.argv[1].startswith('[') and sys.argv[1].endswith(']'):
            # Handle JSON array input
            try:
                keywords = json.loads(sys.argv[1])
            except json.JSONDecodeError:
                keywords = [sys.argv[1]]
        else:
            # Handle comma-separated input
            keywords = sys.argv[1].split(',') if ',' in sys.argv[1] else [sys.argv[1]]
            keywords = [k.strip() for k in keywords]
    else:
        # Interactive input
        print("Enter short keywords to convert to long-tail queries.")
        print("You can enter them comma-separated or paste a list:")
        keywords_input = input("Keywords: ").strip()
        
        if not keywords_input:
            print("No keywords provided, using sample keywords for testing")
            keywords = [
                "api", "seo tools", "digital marketing", "web development", 
                "analytics", "automation", "content creation", "social media",
                "email marketing", "conversion optimization", "web design",
                "mobile apps", "cloud computing", "data analysis"
            ]
        else:
            # Try to parse as JSON first, then fall back to comma-separated
            try:
                keywords = json.loads(keywords_input) if keywords_input.startswith('[') else keywords_input.split(',')
                keywords = [k.strip() for k in keywords if isinstance(k, str)]
            except json.JSONDecodeError:
                keywords = [k.strip() for k in keywords_input.split(',')]
    
    try:
        print(f"\n🚀 Processing {len(keywords)} short keywords with gpt-4o structured outputs...")
        print("Sample input keywords:")
        for i, keyword in enumerate(keywords[:10], 1):
            print(f"  {i:2d}. {keyword}")
        if len(keywords) > 10:
            print(f"  ... and {len(keywords) - 10} more")
        
        long_tail_keywords = execute_step(keywords)
        
        print(f"\n✅ Success! Generated {len(long_tail_keywords)} long-tail keywords:")
        print("-" * 70)
        for i, keyword in enumerate(long_tail_keywords, 1):
            print(f"{i:2d}. {keyword}")
        
        return long_tail_keywords
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return []

if __name__ == "__main__":
    keywords = main()
    print(f"\nFinal result: {keywords}") 