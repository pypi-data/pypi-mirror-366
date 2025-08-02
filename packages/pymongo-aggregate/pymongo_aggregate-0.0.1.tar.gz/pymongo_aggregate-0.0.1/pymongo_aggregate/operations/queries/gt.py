from pymongo_aggregate.operations.queries.query_operation import QueryOperation


class Gt(QueryOperation[int | float]):

    """$gt

    '$gt' selects those documents where the value of the specified field is grater than (i.e. >) the
    specified value.
    """

    operator = "$gt"
