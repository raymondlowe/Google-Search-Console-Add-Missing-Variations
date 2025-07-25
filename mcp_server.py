#!/usr/bin/env python3
"""
MCP Server with Authorization Fallback Mechanism

This server implements the Model Context Protocol (MCP) with support for
authorization keys through multiple mechanisms:
1. Authorization header (primary method)
2. URL parameter fallback (when headers are not supported)

Security considerations:
- URL parameters are logged in server logs and browser history
- HTTPS should be used when transmitting keys via URL parameters
- Consider using short-lived tokens when possible
"""

import json
import logging
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Dict, Any
import argparse
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPServerHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP server with authorization fallback."""
    
    def __init__(self, *args, authorized_keys=None, **kwargs):
        self.authorized_keys = authorized_keys or set()
        super().__init__(*args, **kwargs)
    
    def extract_authorization_key(self) -> Optional[str]:
        """
        Extract authorization key using fallback mechanism:
        1. Try Authorization header first (Bearer token or API key)
        2. Fall back to URL parameter 'key' if header is missing
        3. Try URL parameter 'auth' as secondary fallback
        
        Returns:
            str: The authorization key if found, None otherwise
        """
        # Method 1: Check Authorization header (primary method)
        auth_header = self.headers.get('Authorization')
        if auth_header:
            # Support both "Bearer <token>" and "ApiKey <key>" formats
            if auth_header.startswith('Bearer '):
                key = auth_header[7:]  # Remove "Bearer " prefix
                logger.debug("Authorization key found in Bearer header")
                return key
            elif auth_header.startswith('ApiKey '):
                key = auth_header[7:]  # Remove "ApiKey " prefix
                logger.debug("Authorization key found in ApiKey header")
                return key
            else:
                # Direct key in header
                logger.debug("Authorization key found in header (direct)")
                return auth_header
        
        # Method 2: Check URL parameters as fallback
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Try 'key' parameter first
        if 'key' in query_params and query_params['key']:
            key = query_params['key'][0]  # Get first value
            logger.warning("Authorization key found in URL parameter 'key' - consider using headers for better security")
            return key
        
        # Try 'auth' parameter as secondary fallback
        if 'auth' in query_params and query_params['auth']:
            key = query_params['auth'][0]  # Get first value
            logger.warning("Authorization key found in URL parameter 'auth' - consider using headers for better security")
            return key
        
        logger.debug("No authorization key found in headers or URL parameters")
        return None
    
    def is_authorized(self) -> bool:
        """
        Check if the request is authorized using the fallback mechanism.
        
        Returns:
            bool: True if authorized, False otherwise
        """
        if not self.authorized_keys:
            # If no keys are configured, allow all requests (development mode)
            logger.warning("No authorization keys configured - allowing all requests")
            return True
        
        auth_key = self.extract_authorization_key()
        if not auth_key:
            logger.info("Request denied: No authorization key provided")
            return False
        
        if auth_key in self.authorized_keys:
            logger.debug("Request authorized successfully")
            return True
        
        logger.info("Request denied: Invalid authorization key")
        return False
    
    def send_json_response(self, data: Dict[Any, Any], status_code: int = 200):
        """Send a JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def send_error_response(self, message: str, status_code: int = 400):
        """Send an error response."""
        error_data = {
            "error": message,
            "status": status_code
        }
        self.send_json_response(error_data, status_code)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        if not self.is_authorized():
            self.send_error_response("Unauthorized: Invalid or missing authorization key", 401)
            return
        
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        if path == '/':
            # Root endpoint - server info
            response = {
                "name": "MCP Server with Authorization Fallback",
                "version": "1.0.0",
                "description": "Model Context Protocol server with header and URL parameter authorization fallback",
                "authorization_methods": [
                    "Authorization header (Bearer <token>)",
                    "Authorization header (ApiKey <key>)",
                    "URL parameter (?key=<key>)",
                    "URL parameter (?auth=<key>)"
                ],
                "endpoints": {
                    "/": "Server information",
                    "/health": "Health check",
                    "/tools": "Available tools",
                    "/auth-test": "Test authorization"
                }
            }
            self.send_json_response(response)
        
        elif path == '/health':
            # Health check endpoint
            response = {
                "status": "healthy",
                "timestamp": self.date_time_string(),
                "authorized": True
            }
            self.send_json_response(response)
        
        elif path == '/tools':
            # Available tools endpoint
            response = {
                "tools": [
                    {
                        "name": "echo",
                        "description": "Echo back the provided message",
                        "parameters": {
                            "message": {"type": "string", "required": True}
                        }
                    },
                    {
                        "name": "auth_info",
                        "description": "Show information about the authorization method used",
                        "parameters": {}
                    }
                ]
            }
            self.send_json_response(response)
        
        elif path == '/auth-test':
            # Test authorization endpoint
            auth_key = self.extract_authorization_key()
            auth_method = "none"
            
            if self.headers.get('Authorization'):
                auth_method = "header"
            elif 'key=' in self.path:
                auth_method = "url_parameter_key"
            elif 'auth=' in self.path:
                auth_method = "url_parameter_auth"
            
            response = {
                "authorized": True,
                "method_used": auth_method,
                "key_present": auth_key is not None,
                "key_valid": auth_key in self.authorized_keys if self.authorized_keys else True
            }
            self.send_json_response(response)
        
        else:
            self.send_error_response("Not Found", 404)
    
    def do_POST(self):
        """Handle POST requests."""
        if not self.is_authorized():
            self.send_error_response("Unauthorized: Invalid or missing authorization key", 401)
            return
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_error_response("Invalid JSON in request body", 400)
                return
            
            # Handle MCP tool execution
            parsed_url = urllib.parse.urlparse(self.path)
            path = parsed_url.path
            
            if path == '/execute':
                self.handle_tool_execution(data)
            else:
                self.send_error_response("Endpoint not found", 404)
                
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self.send_error_response("Internal server error", 500)
    
    def handle_tool_execution(self, data: Dict[Any, Any]):
        """Handle tool execution requests."""
        tool_name = data.get('tool')
        parameters = data.get('parameters', {})
        
        if tool_name == 'echo':
            message = parameters.get('message', 'No message provided')
            response = {
                "tool": "echo",
                "result": {
                    "echoed_message": message,
                    "timestamp": self.date_time_string()
                }
            }
            self.send_json_response(response)
        
        elif tool_name == 'auth_info':
            auth_key = self.extract_authorization_key()
            auth_method = "none"
            
            if self.headers.get('Authorization'):
                auth_method = "header"
            elif 'key=' in self.path:
                auth_method = "url_parameter_key"
            elif 'auth=' in self.path:
                auth_method = "url_parameter_auth"
            
            response = {
                "tool": "auth_info",
                "result": {
                    "authorization_method": auth_method,
                    "key_present": auth_key is not None,
                    "key_valid": auth_key in self.authorized_keys if self.authorized_keys else True,
                    "timestamp": self.date_time_string()
                }
            }
            self.send_json_response(response)
        
        else:
            self.send_error_response(f"Unknown tool: {tool_name}", 400)
    
    def log_message(self, format, *args):
        """Override to use our logger instead of stderr."""
        logger.info(f"{self.address_string()} - {format % args}")


