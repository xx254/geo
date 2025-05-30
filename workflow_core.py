#!/usr/bin/env python3
"""
Core Workflow Engine
Created: Initial implementation of extensible step-based workflow system

This module provides the core infrastructure for running a linear workflow where:
- Each step is a separate function/module
- Output of one step becomes input of the next step
- Steps can be easily added, removed, or reordered
- Each step has clear input/output contracts
"""

import os
import json
import importlib
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import traceback
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

@dataclass
class WorkflowStep:
    """
    Represents a single step in the workflow
    
    Attributes:
        name: Human readable name of the step
        module_name: Python module name containing the step function
        function_name: Function name to execute
        description: What this step does
        input_type: Expected input type/format
        output_type: Expected output type/format
        enabled: Whether this step should be executed
    """
    name: str
    module_name: str
    function_name: str
    description: str
    input_type: str
    output_type: str
    enabled: bool = True

@dataclass
class WorkflowResult:
    """
    Contains the result of workflow execution
    
    Attributes:
        success: Whether workflow completed successfully
        data: Final output data
        steps_executed: List of step names that were executed
        execution_time: Total execution time in seconds
        error_message: Error message if workflow failed
        step_results: Individual results from each step
    """
    success: bool
    data: Any
    steps_executed: List[str]
    execution_time: float
    error_message: Optional[str] = None
    step_results: Dict[str, Any] = None

class WorkflowEngine:
    """
    Main workflow execution engine
    
    Manages step registration, execution order, data flow, and error handling
    """
    
    def __init__(self, output_dir: str = None, cache_dir: str = None):
        """
        Initialize the workflow engine
        
        Args:
            output_dir: Directory to save workflow outputs
            cache_dir: Directory for caching intermediate results
        """
        self.steps: List[WorkflowStep] = []
        self.output_dir = Path(output_dir or os.getenv('WORKFLOW_OUTPUT_DIR', './outputs'))
        self.cache_dir = Path(cache_dir or os.getenv('WORKFLOW_CACHE_DIR', './cache'))
        
        # Create directories if they don't exist
        self.output_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Configure logging
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        logger.add(self.output_dir / "workflow.log", level=log_level, rotation="1 MB")
        
    def register_step(self, step: WorkflowStep) -> None:
        """
        Register a new step in the workflow
        
        Args:
            step: WorkflowStep instance to register
        """
        logger.info(f"Registering step: {step.name}")
        self.steps.append(step)
        
    def register_steps_from_config(self, config_path: str) -> None:
        """
        Register multiple steps from a configuration file
        
        Args:
            config_path: Path to JSON configuration file
        """
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        for step_config in config['steps']:
            step = WorkflowStep(**step_config)
            self.register_step(step)
    
    def _load_step_function(self, module_name: str, function_name: str) -> Callable:
        """
        Dynamically load a step function from a module
        
        Args:
            module_name: Name of the Python module
            function_name: Name of the function to load
            
        Returns:
            The loaded function
        """
        try:
            module = importlib.import_module(module_name)
            return getattr(module, function_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Could not load function {function_name} from module {module_name}: {e}")
    
    def _save_intermediate_result(self, step_name: str, data: Any) -> None:
        """
        Save intermediate result to cache
        
        Args:
            step_name: Name of the step
            data: Data to cache
        """
        cache_file = self.cache_dir / f"{step_name}_result.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Could not cache result for step {step_name}: {e}")
    
    def execute_workflow(self, initial_input: Any, save_intermediate: bool = True) -> WorkflowResult:
        """
        Execute the complete workflow
        
        Args:
            initial_input: Input data for the first step
            save_intermediate: Whether to save intermediate results
            
        Returns:
            WorkflowResult containing execution details and final output
        """
        start_time = datetime.now()
        steps_executed = []
        step_results = {}
        current_data = initial_input
        
        logger.info(f"Starting workflow execution with {len(self.steps)} steps")
        logger.info(f"Initial input: {initial_input}")
        
        try:
            for i, step in enumerate(self.steps):
                if not step.enabled:
                    logger.info(f"Skipping disabled step: {step.name}")
                    continue
                
                logger.info(f"Executing step {i+1}/{len(self.steps)}: {step.name}")
                logger.info(f"Step description: {step.description}")
                logger.info(f"Expected input: {step.input_type} -> Expected output: {step.output_type}")
                
                try:
                    # Load and execute the step function
                    step_function = self._load_step_function(step.module_name, step.function_name)
                    result = step_function(current_data)
                    
                    # Update for next step
                    current_data = result
                    steps_executed.append(step.name)
                    step_results[step.name] = result
                    
                    # Save intermediate result if requested
                    if save_intermediate:
                        self._save_intermediate_result(step.name, result)
                    
                    logger.info(f"Step {step.name} completed successfully")
                    logger.debug(f"Step output: {result}")
                    
                except Exception as e:
                    error_msg = f"Error in step {step.name}: {str(e)}"
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    
                    end_time = datetime.now()
                    execution_time = (end_time - start_time).total_seconds()
                    
                    return WorkflowResult(
                        success=False,
                        data=None,
                        steps_executed=steps_executed,
                        execution_time=execution_time,
                        error_message=error_msg,
                        step_results=step_results
                    )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Save final result
            final_output_file = self.output_dir / f"workflow_result_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(final_output_file, 'w') as f:
                json.dump({
                    'success': True,
                    'final_data': current_data,
                    'steps_executed': steps_executed,
                    'execution_time': execution_time,
                    'timestamp': start_time.isoformat()
                }, f, indent=2, default=str)
            
            logger.info(f"Workflow completed successfully in {execution_time:.2f} seconds")
            logger.info(f"Final result saved to: {final_output_file}")
            
            return WorkflowResult(
                success=True,
                data=current_data,
                steps_executed=steps_executed,
                execution_time=execution_time,
                step_results=step_results
            )
            
        except Exception as e:
            error_msg = f"Unexpected workflow error: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return WorkflowResult(
                success=False,
                data=None,
                steps_executed=steps_executed,
                execution_time=execution_time,
                error_message=error_msg,
                step_results=step_results
            )
    
    def list_steps(self) -> None:
        """Print a summary of all registered steps"""
        logger.info(f"Registered workflow steps ({len(self.steps)} total):")
        for i, step in enumerate(self.steps):
            status = "✓ Enabled" if step.enabled else "✗ Disabled"
            logger.info(f"  {i+1}. {step.name} ({status})")
            logger.info(f"     {step.description}")
            logger.info(f"     Input: {step.input_type} → Output: {step.output_type}")
            logger.info("") 