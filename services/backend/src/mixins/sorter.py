"""
sorter.py

Provides the `SorterMixin`, a reusable mixin class that adds sorting logic
based on query parameters.

It allows:
- Validating and parsing `sort_param` and `sort_value` from query strings.
- Mapping logical sort parameters (e.g., "sort_age") to actual SQL column names.
"""
from typing import Dict


class SorterMixin:
    """
    Mixin that enables parsing and validating sorting parameters from query strings.

    Supports:
    - Safe parsing of sort field and direction
    - Mapping logical parameters to SQL column names

    Attributes:
        sort_param (str): Current logical sort parameter (e.g., "sort_age").
        sort_value (str): Current sort direction (e.g., "asc" or "desc").

        DEFAULT_SORT_PARAM (str): Default sort parameter if not provided.
        AVAILABLE_SORT_PARAMS (set): Set of allowed sort parameter keys.
        DEFAULT_SORT_VALUES (str): Default sort direction if not provided.
        AVAILABLE_SORT_VALUES (set): Set of allowed sort directions.
        MATCHED_SQL_PARAMS (dict): Mapping from logical sort parameters to SQL column names.
    """
    sort_param: str
    sort_value: str

    DEFAULT_SORT_PARAM: str = "sort_age"
    AVAILABLE_SORT_PARAMS: set[str] = {"sort_age", "sort_size", "sort_name"}

    DEFAULT_SORT_VALUES: str = "desc"
    AVAILABLE_SORT_VALUES: set[str] = {"asc", "desc"}

    MATCHED_SQL_PARAMS: dict = {
        "sort_age": "upload_time",
        "sort_size": "size",
        "sort_name": "original_name",
    }

    def _parse_sort(self, query_params: Dict[str, str]) -> None:
        """
        Parse and validate sorting parameters from query string.

        Args:
            query_params (Dict[str, str]): Dictionary of query parameters.

        Raises:
            ValueError: If `sort_param` or `sort_value` is invalid.
        """
        sort_param = query_params.get("sort_param", self.DEFAULT_SORT_PARAM)
        if sort_param not in self.AVAILABLE_SORT_PARAMS:
            raise ValueError(f"Invalid sort_param: {sort_param}")

        sort_value = query_params.get("sort_value", self.DEFAULT_SORT_VALUES)
        if sort_value not in self.AVAILABLE_SORT_VALUES:
            raise ValueError(f"Invalid sort_value: {sort_value}")

        self.sort_param = sort_param
        self.sort_value = sort_value


    def _sort_param_to_sql(self) -> str:
        """
        Translate the logical sort parameter to its SQL column name.

        Returns:
            str: SQL column name corresponding to the selected `sort_param`.
        """
        return self.MATCHED_SQL_PARAMS[self.sort_param]


    def get_sort_params(self, query_params: Dict[str, str]) -> Dict[str, str]:
        """
        Parse and return validated sort parameters as a dictionary suitable for SQL query usage.

        Args:
            query_params (Dict[str, str]): Dictionary of query parameters.

        Returns:
            Dict[str, str]: Dictionary with keys `sort_param` and `sort_value`.

        Raises:
            ValueError: If either the sort parameter or sort value is invalid.
        """
        try:
            self._parse_sort(query_params)
        except ValueError as e:
            raise ValueError(f"Invalid sort param or value: {str(e)}")

        return {
            "sort_param": self._sort_param_to_sql(),
            "sort_value": self.sort_value
        }