def create_handler_class(authorized_keys):
    """Create a handler class with the authorized keys."""
    class Handler(MCPServerHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, authorized_keys=authorized_keys, **kwargs)
    return Handler


def main():
    """Main function to start the MCP server."""
    parser = argparse.ArgumentParser(
        description="MCP Server with Authorization Fallback Mechanism"
    )
    parser.add_argument(
        '--port', '-p', type=int, default=8000,
        help="Port to run the server on (default: 8000)"
    )
    parser.add_argument(
        '--host', default='localhost',
        help="Host to bind the server to (default: localhost)"
    )
    parser.add_argument(
        '--keys', '-k', nargs='*', default=[],
        help="Authorized API keys (space-separated). If none provided, all requests are allowed."
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set up authorized keys
    authorized_keys = set(args.keys) if args.keys else set()
    
    if authorized_keys:
        logger.info(f"Server configured with {len(authorized_keys)} authorized key(s)")
    else:
        logger.warning("No authorized keys configured - all requests will be allowed")
    
    # Create handler class with authorized keys
    handler_class = create_handler_class(authorized_keys)
    
    # Start server
    try:
        server = HTTPServer((args.host, args.port), handler_class)
        logger.info(f"MCP Server starting on {args.host}:{args.port}")
        logger.info("Authorization methods supported:")
        logger.info("  1. Authorization header: 'Authorization: Bearer <key>' or 'Authorization: ApiKey <key>'")
        logger.info("  2. URL parameter fallback: '?key=<key>' or '?auth=<key>'")
        logger.info("  Note: URL parameters are less secure and should only be used when headers are not supported")
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()