from abc import ABC

from pymongo_aggregate.operations.base_operation import BaseOperation


class QueryOperation[T](BaseOperation[T], ABC):

    typology = "queries"

    def __init__(self, content: T):
        super().__init__(content)
