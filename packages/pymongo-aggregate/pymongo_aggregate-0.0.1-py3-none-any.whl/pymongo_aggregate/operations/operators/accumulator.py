"""accumulator operator module"""

from bson import Code

from pymongo_aggregate.operations.operators.op_operation import OpOperation
from pymongo_aggregate.utils.code_validator import CodeValidator

type AccumulatorContentType = dict[str, str | list[str]]


class Accumulator(OpOperation[AccumulatorContentType]):

    """$accumulator (aggregation)

    Defines a custom accumulator operators. Accumulators are operators maintaining their state (e.g.
    totals, maximums, minimums, and related data) as documents progress through the pipeline. Use
    the $accumulator operators to execute your own JavaScript functions to implement behavior not
    supported by the MongoDB Query Language. See also $function.
    """

    operator = "$accumulator"

    def __init__(self,
                 codes: tuple[str, str, str],
                 init_args: list[str] | None = None,
                 accumulate_args: list[str] | None = None,
                 finalize_code: str | None = None):
        init_code, accumulate_code, merge_code = codes
        CodeValidator.validate_js(init_code)
        CodeValidator.validate_js(accumulate_code)
        CodeValidator.validate_js(merge_code)
        content: AccumulatorContentType = {
            "init": Code(init_code),
            "accumulateCode": Code(accumulate_code),
            "mergeCode": Code(merge_code),
            "lang": "js"
        }

        if init_args:
            content.update({
                "initArgs": init_args
            })
        if accumulate_args:
            content.update({
                "accumulateArgs": accumulate_args
            })
        if finalize_code:
            content.update({
                "finalizeCode": Code(finalize_code)
            })

        super().__init__(content)
