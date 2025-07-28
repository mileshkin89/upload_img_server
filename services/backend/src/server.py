# server.py

import os
import uuid
import shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from multiprocessing import Process, current_process
from multipart import parse_form
from PIL import Image, UnidentifiedImageError

from db.dto import ImageDTO
from db.dependencies import get_image_repository
from exceptions import APIError, MaxSizeExceedError, MultipleFilesUploadError, NotSupportedFormatError
from json_sender import JsonSenderMixin
from file_handler import FileHandler
from settings.config import config
from settings.logging_config import get_logger


logger = get_logger(__name__)

os.makedirs(config.UPLOAD_DIR, exist_ok=True)


class UploadHandler(BaseHTTPRequestHandler, JsonSenderMixin):

    routes_get = {
        "/api/images/": "_handle_get_api_images",
        "/": "_handle_get_root",
    }

    routes_post = {
        "/api/upload/": "_handle_post_api_upload",
    }

    routes_delete = {
        "/api/images/": "_handle_delete_api_image",
    }


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
            self.send_json_error(404, "Not Found")
            return

        handler = getattr(self, handler_name, None)
        if not handler:
            self.send_json_error(500, "Handler not implemented.")
            return

        handler()


    def _handle_get_root(self):
        """Handles healthcheck at GET /."""
        logger.info("Healthcheck endpoint hit: /")
        self.send_json_response(200, {"message": "Welcome to the Upload Server"})


    def _handle_get_api_images(self):
        try:
            files = os.listdir(config.UPLOAD_DIR)
        except Exception as e:
            self.send_json_error(500, f"Error reading image directory: {e}")
            return

        images = []
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in config.SUPPORTED_FORMATS:
                images.append(f)

        self.send_json_response(200, images)



    def _handle_post_api_upload(self):

        f_handler = FileHandler()
        try:
            f_handler.parse_formdata(self.headers, self.rfile)
            f_handler.save_file(f_handler.file)
        except APIError as e:
            self.send_json_error(e.status_code, e.message)
            return
        except Exception as e:
            logger.exception("Unexpected error during file upload")
            self.send_json_error(500, f"Internal server error: {str(e)}")
            return

        url = f"/images/{f_handler.unique_name_ext}"

        self.send_json_response(200,{"filename": f"{f_handler.unique_name_ext}","url": f"{url}"})



    def _handle_delete_api_image(self):
        filename = ""
        filepath = self.path
        if filepath.startswith("/api/images/"):
            filename = filepath[len("/api/images/"):]
        elif filepath.startswith("/images/"):
            filename = filepath[len("/images/"):]

        if not filename:
            self.send_json_error(400, "Filename not provided.")
            return

        unique_name, ext = os.path.splitext(filename.lower())
        filepath = os.path.join(config.UPLOAD_DIR, filename)

        if ext not in config.SUPPORTED_FORMATS:
            self.send_json_error(400, "Unsupported file format.")
            return

        if not os.path.isfile(filepath):
            self.send_json_error(404, "File not found.")
            return


        # Delete from DB
        repository = get_image_repository()

        try:
            is_deleted = repository.delete_by_filename(unique_name)
            if not is_deleted:
                logger.warning(f"File '{unique_name}' was not found in database while deleting")
                return
        except Exception as e:
            self.send_json_error(500, "Error delete image from DB: " + str(e))
            return


        try:
            os.remove(filepath)
        except PermissionError:
            self.send_json_error(500, "Permission denied to delete file.")
            return
        except Exception as e:
            self.send_json_error(500, f"Internal Server Error: {str(e)}")
            return

        self.send_json_response(200, {"message": f"File '{filename}' deleted successfully."})



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