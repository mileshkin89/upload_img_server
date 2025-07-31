
from typing import Dict, Optional
from exceptions.pagination_errors import InvalidPageNumberError, InvalidPerPageError, NotAvailablePerPageError, PaginationError


class PaginationMixin:
    page: int
    per_page: int

    AVAILABLE_PER_PAGE: set[int] = {4, 8, 12}
    DEFAULT_PAGE: int = 1
    DEFAULT_PER_PAGE: int = 4
    MAX_PER_PAGE: Optional[int] = 20


    def _parse_pagination(self, query_params: Dict[str, str]):
        """Parse and validate pagination parameters from query parameters.

        Args:
            query_params (Dict[str, str]): Dictionary of query parameters.
            default_page (int, optional): Default page number if not specified. Defaults to 1.
            default_per_page (int, optional): Default items per page if not specified. Defaults to 10.
            max_per_page (Optional[int], optional): Maximum allowed items per page. Defaults to None (no limit).

        Returns:
            PaginationDTO: Data transfer object with validated pagination parameters.

        Raises:
            InvalidPageNumberError: If page is not a positive integer.
            InvalidPerPageError: If per_page is not a positive integer or exceeds max_per_page.
        """
        page_str = query_params.get('page', str(self.DEFAULT_PAGE))
        try:
            page = int(page_str)
            if page <= 0:
                raise InvalidPageNumberError(page_str)
        except ValueError:
            raise InvalidPageNumberError(page_str)
        self.page = page

        per_page_str = query_params.get('per_page', str(self.DEFAULT_PER_PAGE))
        try:
            per_page = int(per_page_str)
            if per_page <= 0:
                raise InvalidPerPageError(per_page_str)
            if per_page not in self.AVAILABLE_PER_PAGE:
                raise NotAvailablePerPageError(per_page_str, self.AVAILABLE_PER_PAGE)
            if self.MAX_PER_PAGE is not None and per_page > self.MAX_PER_PAGE:
                per_page = self.MAX_PER_PAGE
        except ValueError:
            raise InvalidPerPageError(per_page_str)
        self.per_page = per_page


    def get_limit_offset(self, query_params: Dict[str, str]) -> Dict[str, int]:
        try:
            self._parse_pagination(query_params)
        except PaginationError:
            return {}

        return {
            "limit": self.per_page,
            "offset": (self.page - 1) * self.per_page
        }
