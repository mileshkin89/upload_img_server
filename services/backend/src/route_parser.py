
import re
from typing import Dict, Optional, Tuple
from abc import abstractmethod
from settings.logging_config import get_logger


logger = get_logger(__name__)


class RouteParserMixin:

    routes_get: Dict[str, str] = {}
    routes_post: Dict[str, str] = {}
    routes_delete: Dict[str, str] = {}
    routes_put: Dict[str, str] = {}

    path: Optional[str] = None
    route_params: Dict[str, str] = {}
    route_query_params: Dict[str, str] = {}


    @abstractmethod
    def send_json_error(self, status_code: int, message: str) -> None:
        pass


    def _route_to_regex(self, route: str) -> Tuple[re.Pattern, list]:
        """Convert route pattern to regex pattern.

        Args:
            route (str): Route pattern like '/upload/<filename>' or '/api/<path>/<id>'

        Returns:
            Tuple[re.Pattern, list]: Compiled regex pattern and list of parameter names
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
        """Extracts query parameters from the request path.

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
        """Match request path to a route and extract path/query parameters.

        Args:
            full_path (str): Full request path, e.g. '/api/images/123.jpg?page=2'
            routes (Dict[str, str]): Map of route patterns to handler names

        Returns:
            Optional[str]: Handler method name or None if no match
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


