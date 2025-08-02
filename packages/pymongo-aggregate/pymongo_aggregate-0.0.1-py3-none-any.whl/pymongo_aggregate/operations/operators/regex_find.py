from re import Pattern

from pymongo_aggregate.operations.operators.op_operation import OpOperation


class RegexFind(OpOperation[dict[str, str | Pattern]]):

    operator = "$regexFind"

    def __init__(self, input_field: str, pattern: Pattern):
        super().__init__({
            "input": input_field,
            "regex": pattern
        })
