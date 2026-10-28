# Splainer API

REST API for translating Splunk SPL queries into SQL.

## Installation

```bash
uv pip install splainer-api
```

## Running the API

Start the API server:

```bash
splainer-api
# or
uv run splainer-api
```

The API will be available at `http://localhost:8080`.

## Documentation

Interactive documentation is available when the server is running:

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

See `docs/api_reference.md` for a static reference.

