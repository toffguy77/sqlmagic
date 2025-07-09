# SQLMagic - PostgreSQL Analytics MCP Server

Production-ready MCP server for PostgreSQL database analytics without SQL knowledge.

## Features

- **Secure**: Input validation, SQL injection protection
- **Scalable**: Connection pooling, configurable limits
- **Observable**: Structured logging, error handling
- **Testable**: Unit tests, modular architecture

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Set environment variables
export LOG_LEVEL=INFO
export MAX_CONNECTIONS=10

# Run server
sqlmagic
```

## Configuration

Environment variables:
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `MAX_CONNECTIONS`: Maximum database connections
- `QUERY_TIMEOUT`: Query timeout in seconds
- `MAX_ROWS_LIMIT`: Maximum rows returned

## Docker

```bash
docker build -t sqlmagic .
docker run -p 8000:8000 sqlmagic
```

## Tools

- `connect_database`: Connect to PostgreSQL
- `explore_tables`: List database tables
- `describe_table`: Show table structure
- `sample_data`: Get sample data
- `analyze_data`: Basic statistics
- `find_correlations`: Find correlations
- `detect_anomalies`: Detect anomalies
- `time_series_analysis`: Time series analysis

## Testing

```bash
pytest tests/
```