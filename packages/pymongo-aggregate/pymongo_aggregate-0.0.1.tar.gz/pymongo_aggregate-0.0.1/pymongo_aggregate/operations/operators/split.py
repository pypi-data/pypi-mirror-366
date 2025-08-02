"""split operator module"""

from pymongo_aggregate.operations.operators.op_operation import OpOperation

type SplitContentType = list[str]


class Split(OpOperation[SplitContentType]):

    """$split

    Divides a string into an array based on delimiter. '$split' removes the delimiter and
    returns the resulting elements of an array. If delimiter is not found in the string,
    '$split' returns the original string as the only element of an array.
    """

    operator = "$split"

    def __init__(self, field: str, delimiter: str):
        super().__init__([field, delimiter])
