# PyMongoAggregate

version: "0.0.1"


example
```python
from re import compile as re_compile

from pymongo_aggregate.operations.stages.match import Match
from pymongo_aggregate.operations.stages.project import Project
from pymongo_aggregate.operations.stages.unwind import Unwind
from pymongo_aggregate.operations.operators.regex_find import RegexFind


pipeline = [
    Match({
        "experiment_name": "experiment2"
    }),
    Project({
        "proxy_id": 1,
        "input_text": 1,
        "capture_country": RegexFind(input_field="$output", pattern=re_compile(r"\*\*Country\*\*\n\s+-\s+(.*)\n"))
    }),
    Unwind(
        path="$capture_country.captures",
        include_array_index="country_index",
        preserve_null_and_empty_arrays=True
    ),
    Match({
        "country_index": 0
    }),
    Project({
        "_id": 0,
        "proxy_id": 1,
        "input_text": 1,
        "output_country": "$capture_country.captures"
    })
]
```