from typing import Literal

from bson import Code

from pymongo_aggregate.operations.operators.op_operation import OpOperation
from pymongo_aggregate.utils.code_validator import CodeValidator


class Function(OpOperation[dict[str, str | list[str]]]):

    """$function (aggregation)

    Defines a custom aggregation function or expression in JavaScript.

    You can use the '$function' operators to define custom functions to implement behavior not
    supported by the MongoDB Query Language. See also '$accumulator'.
    """

    operator = "$function"

    def __init__(self, code: str, args: list[str], lang: Literal["js"] = "js"):
        CodeValidator.validate_js(code)
        super().__init__({
            "body": Code(code),
            "args": args,
            "lang": lang
        })
