from dataclasses import dataclass
from typing import Any, Dict, Optional

from dateparser import parse as date_parse
from requests import request as http_request
from requests.auth import HTTPBasicAuth

from jira_cloud_api.jira_models import (
    JiraField,
    JiraFieldSchema,
    JiraIssueType,
    JiraProject,
    JiraProjectCategory,
    JiraProjectDetail,
    JiraProjectField,
)
from jira_cloud_api.jira_request import (
    CreateIssueRequest,
    GetProjectIssueFieldsRequest,
    GetProjectIssueTypesRequest,
)
from jira_cloud_api.jira_response import (
    CreateIssueResponse,
    GetFieldsResponse,
    GetMySelfResponse,
    GetProjectDetailResponse,
    GetProjectIssueFieldsResponse,
    GetProjectIssueTypesResponse,
    GetProjectsResponse,
    GetServerInfoResponse,
)

_DEFAULT_JIRA_TIMEOUT = 60.0


@dataclass
class JiraApiRequest:
    url: str
    params: Optional[Dict[str, Any]] = None
    body: Optional[Any] = None


class JiraApiResponse:
    status_code: int
    content: Any
    status_reason: Optional[str] = None
    error_text: Optional[str] = None

    def is_success_response(self) -> bool:
        return self.status_code >= 200 and self.status_code <= 299


@dataclass
class JiraApiOptions:
    url: str
    access_token: str
    user_email: Optional[str] = None
    timeout: Optional[float] = _DEFAULT_JIRA_TIMEOUT
    ssl_verify: bool = False


