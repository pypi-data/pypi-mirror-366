"""operator module"""

from abc import ABC

from pymongo_aggregate.operations.base_operation import BaseOperation


class OpOperation[T](BaseOperation[T], ABC):

    """Operator base class"""

    typology = "operators"

    @staticmethod
    def is_aggregation() -> bool:
        """returns weather """
        return True
