from pymongo_aggregate.operations.stages.stage_operation import StageOperation


class Count(StageOperation[str]):

    """$count (aggregation)

    Passes a document to the next stages that contains a count of the number of documents into to
    the stages.
    """

    operator = "$count"
