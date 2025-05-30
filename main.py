#!/usr/bin/env python3
"""
Main Workflow Execution Script
Created: Main entry point for running the extensible website analysis workflow

This script provides multiple ways to run the workflow:
1. Interactive mode - prompts for input
2. Command line mode - accepts URL as argument
3. Batch mode - processes multiple URLs from file
4. Configuration mode - loads workflow from config file
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from loguru import logger

# Import our workflow engine
from workflow_core import WorkflowEngine, WorkflowStep

# Load environment variables
load_dotenv()

def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level"""
    log_level = "DEBUG" if verbose else "INFO"
    logger.remove()
    logger.add(sys.stderr, level=log_level, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

def run_workflow_interactive() -> None:
    """Run workflow in interactive mode with user prompts"""
    print("🚀 Website Analysis Workflow - Interactive Mode")
    print("=" * 50)
    
    # Get URL from user
    url = input("\n📝 Enter the website URL to analyze: ").strip()
    if not url:
        print("❌ No URL provided. Exiting.")
        return
    
    if not (url.startswith('http://') or url.startswith('https://')):
        url = f"https://{url}"
    
    print(f"🔍 Starting analysis for: {url}")
    
    # Initialize and run workflow
    engine = WorkflowEngine()
    engine.register_steps_from_config("workflow_config.json")
    
    print(f"\n📋 Workflow Summary:")
    engine.list_steps()
    
    # Confirm execution
    confirm = input("\n▶️  Continue with workflow execution? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Workflow cancelled.")
        return
    
    print("\n🏃‍♂️ Running workflow...")
    result = engine.execute_workflow(url)
    
    # Display results
    print("\n" + "=" * 50)
    if result.success:
        print("✅ Workflow completed successfully!")
        print(f"⏱️  Execution time: {result.execution_time:.2f} seconds")
        print(f"📊 Steps executed: {', '.join(result.steps_executed)}")
        print(f"📁 Check ./outputs/ directory for detailed results")
        
        # Show sample of final data if it's reasonable size
        if isinstance(result.data, dict) and len(str(result.data)) < 1000:
            print(f"\n📈 Final Results Preview:")
            for key, value in result.data.items():
                if isinstance(value, list):
                    print(f"  {key}: {len(value)} items")
                    if value:
                        print(f"    Sample: {value[0]}")
                else:
                    print(f"  {key}: {value}")
    else:
        print("❌ Workflow failed!")
        print(f"💥 Error: {result.error_message}")
        print(f"📊 Steps completed before failure: {', '.join(result.steps_executed)}")

def run_workflow_cli(url: str, config_file: str = "workflow_config.json") -> None:
    """Run workflow from command line with given URL"""
    logger.info(f"Starting CLI workflow for URL: {url}")
    
    if not (url.startswith('http://') or url.startswith('https://')):
        url = f"https://{url}"
    
    # Initialize and run workflow
    engine = WorkflowEngine()
    engine.register_steps_from_config(config_file)
    
    result = engine.execute_workflow(url)
    
    if result.success:
        logger.info("✅ Workflow completed successfully!")
        print(f"Final result: {result.data}")
    else:
        logger.error(f"❌ Workflow failed: {result.error_message}")
        sys.exit(1)

def run_workflow_batch(urls_file: str, config_file: str = "workflow_config.json") -> None:
    """Run workflow for multiple URLs from a file"""
    logger.info(f"Starting batch workflow from file: {urls_file}")
    
    if not Path(urls_file).exists():
        logger.error(f"URLs file not found: {urls_file}")
        sys.exit(1)
    
    # Read URLs from file
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    if not urls:
        logger.error("No URLs found in file")
        sys.exit(1)
    
    logger.info(f"Processing {len(urls)} URLs")
    
    # Initialize workflow engine
    engine = WorkflowEngine()
    engine.register_steps_from_config(config_file)
    
    results = []
    for i, url in enumerate(urls, 1):
        logger.info(f"Processing URL {i}/{len(urls)}: {url}")
        
        if not (url.startswith('http://') or url.startswith('https://')):
            url = f"https://{url}"
        
        result = engine.execute_workflow(url)
        results.append({
            'url': url,
            'success': result.success,
            'data': result.data,
            'error': result.error_message
        })
        
        if result.success:
            logger.info(f"✅ Completed {url}")
        else:
            logger.error(f"❌ Failed {url}: {result.error_message}")
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    logger.info(f"Batch processing complete: {successful}/{len(results)} successful")

def list_workflow_steps(config_file: str = "workflow_config.json") -> None:
    """List all available workflow steps"""
    engine = WorkflowEngine()
    engine.register_steps_from_config(config_file)
    
    print("📋 Available Workflow Steps:")
    print("=" * 50)
    engine.list_steps()

def validate_environment() -> bool:
    """Check if required environment variables are set"""
    required_vars = ['APIFY_API_TOKEN']  # Add others as needed
    optional_vars = ['OPENAI_API_KEY', 'BROWSERBASE_API_KEY', 'FIRECRAWL_API_KEY']
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_required:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_required)}")
        logger.error("Please set these variables in your .env file or environment")
        return False
    
    if missing_optional:
        logger.warning(f"⚠️  Optional environment variables not set: {', '.join(missing_optional)}")
        logger.warning("Some workflow steps may be skipped or fail")
    
    return True

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Website Analysis Workflow - Extensible pipeline for website keyword research and analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Interactive mode
  python main.py --url example.com         # Analyze single URL
  python main.py --batch urls.txt          # Process multiple URLs
  python main.py --list-steps              # Show available steps
  python main.py --url example.com -v      # Verbose logging
        """
    )
    
    parser.add_argument(
        '--url', '-u',
        help='Website URL to analyze'
    )
    
    parser.add_argument(
        '--batch', '-b',
        help='File containing URLs to process (one per line)'
    )
    
    parser.add_argument(
        '--config', '-c',
        default='workflow_config.json',
        help='Workflow configuration file (default: workflow_config.json)'
    )
    
    parser.add_argument(
        '--list-steps', '-l',
        action='store_true',
        help='List available workflow steps and exit'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--skip-env-check',
        action='store_true',
        help='Skip environment variable validation'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Validate environment unless skipped
    if not args.skip_env_check and not validate_environment():
        sys.exit(1)
    
    # Handle different modes
    if args.list_steps:
        list_workflow_steps(args.config)
    elif args.url:
        run_workflow_cli(args.url, args.config)
    elif args.batch:
        run_workflow_batch(args.batch, args.config)
    else:
        run_workflow_interactive()

if __name__ == "__main__":
    main() 