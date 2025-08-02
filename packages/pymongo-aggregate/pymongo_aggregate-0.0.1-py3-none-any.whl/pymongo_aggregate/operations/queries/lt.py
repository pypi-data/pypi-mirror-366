from pymongo_aggregate.operations.queries.query_operation import QueryOperation


class Lt(QueryOperation[int | float]):

    """$lt


    """

    operator = "$lt"