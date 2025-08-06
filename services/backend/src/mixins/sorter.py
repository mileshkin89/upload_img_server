
from typing import Dict


class SorterMixin:
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


    def _parse_sort(self, query_params: Dict[str, str]):
        sort_param = query_params.get("sort_param", self.DEFAULT_SORT_PARAM)
        if sort_param not in self.AVAILABLE_SORT_PARAMS:
            raise ValueError(f"Invalid sort_param: {sort_param}")

        sort_value = query_params.get("sort_value", self.DEFAULT_SORT_VALUES)
        if sort_value not in self.AVAILABLE_SORT_VALUES:
            raise ValueError(f"Invalid sort_value: {sort_value}")

        self.sort_param = sort_param
        self.sort_value = sort_value


    def _sort_param_to_sql(self):
        return self.MATCHED_SQL_PARAMS[self.sort_param]


    def get_sort_params(self, query_params: Dict[str, str]) -> Dict[str, str]:
        try:
            self._parse_sort(query_params)
        except ValueError as e:
            raise ValueError(f"Invalid sort param or value: {str(e)}")

        return {
            "sort_param": self._sort_param_to_sql(),
            "sort_value": self.sort_value
        }

