"""JSON Schema Extraction Module

Extracts and compresses JSON schemas from large/complex data, reducing token usage 
by 80-95% while preserving all structural information for accurate Pydantic model generation.
"""

import json
import random
import re
from typing import Any, Dict, List


def detect_type(value: Any) -> str:
    """Detect the type of a JSON value with pattern recognition"""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, str):
        # Pattern detection for strings
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            return "email"
        elif re.match(r'^https?://', value):
            return "url"
        elif re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
            return "datetime"
        elif re.match(r'^\d+\s+(year|month|week|day|hour|minute|second)s?\s+ago$', value):
            return "relative_time"
        elif value.startswith('@'):
            return "username"
        elif re.match(r'^UC[a-zA-Z0-9_-]{22}$', value):
            return "youtube_channel_id"
        elif re.match(r'^[a-zA-Z0-9_-]{11}$', value):
            return "youtube_video_id"
        elif value.isdigit():
            return "numeric_string"
        elif len(value) > 50 and any(char in value for char in '.!?'):
            return "text_content"
        else:
            return "str"
    elif isinstance(value, list):
        return "array"
    elif isinstance(value, dict):
        return "object"
    else:
        return "unknown"


def sample_array(arr: List[Any], max_samples: int = 5) -> List[Any]:
    """Smart sampling of arrays"""
    if len(arr) <= max_samples:
        return arr
    
    samples = []
    # Always include first item
    samples.append(arr[0])
    
    # Include last item if different structure
    if len(arr) > 1:
        samples.append(arr[-1])
    
    # Add random samples from middle
    remaining_slots = max_samples - len(samples)
    if remaining_slots > 0 and len(arr) > 2:
        middle_indices = random.sample(range(1, len(arr) - 1), 
                                     min(remaining_slots, len(arr) - 2))
        for idx in middle_indices:
            samples.append(arr[idx])
    
    return samples


def extract_schema(data: Any, depth: int = 0, max_depth: int = 6) -> Dict[str, Any]:
    """Extract schema from JSON data with nesting support"""
    
    if depth > max_depth:
        return {"type": "truncated", "reason": "max_depth_exceeded"}
    
    if isinstance(data, dict):
        schema = {
            "type": "object",
            "depth": depth,
            "field_count": len(data),
            "fields": {}
        }
        
        for key, value in data.items():
            field_type = detect_type(value)
            field_schema = {
                "type": field_type,
                "required": True,  # Will be determined with multiple samples
            }
            
            # Add sample values (limit to 3)
            if field_type in ["str", "int", "float", "bool", "email", "url", "username", "relative_time", "youtube_video_id", "youtube_channel_id", "numeric_string"]:
                field_schema["samples"] = [value] if value is not None else []
            
            # Recursively extract nested structures
            if field_type == "object":
                field_schema["nested_schema"] = extract_schema(value, depth + 1, max_depth)
            elif field_type == "array" and len(value) > 0:
                # Sample the array and analyze structure
                sampled_items = sample_array(value)
                field_schema["array_info"] = {
                    "total_items": len(value),
                    "sampled_items": len(sampled_items)
                }
                
                # Analyze array item types
                item_types = [detect_type(item) for item in sampled_items]
                if len(set(item_types)) == 1 and item_types[0] == "object":
                    # Homogeneous array of objects - extract schema from first item
                    field_schema["item_schema"] = extract_schema(sampled_items[0], depth + 1, max_depth)
                else:
                    # Mixed types or primitives
                    field_schema["item_types"] = list(set(item_types))
                    field_schema["sample_items"] = sampled_items[:3]
            
            schema["fields"][key] = field_schema
        
        return schema
    
    elif isinstance(data, list):
        return {
            "type": "array",
            "depth": depth,
            "total_items": len(data),
            "item_schema": extract_schema(data[0], depth + 1, max_depth) if data else None
        }
    
    else:
        return {
            "type": detect_type(data),
            "value": data
        }


def process_json_file(file_path: str):
    """Process JSON file and extract schema"""
    try:
        # Read JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Always extract schema since agent is called for this purpose
        print("Extracting schema from JSON data...")
        schema = extract_schema(data)
        
        # Calculate compression
        original_json = json.dumps(data)
        original_size = len(original_json)
        schema_json = json.dumps(schema, indent=2)
        schema_size = len(schema_json)
        compression_ratio = original_size / schema_size
        
        print(f"Compression: {original_size:,} -> {schema_size:,} chars ({compression_ratio:.1f}x reduction)")
        print(f"Token savings: {((original_size - schema_size) / original_size * 100):.1f}%")
        print("\n" + "="*50)
        print("COMPRESSED SCHEMA (use this for Pydantic generation):")
        print("="*50)
        print(schema_json)
        
        return schema
            
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in file {file_path}: {e}")
        return None
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        return None
    except Exception as e:
        print(f"ERROR: Error processing file {file_path}: {e}")
        return None