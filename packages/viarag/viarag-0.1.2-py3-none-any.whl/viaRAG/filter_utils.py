# filter_utils.py

from typing import Dict, Any, List


class MetadataFilterBuilder:
    def __init__(self):
        self.filters: List[Dict[str, Any]] = []

    def eq(self, **kwargs):
        for key, val in kwargs.items():
            self.filters.append({"key": key, "op": "=", "value": val})
        return self

    def ne(self, **kwargs):
        for key, val in kwargs.items():
            self.filters.append({"key": key, "op": "!=", "value": val})
        return self

    def gt(self, **kwargs):
        for key, val in kwargs.items():
            self.filters.append({"key": key, "op": ">", "value": val})
        return self

    def gte(self, **kwargs):
        for key, val in kwargs.items():
            self.filters.append({"key": key, "op": ">=", "value": val})
        return self

    def lt(self, **kwargs):
        for key, val in kwargs.items():
            self.filters.append({"key": key, "op": "<", "value": val})
        return self

    def lte(self, **kwargs):
        for key, val in kwargs.items():
            self.filters.append({"key": key, "op": "<=", "value": val})
        return self

    def build(self) -> List[Dict[str, Any]]:
        return self.filters
