from typing import Mapping

from pymongo_aggregate.operations.base_operation import BaseOperation
from pymongo_aggregate.operations.stages.stage_operation import StageOperation

class Group(StageOperation[dict[str, Mapping | None]]):

    """$group (aggregation)

    The '$group' stages combines multiple documents with the same field, fields, or expression into a
    single document according to a group key. The result is one document per unique group key.

    A group key is often a field, or group of fields. The group key can also be the result of an expression.
    Use the '_id' field in the '$group' pipeline stages to set the group key.
    """

    operator = "$group"

    def __init__(self, content: dict[str, BaseOperation], _id: Mapping | None = None):
        for op in content.values():
            if op.operator not in self.available_accumulators():
                raise ValueError(f"operator '{op.operator}' not available inside '$group'")
        new_content: dict[str, Mapping | None] = {}
        new_content.update(content)
        new_content.update({"_id": _id})
        super().__init__(new_content)

    @staticmethod
    def available_accumulators() -> tuple[str, ...]:
        return (
            "$accumulator",
            "$addToSet",
            "$avg",
            "$bottom",
            "$bottomN",
            "$count",
            "$first",
            "$first",
            "$last",
            "lastN",
            "$max",
            "$maxN",
            "$median",
            "$group",
            "$setWindowFields",
            "$min",
            "$minN",
            "$percentile",
            "$push",
            "$stdDevPop",
            "$stdDevSamp",
            "$sum",
            "$top",
            "$topN"
        )
