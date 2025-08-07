"""
json_sender.py

Provides a reusable mixin class `JsonSenderMixin` that simplifies sending
JSON responses and error messages in HTTP handlers based on `http.server`.

This mixin can be inherited by custom HTTP handler classes to standardize
JSON API responses and include proper logging for both client and server errors.
"""
import json
import logging

logger = logging.getLogger(__name__)

class JsonSenderMixin:
    """
    Mixin class for sending standardized JSON responses and errors.

    Designed to be used with subclasses of `BaseHTTPRequestHandler`. Handles
    setting proper headers, encoding JSON data, and logging the response.

    Methods:
        - send_json_error: Sends a JSON-formatted error response.
        - send_json_response: Sends a successful JSON response.
    """

    def send_json_error(self, status_code: int, message: str) -> None:
        """
        Sends an HTTP error response with a JSON body.

        Logs the error with appropriate severity level based on status code.

        Args:
            status_code (int): HTTP status code to return (e.g., 400, 500).
            message (str): Error message to include in the JSON response.
        """
        if status_code >= 500:
            logger.error(f"{self.command} {self.path} → {status_code}: {message}")
        else:
            logger.warning(f"{self.command} {self.path} → {status_code}: {message}")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {"detail": message}
        self.wfile.write(json.dumps(response).encode())

    def send_json_response(self, status_code: int, data: dict) -> None:
        """
        Sends a successful JSON response.

        Args:
            status_code (int): HTTP status code to return (typically 200 or 201).
            data (dict): Data to encode and send as the JSON response body.
        """
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())