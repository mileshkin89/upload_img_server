# server.py

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

from settings.config import config
from settings.logging_config import get_logger

logger = get_logger(__name__)

os.makedirs(config.UPLOAD_DIR, exist_ok=True)


class UploadHandler(BaseHTTPRequestHandler):

    routes_get = {
        "/": "_handle_get_root",
    }

    routes_post = {
        "/": "_handle_post_upload",
    }

    routes_delete = {
        "/": "_handle_del_api_images",
    }

    def _send_json_error(self, status_code: int, message: str) -> None:
        if status_code >= 500:
            logger.error(f"{self.command} {self.path} → {status_code}: {message}")
        else:
            logger.warning(f"{self.command} {self.path} → {status_code}: {message}")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {"detail": message}
        self.wfile.write(json.dumps(response).encode())


    def do_GET(self):
        """Handles GET requests and dispatches them based on route."""
        self._handle_request(self.routes_get)

    def do_POST(self):
        """Handles POST requests and dispatches them based on route."""
        self._handle_request(self.routes_post)

    def do_DELETE(self):
        """Handles DELETE requests and dispatches them based on route."""
        self._handle_request(self.routes_delete)


    def _handle_request(self, routes: dict[str, str]) -> None:
        handler_name = routes.get(self.path)
        if not handler_name:
            for route_prefix, candidate_handler in routes.items():
                if self.path.startswith(route_prefix):
                    handler_name = candidate_handler
                    break

        if not handler_name:
            self._send_json_error(404, "Not Found")
            return

        handler = getattr(self, handler_name, None)
        if not handler:
            self._send_json_error(500, "Handler not implemented.")
            return

        handler()


    def _handle_get_root(self):
        """Handles healthcheck at GET /."""
        logger.info("Healthcheck endpoint hit: /")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write("{{'message': 'Welcome to the Upload Server'}}".encode()) #b"{'message': 'Welcome to the Upload Server'}"




if __name__ == "__main__":
    try:
        server = HTTPServer(("localhost", 8000), UploadHandler)
        logger.info("Upload server running on http://localhost:8000")
        server.serve_forever()
    except Exception:
        server.shutdown()