class JiraApi:
    default_request_headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "Media-Type": "application/json",
        "X-Atlassian-Token": "no-check",
    }

    def __init__(
        self,
        options: JiraApiOptions,
    ) -> None:
        self.__is_jira_cloud = self.__is_jira_cloud_url(options.url)
        self.__options = options

        if self.__is_jira_cloud:
            if not options.user_email:
                raise ValueError("User email must be provided for Jira Cloud API.")
        else:
            self.default_request_headers["Authorization"] = (
                f"Bearer {options.access_token}"
            )

    @staticmethod
    def __is_jira_cloud_url(jira_url: Optional[str]) -> bool:
        if jira_url is not None and "atlassian.net".upper() in jira_url.upper():
            return True
        return False

    def __call_post_api(self, request: JiraApiRequest) -> JiraApiResponse:
        api_response = JiraApiResponse()

        try:
            response = http_request(
                method="POST",
                url=request.url,
                params=request.params,
                json=request.body if request.body else {},
                auth=(
                    HTTPBasicAuth(
                        self.__options.user_email, self.__options.access_token
                    )
                    if self.__is_jira_cloud and self.__options.user_email
                    else None
                ),
                timeout=self.__options.timeout,
                verify=self.__options.ssl_verify,
            )

            api_response.status_code = response.status_code
            api_response.status_reason = response.reason
            api_response.content = (
                response.json() if response.status_code == 200 else {}
            )
            api_response.error_text = (
                response.text if hasattr(response, "text") else None
            )
        except Exception as e:
            api_response.error_text = (
                str(e) if api_response.error_text is None else api_response.error_text
            )
        finally:
            if response:
                response.close()
        return api_response

    def __call_get_api(self, request: JiraApiRequest) -> JiraApiResponse:
        api_response = JiraApiResponse()

        try:
            response = http_request(
                method="GET",
                url=request.url,
                params=request.params,
                auth=(
                    HTTPBasicAuth(
                        self.__options.user_email, self.__options.access_token
                    )
                    if self.__is_jira_cloud and self.__options.user_email
                    else None
                ),
                timeout=self.__options.timeout,
                verify=self.__options.ssl_verify,
            )

            api_response.status_code = response.status_code
            api_response.status_reason = response.reason
            api_response.content = (
                response.json() if response.status_code == 200 else {}
            )
            api_response.error_text = (
                response.text
                if hasattr(response, "text") and response.status_code > 299
                else None
            )
        except Exception as e:
            api_response.error_text = (
                str(e) if api_response.error_text is None else api_response.error_text
            )
        finally:
            if response:
                response.close()
        return api_response

    def get_server_info(self) -> GetServerInfoResponse:
        raw_response = self.__call_get_api(
            JiraApiRequest(url=f"{self.__options.url}/rest/api/2/serverInfo")
        )

        response = GetServerInfoResponse()
        response.status_code = raw_response.status_code
        response.status_reason = raw_response.status_reason

        if raw_response.status_code != 200:
            response.error_text = raw_response.error_text
            return response

        response.status_code = raw_response.status_code
        response.base_url = str(raw_response.content.get("baseUrl", ""))
        response.version = str(raw_response.content.get("version", ""))
        response.deployment_type = str(raw_response.content.get("deploymentType", ""))
        response.server_time_zone = str(raw_response.content.get("serverTimeZone", ""))
        response.server_time = date_parse(raw_response.content.get("serverTime", ""))

        return response

    def get_jira_browser_link(self, key: str) -> "str":
        return f"{self.__options.url}/browse/{key}"

    def get_myself(self) -> GetMySelfResponse:
        raw_response = self.__call_get_api(
            JiraApiRequest(url=f"{self.__options.url}/rest/api/2/myself")
        )

        response = GetMySelfResponse()
        response.status_code = raw_response.status_code
        response.status_reason = raw_response.status_reason

        if not raw_response.is_success_response():
            response.error_text = raw_response.error_text
            return response

        response.account_id = str(raw_response.content.get("accountId", ""))
        response.account_type = str(raw_response.content.get("accountType", ""))
        response.email_address = str(raw_response.content.get("emailAddress", ""))
        response.display_name = str(raw_response.content.get("displayName", ""))
        response.time_zone = str(raw_response.content.get("timeZone", ""))

        return response

    def get_all_projects(self) -> GetProjectsResponse:
        raw_response = self.__call_get_api(
            JiraApiRequest(url=f"{self.__options.url}/rest/api/2/project")
        )

        response = GetProjectsResponse()
        response.status_code = raw_response.status_code
        response.status_reason = raw_response.status_reason

        if not raw_response.is_success_response():
            response.error_text = raw_response.error_text
            return response

        def __convert_to_project(raw_data: Dict[str, Any]) -> JiraProject:
            return JiraProject(
                id=str(raw_data.get("id", "")),
                name=str(raw_data.get("name", "")),
                key=str(raw_data.get("key", "")),
                type=str(raw_data.get("projectTypeKey", "")),
                is_private=raw_data.get("isPrivate", False),
                category=JiraProjectCategory(
                    id=str(raw_data.get("projectCategory", {}).get("id", "")),
                    name=str(raw_data.get("projectCategory", {}).get("name", "")),
                    description=str(
                        raw_data.get("projectCategory", {}).get("description", "")
                    ),
                ),
            )

        response.projects = [
            __convert_to_project(project) for project in raw_response.content
        ]

        return response

    def get_project_detail(self, project_id_or_key: str) -> GetProjectDetailResponse:
        raw_response = self.__call_get_api(
            JiraApiRequest(
                url=f"{self.__options.url}/rest/api/2/project/{project_id_or_key}"
            )
        )

        response = GetProjectDetailResponse()
        response.status_code = raw_response.status_code
        response.status_reason = raw_response.status_reason

        if not raw_response.is_success_response():
            response.error_text = raw_response.error_text
            return response

        response.project = JiraProjectDetail(
            id=str(raw_response.content.get("id", "")),
            key=str(raw_response.content.get("key", "")),
            description=str(raw_response.content.get("description", "")),
            issue_types=[
                JiraIssueType(
                    id=str(issue_type.get("id", "")),
                    name=str(issue_type.get("name", "")),
                    description=str(issue_type.get("description", "")),
                    subtask=issue_type.get("subtask", False),
                    hierarchy_level=issue_type.get("hierarchyLevel", 0),
                    project_id=str(raw_response.content.get("id", "")),
                )
                for issue_type in raw_response.content.get("issueTypes", [])
            ],
            assignee_type=str(raw_response.content.get("assigneeType", "")),
            name=str(raw_response.content.get("name", "")),
            is_private=raw_response.content.get("isPrivate", False),
            type=str(raw_response.content.get("projectTypeKey", "")),
        )

        return response

    def get_project_issue_types(
        self, request: GetProjectIssueTypesRequest
    ) -> GetProjectIssueTypesResponse:
        raw_request = JiraApiRequest(
            url=f"{self.__options.url}/rest/api/2/issue/createmeta/{request.project_id_or_key}/issuetypes",  # pylint: disable=line-too-long
            params={
                "startAt": request.start_at,
                "maxResults": request.max_results,
            },
        )

        raw_response = self.__call_get_api(raw_request)

        response = GetProjectIssueTypesResponse()
        response.status_code = raw_response.status_code
        response.status_reason = raw_response.status_reason
        response.total = raw_response.content.get("total", 0)
        response.max_results = raw_response.content.get("maxResults", 50)

        if not raw_response.is_success_response():
            response.error_text = raw_response.error_text
            return response

        def __convert_to_issue_type(raw_data: Dict[str, Any]) -> JiraIssueType:
            return JiraIssueType(
                id=str(raw_data.get("id", "")),
                name=str(raw_data.get("name", "")),
                description=str(raw_data.get("description", "")),
                subtask=raw_data.get("subtask", False),
                hierarchy_level=raw_data.get("hierarchyLevel", 0),
                project_id=request.project_id_or_key,
            )

        response.issue_types = [
            __convert_to_issue_type(issue_type)
            for issue_type in raw_response.content.get("issueTypes", [])
        ]

        if (
            request.query_all
            and request.start_at + request.max_results < response.total
        ):
            request.start_at += request.max_results

            next_response = self.get_project_issue_types(request)

            response.issue_types = response.issue_types + (
                next_response.issue_types if next_response.status_code == 200 else []
            )

        return response

    def get_all_fields(self) -> GetFieldsResponse:
        raw_response = self.__call_get_api(
            JiraApiRequest(url=f"{self.__options.url}/rest/api/2/field")
        )

        response = GetFieldsResponse()
        response.status_code = raw_response.status_code
        response.status_reason = raw_response.status_reason
        response.error_text = raw_response.error_text

        if not raw_response.is_success_response():
            response.error_text = raw_response.error_text
            return response

        response.fields = [
            JiraField(
                id=str(field.get("id", "")),
                key=str(field.get("key", "")),
                name=str(field.get("name", "")),
                custom=field.get("custom", False),
                orderable=field.get("orderable", False),
                searchable=field.get("searchable", False),
                clause_names=field.get("clauseNames", []),
                schema=(
                    JiraFieldSchema(
                        type=str(field.get("schema", {}).get("type", "")),
                        items=str(field.get("schema", {}).get("items", "")),
                        system=str(field.get("schema", {}).get("system", "")),
                        custom=str(field.get("schema", {}).get("custom", "")),
                        custom_id=str(field.get("schema", {}).get("customId", "")),
                    )
                    if field.get("schema", None)
                    else None
                ),
            )
            for field in raw_response.content
        ]

        return response

    def get_project_issue_fields(
        self, request: GetProjectIssueFieldsRequest
    ) -> GetProjectIssueFieldsResponse:
        raw_request = JiraApiRequest(
            url=f"{self.__options.url}/rest/api/2/issue/createmeta/{request.project_id_or_key}/issuetypes/{request.issue_type_id}",  # pylint: disable=line-too-long
            params={
                "startAt": request.start_at,
                "maxResults": request.max_results,
            },
        )

        raw_response = self.__call_get_api(raw_request)

        response = GetProjectIssueFieldsResponse()
        response.status_code = raw_response.status_code
        response.status_reason = raw_response.status_reason
        response.error_text = raw_response.error_text
        response.total = raw_response.content.get("total", 0)
        response.max_results = raw_response.content.get("maxResults", 50)

        if not raw_response.is_success_response():
            response.error_text = raw_response.error_text
            return response

        def __convert_to_allowed_values(raw_data: Optional[Any]) -> Dict[str, str]:
            if (raw_data is None) or not isinstance(raw_data, list):
                return {}

            allowed_values = {}
            i = 0
            for item in raw_data:
                allowed_values.update(
                    {f"{key}_{i}": str(value) for key, value in item.items()}
                )
                i += 1

            return allowed_values

        def __convert_to_jira_project_field(
            raw_data: Dict[str, Any],
        ) -> JiraProjectField:
            return JiraProjectField(
                required=raw_data.get("required", False),
                name=str(raw_data.get("name", "")),
                has_default_value=raw_data.get("hasDefaultValue", False),
                allowed_values=(
                    __convert_to_allowed_values(raw_data.get("allowedValues", []))
                    if raw_data.get("allowedValues", None)
                    else {}
                ),
                field_id=str(raw_data.get("fieldId", "")),
                key=str(raw_data.get("key", "")),
                schema=(
                    JiraFieldSchema(
                        type=str(raw_data.get("schema", {}).get("type", "")),
                        items=str(raw_data.get("schema", {}).get("items", "")),
                        system=str(raw_data.get("schema", {}).get("system", "")),
                        custom=str(raw_data.get("schema", {}).get("custom", "")),
                        custom_id=str(raw_data.get("schema", {}).get("customId", "")),
                    )
                    if raw_data.get("schema", None)
                    else None
                ),
            )

        response.fields = [
            __convert_to_jira_project_field(issue_type)
            for issue_type in raw_response.content.get("fields", [])
        ]

        if (
            request.query_all
            and request.start_at + request.max_results < response.total
        ):
            request.start_at += request.max_results

            next_response = self.get_project_issue_fields(request)

            response.fields = response.fields + (
                next_response.fields if next_response.status_code == 200 else []
            )

        return response

    def create_issue(self, request: CreateIssueRequest) -> CreateIssueResponse:
        raw_response = self.__call_post_api(
            JiraApiRequest(
                url=f"{self.__options.url}/rest/api/2/issue",
                body={"fields": request.fields},
            )
        )

        response = CreateIssueResponse()
        response.status_code = raw_response.status_code
        response.status_reason = raw_response.status_reason
        response.error_text = raw_response.error_text

        if not raw_response.is_success_response():
            response.error_text = raw_response.error_text
            return response

        response.id = raw_response.content.get("id", "")
        response.key = raw_response.content.get("key", "")
        response.link = raw_response.content.get("self", "")

        return response
