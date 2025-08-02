# API to Pydantic Utils

> Core utilities for JSON schema extraction and Pydantic model generation

A Python package that provides utilities for processing JSON data and extracting schemas for Pydantic model generation. Originally developed as part of the [API to Pydantic](https://github.com/luc-pimentel/api-to-pydantic) project.

## Installation

```bash
pip install api-to-pydantic-utils
```

## Features

- **Schema Extraction**: Intelligent JSON schema extraction with 80-95% compression
- **Type Detection**: Automatic detection of emails, URLs, timestamps, and other patterns
- **Model Testing**: Utilities for validating Pydantic models against JSON data
- **JSON Validation**: Simple JSON file validation utilities

## Quick Start

```python
from api_to_pydantic_utils import extract_schema, validate_json_file, create_test_file

# Extract schema from JSON data
schema = extract_schema({"name": "John", "email": "john@example.com"})
print(schema)

# Validate a JSON file
is_valid = validate_json_file("data.json")

# Create test file for a Pydantic model
test_file = create_test_file("model.py", "test_data.json")
```

## API Reference

### `extract_schema(data, max_depth=10)`
Extracts a compressed schema from JSON data.

**Parameters:**
- `data`: JSON data (dict, list, or primitive)
- `max_depth`: Maximum nesting depth to process

**Returns:** Compressed schema representation

### `process_json_file(file_path, max_depth=10)`
Processes a JSON file and extracts its schema.

**Parameters:**
- `file_path`: Path to JSON file
- `max_depth`: Maximum nesting depth to process

**Returns:** Tuple of (schema, compression_stats)

### `validate_json_file(file_path)`
Validates if a file contains valid JSON.

**Parameters:**
- `file_path`: Path to JSON file

**Returns:** Boolean indicating if file is valid JSON

### `create_test_file(model_file_path, json_file_path)`
Creates a test file for validating Pydantic models.

**Parameters:**
- `model_file_path`: Path to Python file with Pydantic model
- `json_file_path`: Path to JSON file to test against

**Returns:** Path to created test file

## Type Detection

The package automatically detects various data patterns:

- **Email addresses**: `john@example.com` → `EmailStr`
- **URLs**: `https://example.com` → `HttpUrl`
- **Timestamps**: `2023-01-01T00:00:00Z` → `datetime`
- **YouTube IDs**: Channel and video ID patterns
- **Usernames**: `@username` patterns
- **Text content**: Long text with punctuation

## Requirements

- Python 3.8+
- Pydantic 2.0+

## License

MIT License

## Contributing

This package is part of the [API to Pydantic](https://github.com/luc-pimentel/api-to-pydantic) project. Please report issues and contribute there.