"""or operator module"""

from typing import Mapping, Any

from pymongo_aggregate.operations.base_operation import BaseOperation
from pymongo_aggregate.operations.queries.query_operation import QueryOperation


class Or(QueryOperation[list[BaseOperation | Mapping[str, Any]]]):

    """$or

    The '$or' operators performs a logical OR operators on an array of one or more <expressions> and
    selects the documents that satisfy at least one of the <expressions>
    """

    operator = "$or"
