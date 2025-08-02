from typing import Any

from pymongo_aggregate.operations.operators.op_operation import OpOperation


class Gt(OpOperation[list[str]]):

    """$gt (aggregation)

    Compares two values and returns:
        * true when the first value is greater than the second value.
        * false when the first value is less than or equal to the second value.
    The '$gt' compares both value and type, using the specified BSON comparison order for values of
    different types.
    """

    operator = "$gt"

    def __init__(self, val1: str, val2: Any):
        super().__init__([val1, val2])
