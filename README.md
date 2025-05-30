# 🚀 Extensible Website Analysis Workflow

An extensible, modular workflow system for website analysis, keyword research, and competitive intelligence. Built with Python, this system allows you to easily add, remove, and modify steps in your analysis pipeline.

## 🏗️ Architecture Overview

The system is built around a **linear workflow** where each step's output becomes the next step's input. This design makes it easy for teams to work on different steps independently while maintaining a clear data flow.

```
Website URL → Extract Keywords → Generate Long-tail → Find Top URLs → ... → Final Results
```

### Core Components

- **`workflow_core.py`** - Main workflow engine that orchestrates step execution
- **`steps/`** - Directory containing individual workflow steps
- **`workflow_config.json`** - Configuration file defining step order and parameters
- **`main.py`** - CLI interface and execution modes
- **`requirements.txt`** - All necessary dependencies

## 📦 Installation

1. **Clone and setup**:
   ```bash
   git clone <your-repo>
   cd geo
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp env.template .env
   # Edit .env with your API keys
   ```

3. **Verify installation**:
   ```bash
   python main.py --list-steps
   ```

## 🔧 Configuration

### Environment Variables

Copy `env.template` to `.env` and fill in your API keys:

```env
# Required
APIFY_API_TOKEN=your_apify_token_here

# Optional (enables specific steps)
OPENAI_API_KEY=your_openai_key_here
BROWSERBASE_API_KEY=your_browserbase_key_here
FIRECRAWL_API_KEY=your_firecrawl_key_here
```

### Workflow Configuration

Edit `workflow_config.json` to customize your workflow:

```json
{
  "workflow_name": "Website Analysis Pipeline",
  "steps": [
    {
      "name": "Extract Keywords from Website",
      "module_name": "steps.step_01_keyword_generator",
      "function_name": "execute_step",
      "description": "Extract initial keywords from website URL using Apify Actor",
      "input_type": "str (website URL)",
      "output_type": "List[str] (extracted keywords)",
      "enabled": true
    }
  ]
}
```

## 🚀 Usage

### Interactive Mode
```bash
python main.py
```
Best for experimentation and one-off analyses.

### Command Line Mode
```bash
# Analyze single URL
python main.py --url https://example.com

# With verbose logging
python main.py --url example.com -v
```

### Batch Processing
```bash
# Create a file with URLs (one per line)
echo -e "example.com\ntest.com\nsite.com" > urls.txt
python main.py --batch urls.txt
```

### List Available Steps
```bash
python main.py --list-steps
```

## 🧩 Current Workflow Steps

### Step 1: Extract Keywords from Website
- **Input**: Website URL (string)
- **Output**: List of keywords (List[str])
- **Description**: Uses Apify Actor to scrape and extract initial keywords from a website

### Step 2: Generate Long-tail Keywords  
- **Input**: Base keywords (List[str])
- **Output**: Expanded keyword list (List[str])
- **Description**: Uses OpenAI to generate long-tail keyword variations for better SEO targeting

### Step 3: Find Top URLs for Keywords
- **Input**: Keywords (List[str])
- **Output**: Keyword-to-URLs mapping (Dict[str, List[str]])
- **Description**: Uses Browserbase to find top-ranking URLs for competitive analysis

## 🔧 Adding New Steps

### 1. Create Step Module

Create a new file in `steps/` directory:

```python
#!/usr/bin/env python3
"""
Step X: Your Step Name
Created: Description of what this step does

INPUT: Description of expected input type
OUTPUT: Description of output type

Detailed description of the step's functionality.
"""

from typing import Any
from loguru import logger

def execute_step(input_data: Any) -> Any:
    """
    Main step execution function
    
    Args:
        input_data: Data from previous step
        
    Returns:
        Processed data for next step
        
    Raises:
        ValueError: If input validation fails
        Exception: If step execution fails
    """
    # Validate input
    if not input_data:
        raise ValueError("Input data is required")
    
    logger.info("Starting step execution")
    
    try:
        # Your step logic here
        result = process_data(input_data)
        
        logger.info(f"Step completed successfully")
        return result
        
    except Exception as e:
        error_msg = f"Error in step: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg) from e

def process_data(data):
    """Helper function for step logic"""
    # Implement your step's logic
    return data

# Test function for standalone execution
def main():
    """Test function"""
    test_data = "your test input"
    try:
        result = execute_step(test_data)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
```

