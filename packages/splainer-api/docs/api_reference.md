# Splainer API Reference

## Base URL
`/v1`

## Authentication
API calls require the `X-API-Key` header if authentication is enabled.
```http
X-API-Key: your_api_key_here
```

## Endpoints

### `GET /health`
Returns API health status. No authentication required.

### `GET /v1/dialects`
Returns a list of supported SQL dialects.

### `POST /v1/translate`
Translate an SPL query to SQL.

**Request Body:**
```json
{
  "spl_query": "search index=main",
  "dialect": "postgres"
}
```

### `POST /v1/pipeline`
Translate and return full pipeline intermediate representations.

### `POST /v1/execute`
Translate and execute against the configured database, auto-fixing errors if encountered.

