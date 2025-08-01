from dataclasses import dataclass
from typing import Dict, List, Optional

from typing_extensions import Self


@dataclass
class JiraFieldType:
    type_: Optional[str]
    name: Optional[str]
    is_basic: Optional[bool]
    array_item_type: Optional[str]
    properties: List[Self]

    def __post_init__(self):
        if self.properties is None:
            self.properties = []


@dataclass
class JiraFieldPropertyPath:
    path: str
    is_array: bool


@dataclass
class JiraFieldSchema:
    type: str
    items: Optional[str] = None
    system: Optional[str] = None
    custom: Optional[str] = None
    custom_id: Optional[str] = None


@dataclass
class JiraField:
    id: str
    key: str
    name: str
    custom: bool
    orderable: bool
    searchable: bool
    clause_names: List[str]
    schema: Optional[JiraFieldSchema]


@dataclass
class JiraProjectCategory:
    id: str
    name: str
    description: str


@dataclass
class JiraProject:
    id: str
    name: str
    key: str
    type: str
    is_private: bool
    category: JiraProjectCategory


@dataclass
class JiraIssueType:
    id: str
    name: str
    description: str
    subtask: bool
    hierarchy_level: int
    project_id: str


@dataclass
class JiraProjectDetail:
    id: str
    key: str
    description: str
    issue_types: List[JiraIssueType]
    assignee_type: str
    name: str
    is_private: bool
    type: str


@dataclass
class JiraProjectField:
    required: bool
    name: str
    has_default_value: bool
    allowed_values: Dict[str, str]
    field_id: str
    key: str
    schema: Optional[JiraFieldSchema]

    def __post_init__(self):
        if self.allowed_values is None:
            self.allowed_values = {}

    def is_array(self) -> bool:
        return self.schema.type == "array" if self.schema else False

    def is_value_allowed(self, value: Optional[str]) -> bool:
        if value not in self.allowed_values.values():
            return False
        return True


@dataclass
class MySelfInfo:
    email_address: str
    display_name: str
    locale: str
    account_type: str
    expand: str
