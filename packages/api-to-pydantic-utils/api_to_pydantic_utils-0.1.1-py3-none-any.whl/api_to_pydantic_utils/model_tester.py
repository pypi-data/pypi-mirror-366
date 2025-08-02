"""
Simplified model testing utility for validating generated Pydantic models.

This module provides a single function for creating executable test files.
"""

import json
import re
import os
from typing import Optional


def create_test_file(model_file_path: str, json_file_path: str) -> str:
    """
    Create a Python test file for validating a Pydantic model against a JSON file.
    
    Args:
        model_file_path: Path to the Python file containing the Pydantic model code
        json_file_path: Path to the JSON file to test against
        
    Returns:
        str: File path of the created test file
    """
    # Read model code from file
    with open(model_file_path, 'r', encoding='utf-8') as f:
        model_code = f.read()
    
    # Extract model class name automatically
    model_class_name = _extract_model_class_name(model_code)
    if not model_class_name:
        raise ValueError("Could not extract model class name from provided code")
    
    # Generate test file content
    test_content = f'''# Auto-generated model validation test
import json
from pydantic import ValidationError

{model_code}

# Load test data from JSON file
with open(r"{json_file_path}", 'r') as f:
    test_data = json.load(f)

# Test with original data - works with both Pydantic v1 and v2
try:
    # Try Pydantic v2 first, fallback to v1
    try:
        instance = {model_class_name}.model_validate(test_data)  # Pydantic v2
        print("Using Pydantic v2")
    except AttributeError:
        instance = {model_class_name}.parse_obj(test_data)  # Pydantic v1
        print("Using Pydantic v1")
    
    print(f"Success: Model parsed correctly - {{instance}}")
    print("RESULT: PASS")
    
except Exception as e:
    print(f"Error: {{str(e)}}")
    print("RESULT: FAIL")
'''
    
    # Create test file
    test_file_path = os.path.join(os.getcwd(), "test_model_validation.py")
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    return test_file_path


def _extract_model_class_name(model_code: str) -> Optional[str]:
    """Extract the main model class name from Pydantic model code (internal helper)"""
    pattern = r'class\s+(\w+)\s*\([^)]*BaseModel[^)]*\):'
    match = re.search(pattern, model_code)
    return match.group(1) if match else None