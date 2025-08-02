from typing import Final

COMMON_STAGES: Final[tuple[str, ...]] = (
            "$addFields",
            "$bucket",
            "$bucketAuto",
            "$group",
            "$match",
            "$project",
            "$replaceRoot",
            "$replaceWith",
            "$set",
            "$setWindowFields"
        )
