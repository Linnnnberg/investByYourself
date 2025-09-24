#!/usr/bin/env python3
"""
Basic HTTP Server for InvestByYourself API
Tech-028: API Implementation

Simple HTTP server to test basic functionality.
"""

import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIHandler(BaseHTTPRequestHandler):
    """Basic API request handler."""

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/health":
            self.send_health_response()
        elif parsed_path.path == "/":
            self.send_root_response()
        else:
            self.send_not_found_response()

    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/api/v1/auth/register":
            self.send_auth_response("register")
        elif parsed_path.path == "/api/v1/auth/login":
            self.send_auth_response("login")
        else:
            self.send_not_found_response()

    def send_health_response(self):
        """Send health check response."""
        response = {
            "status": "healthy",
            "service": "InvestByYourself API",
            "version": "1.0.0",
            "environment": "development",
        }
        self.send_json_response(response, 200)

    def send_root_response(self):
        """Send root endpoint response."""
        response = {
            "message": "InvestByYourself API Gateway",
            "version": "1.0.0",
            "docs": "Not available in basic mode",
            "health": "/health",
        }
        self.send_json_response(response, 200)

    def send_auth_response(self, endpoint):
        """Send auth endpoint response."""
        response = {
            "message": f"{endpoint.title()} endpoint - not implemented yet",
            "status": "placeholder",
        }
        self.send_json_response(response, 200)

    def send_not_found_response(self):
        """Send 404 response."""
        response = {
            "error": "Not Found",
            "message": "The requested resource was not found",
        }
        self.send_json_response(response, 404)

    def send_json_response(self, data, status_code):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS"
        )
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode("utf-8"))

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS"
        )
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def log_message(self, format, *args):
        """Log HTTP requests."""
        logger.info(f"{self.address_string()} - {format % args}")


def run_server(host="localhost", port=8000):
    """Run the HTTP server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, APIHandler)

    logger.info(f"Starting InvestByYourself API Server on {host}:{port}")
    logger.info("Environment: development")
    logger.info("Basic HTTP server mode")
    logger.info("Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  GET  / - Root endpoint")
    logger.info("  POST /api/v1/auth/register - Registration (placeholder)")
    logger.info("  POST /api/v1/auth/login - Login (placeholder)")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    run_server()
