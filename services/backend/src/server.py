# server.py

import os
import json
import uuid
import shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from multiprocessing import Process, current_process
from multipart import parse_form
from PIL import Image, UnidentifiedImageError
from exceptions import APIError, MaxSizeExceedError, MultipleFilesUploadError, NotSupportedFormatError

from settings.config import config
from settings.logging_config import get_logger


logger = get_logger(__name__)

os.makedirs(config.UPLOAD_DIR, exist_ok=True)


class UploadHandler(BaseHTTPRequestHandler):

    routes_get = {
        "/": "_handle_get_root",
    }

    routes_post = {
        "/api/upload/": "_handle_post_upload",
    }

    routes_delete = {
        "/": "_handle_del",
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
        self.wfile.write(json.dumps({"message": "Welcome to the Upload Server"}).encode())



    def _handle_post_upload(self):

        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self._send_json_error(400, "Bad Request: Expected multipart/form-data")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        headers = {
            "Content-Type": content_type,
            "Content-Length": str(content_length)
        }

        files = []

        def on_file(file):
            if len(files) >= 1:
                raise MultipleFilesUploadError()
            files.append(file)

        try:
            parse_form(headers, self.rfile, lambda _: None, on_file)  # type: ignore[arg-type]
        except APIError as e:
            self._send_json_error(e.status_code, e.message)
            return

        file = files[0]

        filename = file.file_name.decode("utf-8") if file.file_name else "uploaded_file"
        ext = os.path.splitext(filename)[1].lower()

        if ext not in config.SUPPORTED_FORMATS:
            raise NotSupportedFormatError(config.SUPPORTED_FORMATS)

        file.file_object.seek(0, os.SEEK_END)
        size = file.file_object.tell()
        file.file_object.seek(0)

        if size > config.MAX_FILE_SIZE:
            raise MaxSizeExceedError(config.MAX_FILE_SIZE)

        try:
            image = Image.open(file.file_object)
            image.verify()
            file.file_object.seek(0)
        except (UnidentifiedImageError, OSError):
            raise NotSupportedFormatError(config.SUPPORTED_FORMATS)

        original_name = os.path.splitext(filename)[0].lower()
        unique_name = f"{original_name}_{uuid.uuid4()}{ext}"

        os.makedirs(config.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(config.UPLOAD_DIR, unique_name)

        with open(file_path, "wb") as f:
            file.file_object.seek(0)
            shutil.copyfileobj(file.file_object, f)

        url = f"/images/{unique_name}"

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            f'{{"filename": "{unique_name}", '
            f'"url": "{url}"}}'.encode()
        )




def run_server_on_port(port: int):
    current_process().name = f"worker-{port}"
    logger.info(f"Starting server on http://0.0.0.0:{port}")
    server = HTTPServer(("0.0.0.0", port), UploadHandler)
    server.serve_forever()


def run(workers: int = 1, start_port: int = 8000):
    for i in range(workers):
        port = start_port + i
        p = Process(target=run_server_on_port, args=(port,))
        p.start()
        logger.info(f"Worker {i + 1} started on port {port}")


if __name__ == '__main__':
    run(workers=config.WEB_SERVER_WORKERS, start_port=config.WEB_SERVER_START_PORT)