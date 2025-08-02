from pymongo_aggregate.operations.operators.op_operation import OpOperation


class Multiply(OpOperation[list[str]]):

    operator = "$multiply"
