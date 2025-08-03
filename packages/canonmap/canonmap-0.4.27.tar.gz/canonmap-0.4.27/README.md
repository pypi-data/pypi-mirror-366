# CanonMap

A powerful data matching and canonicalization library with MySQL connector support.

## Features

- **Data Matching**: Advanced algorithms for fuzzy string matching and record linkage
- **MySQL Integration**: Seamless connection and management of MySQL databases
- **Canonicalization**: Standardize and normalize data across different formats
- **Rich Logging**: Beautiful console output with structured logging
- **FastAPI Support**: Optional FastAPI integration for web services

## Installation

```bash
pip install canonmap
```

For development dependencies:
```bash
pip install canonmap[dev]
```

For FastAPI support:
```bash
pip install canonmap[fastapi]
```

## Quick Start

### Command Line Interface

CanonMap provides a CLI tool for quick project setup:

```bash
# Create a new API project (default name: app)
cm create-api

# Create a new API project with custom name
cm create-api --name my-api

# Create a new API project with spaces (will be normalized)
cm create-api --name "My API"
```

The CLI will automatically:
- Normalize directory names to follow Python conventions
- Auto-increment names if the directory already exists (app, app-2, app-3, etc.)
- Copy and customize the example API template
- Replace all references from "app" to your chosen name
- Install required dependencies (fastapi, uvicorn, python-dotenv)

### Basic Usage

```python
from canonmap import make_console_handler
from canonmap.connectors.mysql_connector import MySQLConnector

# Set up logging
make_console_handler(set_root=True)

# Create a MySQL connector
connector = MySQLConnector(
    host="localhost",
    port=3306,
    user="your_user",
    password="your_password",
    database="your_database"
)

# Use the connector for data operations
# ... your data matching and canonicalization code
```

### Data Matching Example

```python
from canonmap.connectors.mysql_connector.matching import Matcher

# Initialize matcher
matcher = Matcher()

# Perform fuzzy matching
matches = matcher.find_matches(
    source_data=source_records,
    target_data=target_records,
    fields_to_match=["name", "address"],
    threshold=0.8
)
```

### Table Management with Primary Key Support

CanonMap supports creating tables from data with intelligent primary key handling:

```python
import pandas as pd
from canonmap.connectors.mysql_connector import MySQLConnector, TableManager
from canonmap.connectors.mysql_connector.managers.table_manager.validators.requests import CreateTableRequest
from canonmap.connectors.mysql_connector.managers.database_manager.validators.models import Database
from canonmap.connectors.mysql_connector.validators.models import IfExists

# Create connector and table manager
connector = MySQLConnector(config)
table_manager = TableManager(connector)

# Example 1: Create table with user-specified primary key (if valid)
data = pd.DataFrame({
    'user_id': [1001, 1002, 1003, 1004, 1005],  # Unique values
    'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'email': ['alice@test.com', 'bob@test.com', 'charlie@test.com', 'david@test.com', 'eve@test.com']
})

request = CreateTableRequest(
    database=Database(name="my_database"),
    name="users",
    data=data,
    primary_key_field="user_id",  # Will be validated for uniqueness
    if_exists=IfExists.REPLACE
)

result = table_manager.create_table(request)
# Result: Table created with 'user_id' as PRIMARY KEY
```

**Primary Key Validation Features:**

- **Automatic Validation**: The system validates that the specified field is unique and contains no null values
- **Smart Fallback**: If validation fails, automatically falls back to auto-increment `id` column
- **Logging**: Clear log messages inform you about validation results and fallback decisions
- **Multiple Data Sources**: Works with DataFrames, CSV files, lists of dictionaries, and more

**Validation Rules:**
- Field must exist in the data
- Field must contain no null/empty values
- Field must have unique values across all rows
- If any rule is violated, falls back to auto-increment `id` PRIMARY KEY

## Documentation

For detailed documentation, visit [the project homepage](https://github.com/yourusername/canonmap).

## Development

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/canonmap.git
cd canonmap
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

3. Run tests:
```bash
pytest
```

### Code Quality

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing

Run all quality checks:
```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/canonmap/issues)
- **Documentation**: [Project README](https://github.com/yourusername/canonmap#readme) 