
import json
import logging

logger = logging.getLogger(__name__)

class JsonSenderMixin:

    def send_json_error(self, status_code: int, message: str) -> None:
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
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())