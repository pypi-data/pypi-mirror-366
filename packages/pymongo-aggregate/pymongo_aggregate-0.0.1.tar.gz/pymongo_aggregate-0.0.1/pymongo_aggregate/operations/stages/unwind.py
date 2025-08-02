from pymongo_aggregate.operations.stages.stage_operation import StageOperation


type UnwindContentType = dict[str, str | bool]


class Unwind(StageOperation[UnwindContentType]):

    """$unwind

    Deconstructs an array field from the input documents to output a document for each element.
    Each output document is the input document with the value of the array field replace by the
    element.
    """

    operator = "$unwind"

    def __init__(self, path: str,
                 include_array_index: str | None = None,
                 preserve_null_and_empty_arrays: bool | None = None):
        content: UnwindContentType = {"path": path}
        if include_array_index:
            content.update({"includeArrayIndex": include_array_index})
        if preserve_null_and_empty_arrays:
            content.update({"preserveNullAndEmptyArrays": preserve_null_and_empty_arrays})
        super().__init__(content)
