from typing import Literal, Any

from pymongo_aggregate.operations.operators.op_operation import OpOperation
from pymongo_aggregate.operations.stages.stage_operation import StageOperation


type ProjectContentType = dict[str, str | Literal[1, 0] | OpOperation[Any]]


class Project(StageOperation[ProjectContentType]):

    """$project (aggregation)

    Passes along the documents with the requested fields to the next stages in the pipeline. The
    specified fields can be existing fields from the input documents or newly computed fields.
    """

    operator = "$project"
