"""
route_parser.py

Provides the `RouteParserMixin`, a reusable mixin class for HTTP request routing.

It supports:
- Matching static and parameterized routes (e.g., `/api/image/<filename>`)
- Extracting route parameters and query parameters from request paths
- Dispatching requests to corresponding handler methods
- Basic error handling via abstract `send_json_error()`

Intended to be used in HTTP handlers (e.g., subclasses of `BaseHTTPRequestHandler`).
"""
import re
from typing import Dict, Optional, Tuple
from abc import abstractmethod
from settings.logging_config import get_logger


logger = get_logger(__name__)


class RouteParserMixin:
    """
    A mixin that enables HTTP-style routing for classes with a `path` attribute.

    It supports:
    - Static and dynamic route pattern matching
    - Extraction of path parameters and query parameters
    - Dispatching to handler methods dynamically

    Attributes:
        routes_get (Dict[str, str]): Mapping of GET routes to handler method names.
        routes_post (Dict[str, str]): Mapping of POST routes to handler method names.
        routes_delete (Dict[str, str]): Mapping of DELETE routes to handler method names.
        routes_put (Dict[str, str]): Mapping of PUT routes to handler method names.
        path (Optional[str]): The raw request path, including query string.
        route_params (Dict[str, str]): Extracted path parameters (e.g., {"filename": "test.png"}).
        route_query_params (Dict[str, str]): Extracted query parameters (e.g., {"page": "1"}).
    """
    routes_get: Dict[str, str] = {}
    routes_post: Dict[str, str] = {}
    routes_delete: Dict[str, str] = {}
    routes_put: Dict[str, str] = {}

    path: Optional[str] = None
    route_params: Dict[str, str] = {}
    route_query_params: Dict[str, str] = {}


    @abstractmethod
    def send_json_error(self, status_code: int, message: str) -> None:
        """
        Abstract method to send a JSON-formatted error response.

        Args:
            status_code (int): HTTP status code.
            message (str): Error message.
        """
        pass


    def _route_to_regex(self, route: str) -> Tuple[re.Pattern, list]:
        """
        Convert a route string with parameter placeholders into a compiled regex.

        Args:
            route (str): A route pattern like '/api/<entity>/<id>'.

        Returns:
            Tuple[re.Pattern, list]: A compiled regex and a list of parameter names.
        """
        param_names = []
        regex_pattern = route

        import re as regex_module
        param_pattern = r'<([^>]+)>'

        for match in regex_module.finditer(param_pattern, route):
            param_name = match.group(1)
            param_names.append(param_name)
            regex_pattern = regex_pattern.replace(f'<{param_name}>', '([^/]+)')

        regex_pattern = f'^{regex_pattern}$'

        compiled_pattern = regex_module.compile(regex_pattern)
        return compiled_pattern, param_names


    def _parse_query_params(self) -> Dict[str, str]:
        """
        Parse and return query parameters from the request path.

        Returns:
            Dict[str, str]: Dictionary of query parameters.
        """
        if self.path is None:
            return {}

        query_params = {}
        if '?' in self.path:
            _, query_string = self.path.split('?', 1)
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    query_params[key] = value

        return query_params


    def _match_route(self, full_path: str, routes: Dict[str, str]) -> Optional[str]:
        """
        Match the request path against a routing table and extract parameters.

        Args:
            full_path (str): The full request path (may include query string).
            routes (Dict[str, str]): Mapping of route patterns to handler method names.

        Returns:
            Optional[str]: The name of the matched handler method, or None.
        """
        self.route_params = {}
        self.route_query_params = {}

        if '?' in full_path:
            path, _ = full_path.split('?', 1)
            self.route_query_params = self._parse_query_params()
        else:
            path = full_path

        if path in routes:
            return routes[path]

        # Template with parameters, for example /api/images/<filename>
        for route_pattern, handler_name in routes.items():
            if '<' in route_pattern:
                regex_pattern, param_names = self._route_to_regex(route_pattern)
                match = regex_pattern.match(path)
                if match:
                    self.route_params = {
                        param_names[i]: match.group(i + 1)
                        for i in range(len(param_names))
                    }
                    return handler_name

        # Prefix match (eg: /api/images/abc.jpg → /api/images/)
        for route_prefix, handler_name in routes.items():
            if '<' not in route_prefix and path.startswith(route_prefix):
                return handler_name

        return None


    def handle_request(self, routes: dict[str, str]) -> None:
        """
        Resolve and invoke the handler function for the current path.

        This method:
        - Validates presence of `self.path`
        - Matches the path to the routing table
        - Calls the appropriate handler if found
        - Sends JSON errors for unmatched or missing handlers

        Args:
            routes (dict[str, str]): Dictionary of route patterns mapped to handler names.
        """
        if self.path is None:
            self.send_json_error(500, "Path not available")
            return

        handler_name = self._match_route(self.path, routes)

        if not handler_name:
            self.send_json_error(404, "Not Found")
            return

        handler = getattr(self, handler_name, None)

        if not handler:
            self.send_json_error(500, "Handler not implemented.")
            return

        handler()


