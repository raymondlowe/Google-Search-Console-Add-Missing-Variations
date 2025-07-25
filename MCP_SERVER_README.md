# MCP Server with Authorization Fallback

This repository contains an implementation of a Model Context Protocol (MCP) server with a robust authorization fallback mechanism. The server supports multiple methods for providing authorization keys, ensuring compatibility with various MCP client implementations.

## Features

- **Multiple Authorization Methods**: Supports both header-based and URL parameter-based authorization
- **Fallback Mechanism**: Automatically falls back to URL parameters when headers are not supported
- **Security Considerations**: Includes warnings and best practices for secure key transmission
- **Backwards Compatibility**: Works with existing authorization header implementations
- **Development Mode**: Can run without authorization for development and testing

## Authorization Methods

The server supports the following authorization methods in order of preference:

1. **Authorization Header (Recommended)**
   - `Authorization: Bearer <key>`
   - `Authorization: ApiKey <key>`
   - `Authorization: <key>` (direct key)

2. **URL Parameter Fallback**
   - `?key=<key>`
   - `?auth=<key>`

## Security Considerations

### Headers vs URL Parameters

- **Headers (Recommended)**: More secure as they are not logged in server access logs or browser history
- **URL Parameters (Fallback)**: Less secure but necessary when MCP clients cannot send headers properly

### Best Practices

1. **Always use HTTPS** when transmitting authorization keys via URL parameters
2. **Use short-lived tokens** when possible
3. **Rotate keys regularly**
4. **Monitor access logs** for unauthorized attempts
5. **Use headers when client supports them**

## Usage

### Starting the Server

```bash
# Start with specific authorized keys
python3 mcp_server.py --keys your-api-key-1 your-api-key-2

# Start on custom port
python3 mcp_server.py --port 9000 --keys your-api-key

# Development mode (no authorization required)
python3 mcp_server.py

# Verbose logging
python3 mcp_server.py --verbose --keys your-api-key
```

### Command Line Options

- `--port, -p`: Port to run the server on (default: 8000)
- `--host`: Host to bind to (default: localhost)
- `--keys, -k`: Authorized API keys (space-separated)
- `--verbose, -v`: Enable verbose logging
- `--help, -h`: Show help message

### Client Examples

#### Using Authorization Header (Recommended)

```bash
# Bearer token
curl -H "Authorization: Bearer your-api-key" http://localhost:8000/health

# API Key format
curl -H "Authorization: ApiKey your-api-key" http://localhost:8000/health
```

#### Using URL Parameters (Fallback)

```bash
# Using 'key' parameter
curl http://localhost:8000/health?key=your-api-key

# Using 'auth' parameter
curl http://localhost:8000/health?auth=your-api-key
```

#### Tool Execution

```bash
# Execute tool with header authorization
curl -X POST \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"tool": "echo", "parameters": {"message": "Hello World"}}' \
  http://localhost:8000/execute

# Execute tool with URL parameter authorization
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"tool": "echo", "parameters": {"message": "Hello World"}}' \
  http://localhost:8000/execute?key=your-api-key
```

## API Endpoints

### GET /
Server information and available authorization methods.

### GET /health
Health check endpoint. Returns server status.

### GET /tools
List of available tools.

### GET /auth-test
Test authorization and see which method was used.

### POST /execute
Execute a tool with the provided parameters.

## Available Tools

### echo
Echo back a provided message.
```json
{
  "tool": "echo",
  "parameters": {
    "message": "Your message here"
  }
}
```

### auth_info
Get information about the authorization method used.
```json
{
  "tool": "auth_info",
  "parameters": {}
}
```

## Error Responses

The server returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid JSON, unknown tool, etc.)
- `401`: Unauthorized (missing or invalid key)
- `404`: Not Found (invalid endpoint)
- `500`: Internal Server Error

## Development and Testing

### Running Tests

```bash
# Test authorization mechanisms
python3 /tmp/test_mcp_auth.py

# Test no-authorization mode
python3 /tmp/test_no_auth.py
```

### Development Mode

For development, you can run the server without any authorization keys:

```bash
python3 mcp_server.py
```

This allows all requests and is useful for testing client implementations.

## Implementation Details

The authorization fallback mechanism works as follows:

1. **Check Authorization Header**: First attempts to extract the key from standard authorization headers
2. **Parse URL Parameters**: If no header is found, parses the URL query parameters
3. **Validate Key**: Compares the extracted key against configured authorized keys
4. **Log Security Warnings**: Warns when URL parameters are used for key transmission

## Backwards Compatibility

The server is fully backwards compatible with existing MCP clients that use authorization headers. The URL parameter fallback is only used when headers are not provided.

## Contributing

When contributing to this project:

1. Ensure all security considerations are addressed
2. Add tests for new authorization methods
3. Update documentation for any new features
4. Follow the existing code style and patterns