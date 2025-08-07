"""
pagination.py

Provides a mixin class `PaginationMixin` that adds pagination parsing
and validation logic to HTTP handlers or data-processing classes.

Supports query parameters like `page` and `per_page`, validates them against
a predefined set of allowed values, and calculates `limit` and `offset` for pagination.

Pagination errors are raised from custom exception classes for consistent error handling.
"""
from typing import Dict, Optional
from exceptions.pagination_errors import InvalidPageNumberError, InvalidPerPageError, NotAvailablePerPageError, PaginationError


class PaginationMixin:
    """
    A reusable mixin that provides pagination support.

    This mixin can be inherited by classes handling HTTP query parameters
    to parse `page` and `per_page` values, validate them, and compute SQL-style
    pagination via `limit` and `offset`.

    Attributes:
        page (int): Parsed and validated page number.
        per_page (int): Parsed and validated number of items per page.
        AVAILABLE_PER_PAGE (set[int]): Allowed values for `per_page`.
        DEFAULT_PAGE (int): Default page number used if not provided.
        DEFAULT_PER_PAGE (int): Default items per page used if not provided.
        MAX_PER_PAGE (Optional[int]): Optional limit to enforce a maximum per_page.
    """
    page: int
    per_page: int

    AVAILABLE_PER_PAGE: set[int] = {4, 8, 12}
    DEFAULT_PAGE: int = 1
    DEFAULT_PER_PAGE: int = 8
    MAX_PER_PAGE: Optional[int] = 20


    def _parse_pagination(self, query_params: Dict[str, str]):
        """
        Parse and validate pagination parameters from the query string.

        Args:
            query_params (Dict[str, str]): Dictionary of query parameters.

        Raises:
            InvalidPageNumberError: If 'page' is not a valid positive integer.
            InvalidPerPageError: If 'per_page' is invalid or negative.
            NotAvailablePerPageError: If 'per_page' is not in the allowed set.
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
        """
        Returns pagination parameters as `limit` and `offset` for querying.

        Args:
            query_params (Dict[str, str]): Dictionary containing `page` and `per_page`.

        Returns:
            Dict[str, int]: A dictionary with `limit` and `offset` keys.
                            Returns an empty dict if pagination is invalid.
        """
        try:
            self._parse_pagination(query_params)
        except PaginationError:
            return {}

        return {
            "limit": self.per_page,
            "offset": (self.page - 1) * self.per_page
        }
