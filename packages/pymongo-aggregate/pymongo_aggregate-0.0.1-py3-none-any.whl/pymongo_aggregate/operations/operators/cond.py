"""cond operator module"""

from typing import Any

from pymongo_aggregate.operations.operators.op_operation import OpOperation


class Cond(OpOperation[dict[str, Any]]):

    """$cond (aggregation)

    Evaluates a boolean expression to return one of the two specified return expressions.
    """

    operator = "$cond"

    def __init__(self, if_expr: OpOperation, then_case: Any, else_case: Any):
        content = {
            "if": if_expr,
            "then": then_case,
            "else": else_case
        }
        self._if = if_expr
        self._then = then_case
        self._else = else_case
        super().__init__(content)

    @property
    def if_expr(self) -> OpOperation:
        """public getter for 'if' field"""
        return self._if

    @property
    def then_case(self) -> Any:
        """public getter for 'then' field"""
        return self._then

    @property
    def else_case(self) -> Any:
        """public getter for 'else' field"""
        return self._else
