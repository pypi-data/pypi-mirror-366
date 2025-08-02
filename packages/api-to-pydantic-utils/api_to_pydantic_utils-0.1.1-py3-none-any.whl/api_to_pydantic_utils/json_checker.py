"""JSON Validation Utility

Simple utility for validating JSON files without returning large data that might break terminals.
"""

import json
import os


def validate_json_file(file_path: str) -> bool:
    """Validate if a file contains valid JSON
    
    Args:
        file_path: The path to the JSON file to validate
        
    Returns:
        bool: True if file exists and contains valid JSON, False otherwise
        
    Note:
        If invalid, prints the error message to avoid returning large data
        that might break the terminal.
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
            
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            print(f"File is not readable: {file_path}")
            return False
            
        # Read and validate JSON content
        with open(file_path, 'r', encoding='utf-8') as f:
            json_content = f.read()
            
        json.loads(json_content)
        return True
        
    except json.JSONDecodeError as e:
        print(f"Invalid JSON format in {file_path}: {e}")
        return False
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return False
    except PermissionError:
        print(f"Permission denied reading file: {file_path}")
        return False
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False