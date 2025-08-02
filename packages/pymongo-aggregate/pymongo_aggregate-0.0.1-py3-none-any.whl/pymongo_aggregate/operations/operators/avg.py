"""avg operator module"""
from pymongo_aggregate.const import COMMON_STAGES
from pymongo_aggregate.operations.operators.op_operation import OpOperation

type AvgContentType = str | OpOperation


class Avg(OpOperation[AvgContentType]):

    """$avg (aggregation)

    Returns the average value of the numeric values. '$avg' ignores non-numeric values.
    """

    operator = "$avg"

    @staticmethod
    def stages_availability() -> tuple[str, ...]:
        """returns the available stages in which this operator can be defined"""
        return COMMON_STAGES