### 2. Update Configuration

Add your step to `workflow_config.json`:

```json
{
  "name": "Your Step Name",
  "module_name": "steps.step_XX_your_step",
  "function_name": "execute_step",
  "description": "What your step does",
  "input_type": "Expected input type",
  "output_type": "Expected output type", 
  "enabled": true
}
```

### 3. Test Your Step

```bash
# Test standalone
python steps/step_XX_your_step.py

# Test in workflow
python main.py --list-steps
python main.py --url test.com
```

## 🏗️ Step Development Guidelines

### Function Contract
- Every step must have an `execute_step(input_data) -> output_data` function
- Include comprehensive docstrings with input/output types
- Validate inputs and handle errors gracefully
- Use `loguru` for consistent logging

### Input/Output Types
- **String**: Simple text data (URLs, text content)
- **List[str]**: Lists of strings (keywords, URLs)
- **Dict**: Structured data with key-value pairs
- **Custom**: Define your own data structures as needed

### Error Handling
- Validate inputs early and provide clear error messages
- Log progress and debug information
- Raise exceptions with descriptive messages
- Don't fail silently - let the workflow engine handle retries

### Testing
- Include a `main()` function for standalone testing
- Test with various input types and edge cases
- Verify output format matches specification

## 📊 Workflow Results

Results are saved in the `outputs/` directory:

```
outputs/
├── workflow.log                          # Execution logs
├── workflow_result_20241201_143022.json  # Final results
└── cache/                                # Intermediate step results
    ├── Extract_Keywords_result.json
    ├── Generate_Long-tail_result.json
    └── Find_Top_URLs_result.json
```

## 🔄 Common Workflow Patterns

### Sequential Processing
Current default - each step processes output from previous step.

### Parallel Processing (Future)
For steps that can run independently:
```json
{
  "execution_mode": "parallel",
  "parallel_groups": [
    ["step_a", "step_b"],
    ["step_c"]
  ]
}
```

### Conditional Steps (Future)
Steps that run based on conditions:
```json
{
  "conditions": {
    "run_if": "previous_step_output.length > 10"
  }
}
```

## 🤝 Team Collaboration

### Division of Work
1. **Step Developer**: Focus on individual step logic
2. **Integration Developer**: Work on workflow engine improvements
3. **Configuration Manager**: Maintain workflow definitions
4. **QA Engineer**: Test individual steps and full workflows

### Best Practices
- Each step is self-contained and testable
- Clear input/output contracts prevent integration issues
- Use descriptive naming for steps and functions
- Document any external dependencies or API requirements
- Version your step implementations

## 🐛 Troubleshooting

### Common Issues

**Environment Variables Not Set**
```bash
python main.py --skip-env-check  # Skip validation
```

**Step Import Errors**
```bash
# Check step module syntax
python -m py_compile steps/step_XX_name.py
```

**API Rate Limits**
- Adjust delays in step implementations
- Consider caching intermediate results
- Use batch processing for multiple URLs

### Debug Mode
```bash
python main.py --url example.com -v  # Verbose logging
```

### Check Logs
```bash
tail -f outputs/workflow.log
```

## 🔮 Future Enhancements

- [ ] Web dashboard for workflow monitoring
- [ ] Parallel step execution
- [ ] Conditional step execution
- [ ] Step dependency management
- [ ] Real-time progress tracking
- [ ] Workflow templates
- [ ] Integration with cloud services
- [ ] API endpoints for workflow execution

## 📝 Contributing

1. Follow the step development guidelines
2. Include comprehensive tests
3. Update documentation
4. Add your step to the example configurations

---

**Built for scalability and maintainability** 🚀

This system is designed to grow with your needs. Start simple, add complexity as required, and always maintain clear separation between steps for maximum team productivity. 