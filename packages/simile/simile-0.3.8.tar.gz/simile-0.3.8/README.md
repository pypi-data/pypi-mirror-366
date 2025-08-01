# Simile API Python Client

A Python client for interacting with the Simile API server.

## Installation

```bash
pip install simile
```

## Dependencies

- `httpx>=0.20.0`
- `pydantic>=2.0.0`

## Usage

```python
from simile import Simile

client = Simile(api_key="your_api_key")
```