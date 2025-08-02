from abc import ABC

from pymongo_aggregate.operations.base_operation import BaseOperation


class StageOperation[T](BaseOperation[T], ABC):

    typology = "stages"

    def __init__(self, content: T):
        super().__init__(content)
