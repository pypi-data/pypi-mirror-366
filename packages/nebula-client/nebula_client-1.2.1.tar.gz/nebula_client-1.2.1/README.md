# Nebula Client SDK

Official Python SDK for the Nebula Cloud API.

## Installation

```bash
pip install nebula-client
```

## Quick Start

### Synchronous Client

```python
from nebula_client import NebulaClient

# Initialize with API key
client = NebulaClient(api_key="your-api-key")

# Make API calls
response = client.get("collections")
print(response)
```

### Asynchronous Client

```python
import asyncio
from nebula_client import NebulaAsyncClient

async def main():
    # Initialize with API key
    async with NebulaAsyncClient(api_key="your-api-key") as client:
        # Make API calls
        response = await client.get("collections")
        print(response)

asyncio.run(main())
```

## Configuration

The SDK can be configured using:

1. **Constructor parameters**: Pass `api_key` and `base_url` directly
2. **Environment variables**:
   - `NEBULA_API_KEY`: Your API key
   - `NEBULA_API_BASE`: Base URL (defaults to `https://api.nebulacloud.app`)

## Basic Usage

The SDK provides simple HTTP client functionality for making API calls:

```python
from nebula_client import NebulaClient

client = NebulaClient(api_key="your-api-key")

# GET request
collections = client.get("collections")

# POST request
new_collection = client.post("collections", json={"name": "my-collection"})

# PUT request
updated = client.put("collections/123", json={"name": "updated-name"})

# DELETE request
deleted = client.delete("collections/123")
```

## Error Handling

The SDK provides custom exceptions:

```python
from nebula_client import NebulaClientException, NebulaException

try:
    result = client.get("collections")`
except NebulaClientException as e:
    print(f"Client error: {e.message}")
except NebulaException as e:
    print(f"API error: {e.message} (Status: {e.status_code})")
```

## API Endpoints

The SDK supports all Nebula API endpoints. Refer to the [Nebula API documentation](https://api.nebulacloud.app/docs) for available endpoints and their usage.

## License

This SDK is proprietary software. All rights reserved.
