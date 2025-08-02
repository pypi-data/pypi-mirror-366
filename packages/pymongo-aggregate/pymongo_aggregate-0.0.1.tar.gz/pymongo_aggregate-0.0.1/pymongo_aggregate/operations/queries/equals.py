from typing import Any

from pymongo_aggregate.operations.queries.query_operation import QueryOperation


class Equals(QueryOperation[Any]):

    operator = "$eq"
