from datetime import datetime
from typing import List, Optional

from jira_cloud_api.jira_models import (
    JiraField,
    JiraIssueType,
    JiraProject,
    JiraProjectDetail,
    JiraProjectField,
)


class BaseResponse:
    status_code: int
    status_reason: Optional[str]
    error_text: Optional[str]


class CreateIssueResponse(BaseResponse):
    id: str
    key: str
    link: str


class GetServerInfoResponse(BaseResponse):
    base_url: str
    version: str
    deployment_type: str
    server_time_zone: str
    server_time: Optional[datetime]


class GetMySelfResponse(BaseResponse):
    account_id: str
    account_type: str
    email_address: str
    display_name: str
    time_zone: str


class GetIssueResponse(BaseResponse):
    id: str
    key: str
    link: str
    fields: dict


class GetProjectsResponse(BaseResponse):
    projects: List[JiraProject]


class GetProjectDetailResponse(BaseResponse):
    project: Optional[JiraProjectDetail]


class GetProjectIssueTypesResponse(BaseResponse):
    issue_types: List[JiraIssueType]
    total: int
    max_results: int


class GetFieldsResponse(BaseResponse):
    fields: List[JiraField]


class GetProjectIssueFieldsResponse(BaseResponse):
    fields: List[JiraProjectField]
    total: int
    max_results: int
