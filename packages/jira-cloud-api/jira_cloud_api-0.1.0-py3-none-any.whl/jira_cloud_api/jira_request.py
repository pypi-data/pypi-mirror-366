from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class CreateIssueRequest:
    fields: Dict[str, Any]

    def __post_init__(self):
        issue_fields: Dict[str, Any] = {}
        for key, value in self.fields.items():
            field_paths = key.split(".")
            tmp = issue_fields
            is_array = isinstance(value, list)
            for count, field_path in enumerate(field_paths):
                # if this value is an array and at least has 2 levels
                # then the last property will be an array.
                if is_array and count == len(field_paths) - 2:
                    tmp[field_path] = [
                        {field_paths[len(field_paths) - 1]: v} for v in value
                    ]
                    break
                if count == len(field_paths) - 1:
                    tmp[field_path] = value
                else:
                    if tmp.get(field_path, None) is not None:
                        # merge exist dict keys.
                        tmp[field_path] = {**{}, **tmp[field_path]}
                    else:
                        tmp[field_path] = {}
                tmp = tmp[field_path]
        self.fields = issue_fields


@dataclass
class GetProjectIssueTypesRequest:
    project_id_or_key: str
    start_at: int = 0
    max_results: int = 50
    query_all: bool = False


@dataclass
class GetProjectIssueFieldsRequest:
    project_id_or_key: str
    issue_type_id: str
    start_at: int = 0
    max_results: int = 50
    query_all: bool = False
