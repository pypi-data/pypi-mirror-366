from re import Pattern

from pymongo_aggregate.operations.operators.op_operation import OpOperation
from pymongo_aggregate.operations.stages.stage_operation import StageOperation

type MatchContentType = dict[str, int | str | Pattern | OpOperation]


class Match(StageOperation[MatchContentType]):

    """$match (aggregation)

    Filters documents based on a specified queries predicate. Matched documents are passed to the
    next pipeline stages.
    """

    operator = "$match"
