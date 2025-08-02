# API to Pydantic 🚀

> Instantly convert API responses into production-ready Pydantic models

A Claude agent that automatically transforms JSON responses, API URLs, or curl commands into clean, type-safe Pydantic data models - eliminating manual model creation.

## ✨ What it does

Transform this messy API response:
```json
{
  "user_id": 123,
  "userName": "john_doe",
  "emailAddress": "john@example.com",
  "createdAt": "2023-01-01T00:00:00Z",
  "userProfile": {
    "biography": "Software developer",
    "followerCount": 42,
    "isVerified": true
  }
}
```

Into this beautiful Pydantic model:
```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserProfile(BaseModel):
    """User profile information"""
    biography: Optional[str] = None
    follower_count: int = Field(alias="followerCount")
    is_verified: bool = Field(alias="isVerified")

class UserResponse(BaseModel):
    """Auto-generated from API response"""
    user_id: int
    user_name: str = Field(alias="userName")
    email_address: EmailStr = Field(alias="emailAddress")
    created_at: datetime = Field(alias="createdAt")
    user_profile: UserProfile = Field(alias="userProfile")
```

## 🎯 Key Features

- **🔍 Smart Detection**: Automatically identifies input type (JSON, URL, curl, file)
- **🧠 Intelligent Typing**: Converts JSON types to proper Python types with validation
- **📧 Pattern Recognition**: Detects emails, URLs, timestamps, UUIDs automatically  
- **🔄 Field Mapping**: Handles camelCase ↔ snake_case conversion seamlessly
- **📚 Auto Documentation**: Generates docstrings and field descriptions
- **🎯 Optional Fields**: Smart detection of required vs optional fields
- **🏗️ Nested Models**: Creates clean class hierarchies for complex data

## 🚀 Quick Start

### Prerequisites
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed
- Python 3.8+ (for using generated models)

### Usage

1. **Activate the agent in Claude Code:**
   ```bash
   /api-to-pydantic
   ```

2. **Provide your input in any format:**

   **📋 Direct JSON:**
   ```json
   {"id": 1, "name": "John", "email": "john@example.com"}
   ```

   **🌐 API URL:**
   ```
   https://api.github.com/users/octocat
   ```

   **💻 curl command:**
   ```bash
   curl -H "Authorization: Bearer token" https://api.example.com/data
   ```

   **📁 JSON file (recommended for large/complex data):**
   ```
   file: response.json
   file: api_data.json
   file: /path/to/your_data.json
   ```

3. **Get instant Pydantic models** - ready to copy and use!

## 💡 Use Cases

- **🔌 API Integration**: Model third-party API responses quickly
- **✅ Data Validation**: Create type-safe models for incoming data  
- **📖 Documentation**: Generate model docs from API examples
- **🧪 Testing**: Create mock data structures for tests
- **🔄 Migration**: Convert JSON schemas to Pydantic v2

## 🛠️ Advanced Features

### Type Intelligence
Automatically detects and converts:
- `2023-01-01T00:00:00Z` → `datetime`
- `john@example.com` → `EmailStr` 
- `https://example.com` → `HttpUrl`
- `550e8400-e29b-41d4-a716-446655440000` → `UUID`

### Smart Field Analysis
- Analyzes data patterns to determine optional vs required fields
- Generates meaningful class names from JSON structure
- Handles complex nested objects and arrays
- Creates proper field aliases for API compatibility

### Developer Experience
- **One-command workflow** from JSON file to tested model
- **Copy-paste ready** output with validation
- **Production quality** code generation
- **Automatic testing** with executable test files
- **Zero configuration** required

## 📁 Project Structure

```
api_2_pydantic/
├── README.md                 # This file
├── CLAUDE.md                # Project instructions and overview
├── agents/                  # Claude agent definitions
│   ├── api-to-pydantic.md   # Main agent - handles routing and model generation
│   ├── schema-extract.md    # Schema extraction agent for large/complex data
│   └── models-tester.md     # Model testing agent (future feature)
├── api_to_pydantic_utils/   # Python utilities for schema processing
│   ├── __init__.py          # Module initialization
│   └── schema_extractor.py  # Core schema extraction logic
└── .gitignore               # Git ignore rules
```

## 🏗️ Architecture

The project uses a **multi-agent architecture** for optimal performance:

- **🎯 Main Agent** (`agents/api-to-pydantic`): Handles input detection, routing, and Pydantic model generation
- **⚡ Schema Extractor** (`agents/schema-extract`): Compresses large JSON data (80-95% reduction) for efficient processing
- **🧪 Model Tester** (`agents/models-tester`): Validates generated models against original data (coming soon)
- **🛠️ Utility Module** (`api_to_pydantic_utils`): Python utilities for file processing and schema extraction

This architecture enables handling everything from small JSON snippets to massive API responses efficiently.

## 🤝 Contributing

This is a Claude agent project. To improve or extend functionality:

1. Modify the agent instructions in `CLAUDE.md`
2. Test with various API responses
3. Submit issues for edge cases or improvements

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the [Claude Code](https://docs.anthropic.com/en/docs/claude-code) ecosystem
- Powered by [Pydantic](https://docs.pydantic.dev/) for data validation
- Inspired by developers who are tired of writing models manually

---

**Made with ❤️ for developers who value their time**

*Stop writing Pydantic models by hand. Let AI do the heavy lifting.*