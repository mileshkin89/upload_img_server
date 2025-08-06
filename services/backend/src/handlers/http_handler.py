# server.py

from http.server import BaseHTTPRequestHandler

from exceptions.api_errors import APIError
from handlers.file_handler import FileHandler
from mixins.json_sender import JsonSenderMixin
from mixins.route_parser import RouteParserMixin
from mixins.pagination import PaginationMixin
from mixins.sorter import SorterMixin
from settings.logging_config import get_logger


logger = get_logger(__name__)


class HTTPHandler(BaseHTTPRequestHandler, JsonSenderMixin, RouteParserMixin, PaginationMixin, SorterMixin):

    routes_get = {
        "/api/images/": "_handle_get_api_images",
        "/": "_handle_get_root",
    }

    routes_post = {
        "/api/upload/": "_handle_post_api_upload",
    }

    routes_delete = {
        "/api/images/<filename>": "_handle_delete_api_image",
    }


    def do_GET(self):
        """Handles GET requests and dispatches them based on route."""
        self.handle_request(self.routes_get)

    def do_POST(self):
        """Handles POST requests and dispatches them based on route."""
        self.handle_request(self.routes_post)

    def do_DELETE(self):
        """Handles DELETE requests and dispatches them based on route."""
        self.handle_request(self.routes_delete)


    def _handle_get_root(self):
        """Handles healthcheck at GET /."""
        logger.info("Healthcheck endpoint hit: /")
        self.send_json_response(200, {"message": "Welcome to the Upload Server"})


    def _handle_get_api_images(self):

        pagination_to_sql = self.get_limit_offset(self.route_query_params)
        limit = pagination_to_sql.get("limit")
        offset = pagination_to_sql.get("offset")

        sort_to_sql = self.get_sort_params(self.route_query_params)
        sort_param = sort_to_sql.get("sort_param")
        sort_value = sort_to_sql.get("sort_value")

        f_handler = FileHandler()
        try:
            images = f_handler.get_list_images(limit, offset, sort_param, sort_value)
        except Exception as e:
            logger.exception(f"Unexpected error to get list of images: {str(e)}")
            self.send_json_error(500, f"Internal server error: {str(e)}")
            return

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

        filename = self.route_params.get("filename", "")

        if not filename:
            self.send_json_error(400, "Filename not provided.")
            return

        f_handler = FileHandler()
        try:
            f_handler.delete_file(filename)
        except APIError as e:
            self.send_json_error(e.status_code, e.message)
            return
        except Exception as e:
            logger.exception(f"Unexpected error during file deletion: {str(e)}")
            self.send_json_error(500, f"Internal server error: {str(e)}")
            return

        self.send_json_response(200, {"message": f"File '{filename}' deleted successfully."})

